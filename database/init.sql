-- Schéma initial de la base RockYou Password Checker.
-- Exécuté automatiquement au premier démarrage du conteneur PostgreSQL
-- (voir docker-compose.yml, volume /docker-entrypoint-initdb.d).
-- UNLOGGED : ces données sont entièrement reconstructibles en relançant
CREATE UNLOGGED TABLE IF NOT EXISTS breached_passwords (
    hash_prefix     CHAR(5)      NOT NULL,
    hash_suffix     VARCHAR(35)  NOT NULL,
    occurrence_count INTEGER     NOT NULL DEFAULT 1,
    PRIMARY KEY (hash_prefix, hash_suffix)
);

-- Pas d'index secondaire sur hash_prefix seul : la clé primaire composite
-- (hash_prefix, hash_suffix) sert déjà efficacement les requêtes
-- WHERE hash_prefix = $1 (hash_prefix est la colonne de tête du B-Tree).

COMMENT ON TABLE breached_passwords IS
    'Hashs SHA-1 (découpés préfixe/suffixe, k-anonymat) des mots de passe '
    'présents dans le corpus RockYou. Aucun mot de passe en clair stocké. '
    'Table UNLOGGED : données reconstructibles via un ré-import.';
