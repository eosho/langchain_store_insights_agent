from __future__ import annotations

import asyncio
import json

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from datetime import date as Date

from app.api.insights_client import FreshAgentAPIClient, InsightsAPIError
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
    client: FreshAgentAPIClient = Depends(get_insights_client),
):
    """Return a flat, LLM-friendly list of insights and recommendations.

    Args:
        store_id: Store/site identifier to filter.
        date: Optional business date in YYYY-mm-dd.

    Returns:
        InsightListResponse: Flat list of items with type = "insight" | "recommendation".

    Raises:
        HTTPException: On upstream failure or malformed staged data.
    """
    try:
        # Check first
        summaries = None

        # If not , fetch from source
        if summaries is None:
            # Prefer staged JSON if present; otherwise hit the upstream API.
            if _STAGE_FILE.exists():
                summaries = _filter_summaries(
                    await _load_stage_json(_STAGE_FILE), store_id, date
                )
            else:
                summaries = await client.get_insights(store_id=store_id, date=date)

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