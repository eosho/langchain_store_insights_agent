from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/version", tags=["version"])

_NAME = "langchain_store_insights_agent"
_VERSION = "0.1.0"


@router.get("")
async def version() -> dict[str, str]:
    return {"name": _NAME, "version": _VERSION}
