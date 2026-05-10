from __future__ import annotations

import asyncio

from collections.abc import Awaitable, Callable
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse

ReadinessCheck = tuple[str, Callable[[], Awaitable[None]]]

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(request: Request):
    checks_registry: list[ReadinessCheck] = getattr(request.app.state, "readyz_checks", [])
    results = await asyncio.gather(
        *(asyncio.wait_for(check(), timeout=2.0) for _, check in checks_registry),
        return_exceptions=True,
    )

    checks: dict[str, str] = {}
    for (name, _), result in zip(checks_registry, results):
        if isinstance(result, Exception):
            checks[name] = f"fail: {str(result)[:200]}"
        else:
            checks[name] = "ok"

    if all(status == "ok" for status in checks.values()):
        return {"status": "ready", "checks": checks}

    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "checks": checks},
    )
