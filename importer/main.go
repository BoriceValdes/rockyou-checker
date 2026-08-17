// Commande d'import du fichier rockyou.txt dans PostgreSQL.
//
// Usage:
//
//	importer -file /data/rockyou.txt -dsn "postgres://user:pass@host:5432/db"
package main

import (
	"context"
	"flag"
	"log"
	"os"
	"runtime"
	"time"

	"github.com/example/rockyou-importer/internal/db"
	"github.com/example/rockyou-importer/internal/importer"
)

func main() {
	filePath := flag.String("file", "/data/rockyou.txt", "chemin vers le fichier rockyou.txt")
	dsn := flag.String("dsn", os.Getenv("DATABASE_URL"), "chaîne de connexion PostgreSQL")
	hashWorkers := flag.Int("hash-workers", runtime.NumCPU(), "nombre de goroutines de hachage")
	writeWorkers := flag.Int("write-workers", 4, "nombre de goroutines d'écriture (COPY)")
	batchSize := flag.Int("batch-size", 20_000, "taille des lots insérés par COPY")
	timeout := flag.Duration("timeout", 30*time.Minute, "délai maximum de l'import")
	flag.Parse()

	if *dsn == "" {
		log.Fatal("DATABASE_URL manquant (variable d'environnement ou flag -dsn)")
	}

	ctx, cancel := context.WithTimeout(context.Background(), *timeout)
	defer cancel()

	pool, err := db.Connect(ctx, *dsn, int32(*writeWorkers+2))
	if err != nil {
		log.Fatalf("connexion base de données impossible: %v", err)
	}
	defer pool.Close()

	cfg := importer.Config{
		FilePath:     *filePath,
		HashWorkers:  *hashWorkers,
		WriteWorkers: *writeWorkers,
		BatchSize:    *batchSize,
	}

	log.Printf(
		"Démarrage de l'import (%d workers de hash, %d workers d'écriture, lots de %d)",
		cfg.HashWorkers, cfg.WriteWorkers, cfg.BatchSize,
	)

	if err := importer.Run(ctx, pool, cfg); err != nil {
		log.Fatalf("échec de l'import: %v", err)
	}
}
