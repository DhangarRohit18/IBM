"""
LEGACYX — Core Configuration.

All settings are loaded from environment variables.
No secrets are hardcoded here.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "LEGACYX"
    app_version: str = "0.1.0"
    app_secret_key: str = "change-me"

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://legacyx:legacyx_dev_password@localhost:5432/legacyx"
    database_sync_url: str = "postgresql+psycopg2://legacyx:legacyx_dev_password@localhost:5432/legacyx"

    # ── Redis ──────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Storage & Security Limits (Phase 2) ────────────────────────────────────
    storage_root: str = "./storage"
    max_upload_size_mb: int = 50
    max_extracted_size_mb: int = 250
    max_file_count: int = 10000
    max_single_file_size_mb: int = 25

    # ── CORS ───────────────────────────────────────────────────────────────────
    allowed_origins: str | list[str] = "http://localhost:5190,http://127.0.0.1:5190,http://localhost:5174,http://localhost:5173,http://localhost:3000,*"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        """Accept comma-separated string, JSON array, or list."""
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                import json
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        return v

    # ── Logging ────────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ── JWT ────────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # ── AI Providers (Phase 4+) ────────────────────────────────────────────────
    ibm_watsonx_api_key: str = ""
    ibm_watsonx_project_id: str = ""
    ibm_watsonx_url: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
