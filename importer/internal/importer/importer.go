// Package importer orchestre le pipeline complet de chargement du fichier
// rockyou.txt : lecture -> hachage (parallélisé) -> écriture par lots
// (COPY) -> agrégation finale en base.
package importer

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"
	"sync"
	"sync/atomic"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/sync/errgroup"

	"github.com/example/rockyou-importer/internal/db"
	"github.com/example/rockyou-importer/internal/hasher"
)

type Config struct {
	FilePath     string
	HashWorkers  int
	WriteWorkers int
	BatchSize    int
}

// Run exécute le pipeline complet et affiche une progression régulière.
func Run(ctx context.Context, pool *pgxpool.Pool, cfg Config) error {
	start := time.Now()

	if err := db.EnsureTargetEmpty(ctx, pool); err != nil {
		return err
	}

	if err := db.PrepareStaging(ctx, pool); err != nil {
		return fmt.Errorf("prepare staging: %w", err)
	}

	file, err := os.Open(cfg.FilePath)
	if err != nil {
		return fmt.Errorf("open file: %w", err)
	}
	defer file.Close()

	linesCh := make(chan string, 10_000)
	rowsCh := make(chan db.Row, 10_000)
	batchesCh := make(chan []db.Row, cfg.WriteWorkers*2)

	var linesRead atomic.Int64
	var rowsWritten atomic.Int64

	// 1) Lecture séquentielle du fichier (I/O disque = goulot naturel).
	go func() {
		defer close(linesCh)
		scanner := bufio.NewScanner(file)
		// rockyou.txt peut contenir des lignes atypiques ; on augmente
		// la taille max de buffer pour éviter tout troncage.
		buf := make([]byte, 0, 1024*1024)
		scanner.Buffer(buf, 1024*1024)
		for scanner.Scan() {
			line := scanner.Text()
			if line == "" {
				continue
			}
			linesCh <- line
			linesRead.Add(1)
		}
		if err := scanner.Err(); err != nil {
			log.Printf("erreur de lecture: %v", err)
		}
	}()

	// 2) Hachage parallélisé (SHA-1) sur plusieurs goroutines CPU-bound.
	var hashWg sync.WaitGroup
	for i := 0; i < cfg.HashWorkers; i++ {
		hashWg.Add(1)
		go func() {
			defer hashWg.Done()
			for line := range linesCh {
				digest := hasher.Digest(line)
				prefix, suffix := hasher.Split(digest)
				if prefix == "" {
					continue
				}
				rowsCh <- db.Row{Prefix: prefix, Suffix: suffix}
			}
		}()
	}
	go func() {
		hashWg.Wait()
		close(rowsCh)
	}()

	// 3) Regroupement en lots de taille fixe pour le COPY.
	go func() {
		defer close(batchesCh)
		batch := make([]db.Row, 0, cfg.BatchSize)
		for row := range rowsCh {
			batch = append(batch, row)
			if len(batch) >= cfg.BatchSize {
				batchesCh <- batch
				batch = make([]db.Row, 0, cfg.BatchSize)
			}
		}
		if len(batch) > 0 {
			batchesCh <- batch
		}
	}()

	// 4) Écriture parallélisée via COPY (le pool pgx supporte des
	// écritures concurrentes sur plusieurs connexions). errgroup collecte
	// la première erreur rencontrée sans mutex manuel.
	var writeGroup errgroup.Group
	for i := 0; i < cfg.WriteWorkers; i++ {
		writeGroup.Go(func() error {
			for batch := range batchesCh {
				n, err := db.CopyBatch(ctx, pool, batch)
				if err != nil {
					return fmt.Errorf("copy batch: %w", err)
				}
				rowsWritten.Add(n)
			}
			return nil
		})
	}

	// 5) Progression périodique.
	progressDone := make(chan struct{})
	go func() {
		ticker := time.NewTicker(2 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-ticker.C:
				log.Printf(
					"... %d lignes lues, %d lignes écrites (%.0fs écoulées)",
					linesRead.Load(),
					rowsWritten.Load(),
					time.Since(start).Seconds(),
				)
			case <-progressDone:
				return
			}
		}
	}()

	writeErr := writeGroup.Wait()
	close(progressDone)

	if writeErr != nil {
		return writeErr
	}

	log.Printf(
		"Chargement brut terminé : %d lignes en %s",
		rowsWritten.Load(), time.Since(start),
	)

	if err := db.FinalizeImport(ctx, pool); err != nil {
		return fmt.Errorf("finalize: %w", err)
	}

	log.Printf("Import complet terminé en %s", time.Since(start))
	return nil
}
