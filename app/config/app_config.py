# app_config.py

"""Application Configuration Module.

This module centralizes how configuration values are loaded across the
application. It supports environment variables, `.env` files, and filesystem-
based secrets (e.g., mounted at `/etc/secrets` via Akeyless or Kubernetes).
"""

import os
import logging

from enum import Enum
from typing import Optional
from functools import lru_cache
from dotenv import (
    find_dotenv,
    load_dotenv
)

from .secret_config import get_secret

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("azure").setLevel(logging.WARNING)


# Override dotenv values
load_dotenv(find_dotenv(), override=True)



@lru_cache(maxsize=1)
class AppConfig:
    """Centralized application configuration (all resolved to strings)."""

    def __init__(self) -> None:
        # Azure OpenAI/Projects
        self.AZURE_OPENAI_API_VERSION = self._resolve("AZURE_OPENAI_API_VERSION", required=False, default="2024-12-01-preview")
        self.AZURE_OPENAI_ENDPOINT = self._resolve("AZURE_OPENAI_ENDPOINT", required=True)
        self.AZURE_OPENAI_API_KEY = self._resolve("AZURE_OPENAI_API_KEY", required=False, is_secret=True)
        self.AZURE_OPENAI_DEPLOYMENT = self._resolve("AZURE_OPENAI_DEPLOYMENT")

        # LLM Provider
        self.LLM_PROVIDER = self._resolve("LLM_PROVIDER", required=True, default="azure").lower()

        # External Fresh API
        self.FRESH_AGENT_API_BASE_URL = self._resolve("FRESH_AGENT_API_BASE_URL", required=False)
        self.FRESH_AGENT_API_KEY = self._resolve("FRESH_AGENT_API_KEY", required=False, is_secret=True)
        self.FRESH_AGENT_API_TIMEOUT_SECONDS = self._resolve("FRESH_AGENT_API_TIMEOUT_SECONDS", required=False, default="30")

        # OpenAI
        self.OPENAI_API_KEY = self._resolve("OPENAI_API_KEY", required=False, is_secret=True)
        self.OPENAI_MODEL_NAME = self._resolve("OPENAI_MODEL_NAME", required=False, default="gpt-4o")

        # Cosmos
        self.COSMOS_DB_ENDPOINT = self._resolve("COSMOS_DB_ENDPOINT", required=False, is_secret=True)
        self.COSMOS_DB_KEY = self._resolve("COSMOS_DB_KEY", required=False, is_secret=True)
        self.COSMOS_DB_DATABASE = self._resolve("COSMOS_DB_DATABASE", required=False)
        self.COSMOS_DB_CONTAINER = self._resolve("COSMOS_DB_CONTAINER", required=False)

        # Store Insights API
        self.STORE_INSIGHTS_API_URL = self._resolve("STORE_INSIGHTS_API_URL", required=True, default="http://localhost:8000/v1/api")

        # Logging
        self.APPLICATION_INSIGHTS_CONNECTION_STRING = self._resolve(
            "APPLICATIONINSIGHTS_CONNECTION_STRING", required=False, default="", is_secret=True
        )


    def _resolve(
        self,
        name: str,
        required: bool = True,
        default: Optional[str] = None,
        is_secret: bool = False,
    ) -> str:
        """Resolve a config value from environment, secret store, or default.

        Lookup order:
            1. Environment variable (including values loaded from `.env`).
            2. Secret store (only if `is_secret=True`).
            3. Explicit default value (if provided).

        Behavior:
            * If `required=True` and no value can be resolved, raises ValueError.
            * If optional and unresolved, logs a warning and returns an empty string.
            * Environment variables always take precedence over secrets for
            easier local development, even if `is_secret=True`.

        Args:
            name: The environment variable / secret name.
            required: Whether the value must exist. Defaults to True.
            default: Value to use if neither env nor secret is found.
            is_secret: If True, also check the secret store when env is missing.

        Returns:
            str: The resolved value. Never returns None.
        """
        if is_secret:
            value = get_secret(name) or os.getenv(name) or default
        else:
            value = os.getenv(name) or get_secret(name) or default

        if value is None:
            value = default

        if value is None and required:
            raise ValueError(f"Missing required config: {name}")

        if value is None:
            logger.warning("Config %s not found", name)
            value = ""

        return value


# global instance
settings = AppConfig()