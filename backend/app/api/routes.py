# Pas de `from __future__ import annotations` ici (contrairement aux autres
# modules du projet) : combiné à `@limiter.limit(...)` de slowapi, ça empêche
# Pydantic de résoudre l'annotation `BreachCheckRequest` du endpoint au
# démarrage (PydanticUndefinedAnnotation) et fait planter l'application.
from fastapi import APIRouter, Request

from app.api.schemas import (
    BreachCheckRequest,
    BreachCheckResponse,
    HealthResponse,
    SuffixMatchResponse,
)
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db import db

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health() -> HealthResponse:
    try:
        db_ok = await db.health_check()
    except Exception:
        db_ok = False
    return HealthResponse(status="ok" if db_ok else "degraded", database=db_ok)


@router.post("/breach-check", response_model=BreachCheckResponse, tags=["breach"])
@limiter.limit(lambda: f"{get_settings().rate_limit_per_minute}/minute")
async def breach_check(
    request: Request,  # requis par slowapi
    payload: BreachCheckRequest,
) -> BreachCheckResponse:
    """
    Recherche par préfixe de hash (k-anonymat, 5 caractères).

    Aucun mot de passe ni hash complet ne transite par cet endpoint.
    Le client compare ensuite localement le reste du hash aux suffixes
    retournés, sans jamais exposer d'information au serveur.
    """
    matches = await db.find_by_prefix(payload.hash_prefix)
    return BreachCheckResponse(
        hash_prefix=payload.hash_prefix,
        matches=[
            SuffixMatchResponse(hash_suffix=m.suffix, occurrence_count=m.occurrence_count)
            for m in matches
        ],
    )
