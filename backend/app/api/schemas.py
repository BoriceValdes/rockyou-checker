from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class BreachCheckRequest(BaseModel):
    """
    Requête de vérification par préfixe (k-anonymat).

    IMPORTANT : `hash_prefix` ne contient JAMAIS le mot de passe ni son
    hash complet — uniquement les 5 premiers caractères hexadécimaux du
    SHA-1, calculé côté client. Voir README (modèle de confidentialité).
    """

    hash_prefix: str = Field(..., min_length=5, max_length=5, examples=["5BAA6"])

    @field_validator("hash_prefix")
    @classmethod
    def validate_hex(cls, value: str) -> str:
        value = value.upper()
        if not all(c in "0123456789ABCDEF" for c in value):
            raise ValueError("hash_prefix doit être hexadécimal (0-9, A-F).")
        return value


class SuffixMatchResponse(BaseModel):
    hash_suffix: str
    occurrence_count: int


class BreachCheckResponse(BaseModel):
    hash_prefix: str
    matches: list[SuffixMatchResponse]


class HealthResponse(BaseModel):
    status: str
    database: bool
