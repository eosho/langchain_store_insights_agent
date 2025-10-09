# secrets_utils.py

"""Secrets Utility Module.

Provides helper functions for managing secrets stored on the filesystem
(e.g., under `/etc/secrets` in containers or a configured local path).
Secrets are expected to be stored as `.txt` files, each containing a single value.
"""

import logging

from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("azure").setLevel(logging.WARNING)


# Default secrets directory
SECRETS_PATH = "/etc/secrets"


def _resolve_secret_path(filename: str) -> Path:
    """Return the full path to a secret file, adding `.txt` if missing."""
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    return Path(SECRETS_PATH) / filename


def get_secret(filename: str) -> Optional[str]:
    """
    Fetch a secret value from the configured secrets path.

    Args:
        filename: Secret name (with or without `.txt` extension).

    Returns:
        Secret value as a string, or None if not found or unreadable.
    """
    secret_path = _resolve_secret_path(filename)

    try:
        if not secret_path.exists():
            return None

        secret = secret_path.read_text(encoding="utf-8").strip()
        return secret or None
    except Exception as e:
        logger.error("Error reading secret '%s': %s", filename, e)
        return None


def list_secrets() -> list[str]:
    """
    List all available secrets in the secrets directory.

    Returns:
        List of `.txt` filenames, or an empty list if directory is missing/unreadable.
    """
    try:
        secrets_dir = Path(SECRETS_PATH)
        if not secrets_dir.exists():
            return []
        return [f.name for f in secrets_dir.glob("*.txt")]
    except Exception as e:
        logger.error("Error listing secrets: %s", e)
        return []


def secret_exists(filename: str) -> bool:
    """
    Check if a secret file exists.

    Args:
        filename: Secret name (with or without `.txt` extension).

    Returns:
        True if the file exists, False otherwise.
    """
    return _resolve_secret_path(filename).exists()