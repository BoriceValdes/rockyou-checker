from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rockyou:rockyou@postgres:5432/rockyou"
    api_cors_origins: str = "http://localhost:5173"
    rate_limit_per_minute: int = 30
    db_pool_min_size: int = 2  
    db_pool_max_size: int = 10

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()
