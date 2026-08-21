from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.routes import router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.db import database


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute des en-têtes de sécurité HTTP de base à chaque réponse."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="RockYou Password Checker API",
        description=(
            "API de vérification de compromission de mots de passe "
            "(base RockYou), conçue selon un "
            "modèle de confidentialité par k-anonymat."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.state.limiter = limiter
    # Le handler de slowapi est typé pour RateLimitExceeded, plus précis que
    # la signature générique (Request, Exception) -> Response attendue par
    # Starlette
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.add_middleware(SecurityHeadersMiddleware)

    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
