// Package db gère la connexion PostgreSQL et les opérations de chargement
// en masse utilisées par l'importeur.
package db

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Row représente une ligne à insérer dans la table de staging.
type Row struct {
	Prefix string
	Suffix string
}

// rowSource implémente pgx.CopyFromSource pour streamer des lignes
// directement au protocole COPY, sans buffer intermédiaire côté SQL.
type rowSource struct {
	rows []Row
	pos  int
}

func (s *rowSource) Next() bool {
	s.pos++
	return s.pos <= len(s.rows)
}

func (s *rowSource) Values() ([]any, error) {
	r := s.rows[s.pos-1]
	return []any{r.Prefix, r.Suffix}, nil
}

func (s *rowSource) Err() error { return nil }

// Connect ouvre un pool de connexions PostgreSQL.
func Connect(ctx context.Context, dsn string, poolSize int32) (*pgxpool.Pool, error) {
	cfg, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		return nil, fmt.Errorf("parse dsn: %w", err)
	}
	cfg.MaxConns = poolSize
	cfg.MaxConnLifetime = time.Hour

	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("connect: %w", err)
	}
	if err := pool.Ping(ctx); err != nil {
		return nil, fmt.Errorf("ping: %w", err)
	}
	return pool, nil
}

// EnsureTargetEmpty vérifie que la table finale breached_passwords est vide
// avant de lancer un import.
func EnsureTargetEmpty(ctx context.Context, pool *pgxpool.Pool) error {
	var isEmpty bool
	if err := pool.QueryRow(ctx, `SELECT NOT EXISTS (SELECT 1 FROM breached_passwords)`).Scan(&isEmpty); err != nil {
		return fmt.Errorf("check target table: %w", err)
	}
	if !isEmpty {
		return fmt.Errorf("la table breached_passwords contient déjà des données : import annulé")
	}
	return nil
}

// PrepareStaging crée une table de staging non journalisée (UNLOGGED) et
// sans index, ce qui rend le COPY massivement plus rapide (pas de
// maintenance d'index ni de WAL par ligne).
func PrepareStaging(ctx context.Context, pool *pgxpool.Pool) error {
	_, err := pool.Exec(ctx, `
		DROP TABLE IF EXISTS staging_passwords;
		CREATE UNLOGGED TABLE staging_passwords (
			hash_prefix CHAR(5) NOT NULL,
			hash_suffix VARCHAR(35) NOT NULL
		);
	`)
	return err
}

// CopyBatch insère un lot de lignes via le protocole COPY (bulk load natif
// PostgreSQL), nettement plus rapide que des INSERT unitaires ou multi-valeurs.
func CopyBatch(ctx context.Context, pool *pgxpool.Pool, rows []Row) (int64, error) {
	if len(rows) == 0 {
		return 0, nil
	}
	n, err := pool.CopyFrom(
		ctx,
		pgx.Identifier{"staging_passwords"},
		[]string{"hash_prefix", "hash_suffix"},
		&rowSource{rows: rows},
	)
	return n, err
}

// FinalizeImport agrège la table de staging (déduplication + comptage des
// occurrences) dans la table finale indexée `breached_passwords`.
func FinalizeImport(ctx context.Context, pool *pgxpool.Pool) error {
	start := time.Now()

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return fmt.Errorf("acquire connection: %w", err)
	}
	defer conn.Release()

	// Réglages mémoire et de parallélisme portés uniquement par cette
	// session (le temps de la connexion), sans toucher à la configuration
	// globale du serveur utilisée par le reste de l'application.
	if _, err := conn.Exec(ctx, `
		SET work_mem = '512MB';
		SET maintenance_work_mem = '512MB';
		SET max_parallel_maintenance_workers = 6;
		SET max_parallel_workers_per_gather = 6;
	`); err != nil {
		return fmt.Errorf("tune session: %w", err)
	}

	log.Println("Insertion en masse sans index, puis reconstruction de l'index...")
	if err := finalizeIntoEmptyTable(ctx, conn); err != nil {
		return err
	}
	log.Printf("Agrégation terminée en %s", time.Since(start))

	if _, err := conn.Exec(ctx, `DROP TABLE IF EXISTS staging_passwords;`); err != nil {
		return fmt.Errorf("drop staging: %w", err)
	}

	log.Println("Recalcul des statistiques (ANALYZE)...")
	if _, err := conn.Exec(ctx, `ANALYZE breached_passwords;`); err != nil {
		return fmt.Errorf("analyze: %w", err)
	}

	return nil
}

func finalizeIntoEmptyTable(ctx context.Context, conn *pgxpool.Conn) error {
	statements := []string{
		`ALTER TABLE breached_passwords DROP CONSTRAINT IF EXISTS breached_passwords_pkey`,
		// Nettoyage d'un éventuel index hérité d'un schéma antérieur : la clé
		// primaire composite ci-dessous sert déjà efficacement
		// WHERE hash_prefix = $1, le rendant redondant.
		`DROP INDEX IF EXISTS idx_breached_passwords_prefix`,
		`INSERT INTO breached_passwords (hash_prefix, hash_suffix, occurrence_count)
			SELECT hash_prefix, hash_suffix, COUNT(*)::INT
			FROM staging_passwords
			GROUP BY hash_prefix, hash_suffix`,
		`ALTER TABLE breached_passwords ADD PRIMARY KEY (hash_prefix, hash_suffix)`,
	}
	for _, stmt := range statements {
		if _, err := conn.Exec(ctx, stmt); err != nil {
			return fmt.Errorf("finalize (table vide): %w", err)
		}
	}
	return nil
}
