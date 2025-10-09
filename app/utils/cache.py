"""Simple caching layer for insights data with 24-hour TTL."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from cachetools import TTLCache
from datetime import date as Date

logger = logging.getLogger(__name__)

# In-memory cache with 24-hour TTL (86400 seconds)
# maxsize=1000 means max 1000 different cache keys
_insights_cache: TTLCache = TTLCache(maxsize=1000, ttl=86400)


def _make_cache_key(store_id: Optional[str], date: Optional[Date]) -> str:
    """Generate a unique cache key from query parameters.

    Args:
        store_id: Optional store identifier
        date: Optional business date

    Returns:
        Unique cache key string
    """
    key_data = {
        "store_id": store_id or "all",
        "date": date.isoformat() if date else "all",
    }
    # Use hash for shorter keys
    key_str = json.dumps(key_data, sort_keys=True)
    return f"insights:{hashlib.md5(key_str.encode()).hexdigest()}"


def get_cached_insights(
    store_id: Optional[str], date: Optional[Date]
) -> Optional[List[Dict[str, Any]]]:
    """Retrieve insights from cache if available.

    Args:
        store_id: Store identifier
        date: Business date

    Returns:
        Cached summaries list or None if not found/expired
    """
    key = _make_cache_key(store_id, date)
    cached = _insights_cache.get(key)

    if cached is not None:
        logger.info(f"Cache HIT for key: {key}")
        return cached

    logger.info(f"Cache MISS for key: {key}")
    return None


def set_cached_insights(
    store_id: Optional[str], date: Optional[Date], summaries: List[Dict[str, Any]]
) -> None:
    """Store insights in cache with 24-hour TTL.

    Args:
        store_id: Store identifier
        date: Business date
        summaries: List of summary dicts to cache
    """
    key = _make_cache_key(store_id, date)
    _insights_cache[key] = summaries
    logger.info(f"Cached {len(summaries)} summaries for key: {key}")


def clear_insights_cache() -> None:
    """Clear all cached insights. Useful for manual refresh."""
    _insights_cache.clear()
    logger.info("Insights cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring.

    Returns:
        Dict with cache size, maxsize, and TTL info
    """
    return {
        "current_size": len(_insights_cache),
        "max_size": _insights_cache.maxsize,
        "ttl_seconds": _insights_cache.ttl,
        "ttl_hours": _insights_cache.ttl / 3600,
    }
