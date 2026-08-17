"""
Accès PostgreSQL : cycle de vie du pool de connexions et requête de
recherche par préfixe de hash (modèle de confidentialité k-anonymat,
voir README).
"""
from __future__ import annotations

from dataclasses import dataclass

import asyncpg

from app.core.config import get_settings


@dataclass(frozen=True)
class SuffixMatch:
    suffix: str
    occurrence_count: int


class Database:
    """Encapsule le cycle de vie du pool de connexions asyncpg."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        settings = get_settings()
        self._pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            command_timeout=5,
        )

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Le pool de base de données n'est pas initialisé.")
        return self._pool


database = Database()


_SELECT_BY_PREFIX = """
    SELECT hash_suffix, occurrence_count
    FROM breached_passwords
    WHERE hash_prefix = $1
"""


async def find_by_prefix(prefix: str) -> list[SuffixMatch]:
    """
    Retourne toutes les entrées (suffixe + occurrences) dont le hash SHA-1
    commence par `prefix` (5 caractères hexadécimaux, déjà validés et
    normalisés en majuscules par `BreachCheckRequest`).

    Ne reçoit et ne journalise jamais de mot de passe ni de hash complet :
    c'est le cœur du modèle de confidentialité k-anonymat. Requête
    paramétrée ($1) : aucune injection SQL possible.
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(_SELECT_BY_PREFIX, prefix)
    return [SuffixMatch(row["hash_suffix"], row["occurrence_count"]) for row in rows]


async def health_check() -> bool:
    async with database.pool.acquire() as connection:
        result = await connection.fetchval("SELECT 1")
    return result == 1
