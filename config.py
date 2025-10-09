from __future__ import annotations
import logging

from enum import Enum
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("azure").setLevel(logging.WARNING)


class LLMProvider(str, Enum):
    """Enum for supported LLM providers."""

    OPENAI = "openai"
    AZURE = "azure"


class Settings(BaseSettings):
    """Centralized configuration and client factory for the Store Insights RAG system."""

    app_name: str = Field(default="store-insights", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # LLM Provider
    llm_provider: LLMProvider = Field(default=LLMProvider.AZURE, alias="LLM_PROVIDER")

    openai_api_key: Optional[SecretStr] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")

    azure_openai_endpoint: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_ENDPOINT"
    )
    azure_openai_api_key: Optional[SecretStr] = Field(
        default=None, alias="AZURE_OPENAI_API_KEY"
    )
    azure_openai_api_version: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_DEPLOYMENT"
    )

    # External fresh API
    fresh_agent_api_base_url: Optional[str] = Field(
        default=None, alias="FRESH_AGENT_API_BASE_URL"
    )
    fresh_agent_api_key: Optional[str] = Field(default=None, alias="FRESH_AGENT_API_KEY")
    fresh_agent_api_timeout_seconds: int = Field(
        default=30, alias="FRESH_AGENT_API_TIMEOUT_SECONDS"
    )

    store_insights_api_url: Optional[str] = Field(
        default="http://localhost:8000/v1/api", alias="STORE_INSIGHTS_API_URL"
    )

    # Observability / Telemetry
    application_insights_connection_string: Optional[str] = Field(
        default=None, alias="APPLICATION_INSIGHTS_CONNECTION_STRING"
    )

    # Cosmos DB
    cosmos_db_endpoint: Optional[str] = Field(default=None, alias="COSMOS_DB_ENDPOINT")
    cosmos_db_key: Optional[str] = Field(default=None, alias="COSMOS_DB_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True


settings = Settings()
