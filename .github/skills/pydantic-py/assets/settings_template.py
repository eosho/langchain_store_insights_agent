"""
Application settings with pydantic-settings.

Usage:
    from {{module}} import get_settings

    settings = get_settings()
    print(settings.database_url)
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables:
        DATABASE_URL: Database connection string (required)
        API_KEY: API key for external services (required)
        DEBUG: Enable debug mode (default: false)
        LOG_LEVEL: Logging level (default: INFO)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings
    database_url: SecretStr
    api_key: SecretStr

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"

    # Constrained settings
    max_connections: int = Field(default=10, ge=1, le=100)
    timeout_seconds: float = Field(default=30.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()
