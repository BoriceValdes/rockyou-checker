from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    api_cors_origins: str
    rate_limit_per_minute: int
    db_pool_min_size: int
    db_pool_max_size: int

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()
