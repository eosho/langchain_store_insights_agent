from __future__ import annotations

import asyncio
import json

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from datetime import date as Date

from app.api.insights_client import FreshAgentAPIClient, InsightsAPIError
from app.utils.cache import (
    get_cached_insights,
    set_cached_insights,
    get_cache_stats,
    clear_insights_cache,
)
from schemas import Insight, InsightListResponse

router = APIRouter(prefix="/insights", tags=["insights"])

_STAGE_FILE = Path("data/stage.json")


def get_insights_client(request: Request) -> FreshAgentAPIClient:
    """Retrieve the shared FreshAgentAPIClient from app state (set in lifespan)."""
    return request.app.state.insights_client


async def _load_stage_json(path: Path) -> List[Dict[str, Any]]:
    """Asynchronously load staged summaries from a JSON file.

    Args:
        path: Location of the staged JSON (list of summaries).

    Returns:
        A list of summary dicts (each may contain `insights` and `recommendations`).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If JSON is not a list payload.
    """
    if not path.exists():
        raise FileNotFoundError(str(path))
    text = await asyncio.to_thread(path.read_text, encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("stage.json must contain a JSON array (list) of summaries.")
    return data


def _filter_summaries(
    summaries: List[Dict[str, Any]],
    store_id: Optional[str],
    date: Optional[Date],
) -> List[Dict[str, Any]]:
    """Apply in-process filters equivalent to upstream query params.

    Args:
        summaries: List of summary dicts to filter.
        store_id: Optional store/site identifier to filter.
        date: Optional business date in YYYY-mm-dd to filter.

    Returns:
        Filtered list of summaries matching the criteria.
    """
    out: List[Dict[str, Any]] = []
    for s in summaries:
        site = s.get("site_id") or s.get("store_id")
        if store_id is not None and str(site) != str(store_id):
            continue
        if date is not None and s.get("applicable_date") != date.isoformat():
            continue
        out.append(s)
    return out


@router.get("", response_model=InsightListResponse)
async def get_insights(
    store_id: Optional[str] = Query(
        default=None,
        description="Store/site identifier (e.g., '100').",
        examples=["100"],
    ),
    date: Optional[Date] = Query(
        default=None,
        description="Optional business date (YYYY-mm-dd).",
        examples=["2025-10-01"],
    ),
    use_cache: bool = Query(
        default=True,
        description="Use cached data if available (24-hour TTL).",
    ),
    client: FreshAgentAPIClient = Depends(get_insights_client),
):
    """Return a flat, LLM-friendly list of insights and recommendations.

    Behavior:
      • Checks cache first (24-hour TTL) unless use_cache=False
      • If `data/stage.json` exists, load and filter it locally (dev/staging mode).
      • Otherwise, call the external insights API via `FreshAgentAPIClient`.

    The external/staged payload is a list of *summaries*. Each summary may contain
    `insights[]` and `recommendations[]`. This route flattens both into `Insight`
    items, carrying IDs for citation.

    Args:
        store_id: Store/site identifier to filter.
        date: Optional business date in YYYY-mm-dd.
        use_cache: Whether to use cached data (default: True)

    Returns:
        InsightListResponse: Flat list of items with type = "insight" | "recommendation".

    Raises:
        HTTPException: On upstream failure or malformed staged data.
    """
    try:
        # Check cache first
        summaries = None
        if use_cache:
            summaries = get_cached_insights(store_id, date)

        # If not in cache, fetch from source
        if summaries is None:
            # Prefer staged JSON if present; otherwise hit the upstream API.
            if _STAGE_FILE.exists():
                summaries = _filter_summaries(
                    await _load_stage_json(_STAGE_FILE), store_id, date
                )
            else:
                summaries = await client.get_insights(store_id=store_id, date=date)

            # Cache the results
            set_cached_insights(store_id, date, summaries)

        items: List[Insight] = []
        for s in summaries:
            site = s.get("site_id") or s.get("store_id")
            applicable_date = s.get("applicable_date")
            generated_ts = s.get("generated_date_time") or s.get("_ts")

            # Flatten INSIGHTS
            for ins in s.get("insights") or []:
                items.append(
                    Insight(
                        id=ins.get("insight_id") or ins.get("id") or "",
                        store_id=site,
                        type="insight",
                        title=ins.get("title"),
                        text=ins.get("content"),
                        score=None,
                        ts=applicable_date or generated_ts,
                    )
                )

            # Flatten RECOMMENDATIONS
            for rec in s.get("recommendations") or []:
                items.append(
                    Insight(
                        id=rec.get("recommendation_id") or rec.get("id") or "",
                        store_id=site,
                        type="recommendation",
                        title=rec.get("title"),
                        text=rec.get("content"),
                        score=None,
                        ts=applicable_date or generated_ts,
                    )
                )

        return {"items": items}

    except FileNotFoundError:
        # Should not happen because we check existence, but keep explicit message.
        raise HTTPException(status_code=500, detail="Staged data file not found.")
    except ValueError as ve:
        raise HTTPException(
            status_code=500, detail=f"Invalid staged data: {ve}"
        ) from ve
    except InsightsAPIError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc


@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics for monitoring.

    Returns:
        Cache size, capacity, and TTL information
    """
    return get_cache_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Manually clear the insights cache.

    Useful for forcing a fresh data fetch.
    """
    clear_insights_cache()
    return {"message": "Cache cleared successfully"}
