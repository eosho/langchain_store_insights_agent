from __future__ import annotations

import asyncio

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.readiness import ReadinessCheck

READINESS_CHECK_TIMEOUT = 2.0
MAX_ERROR_MESSAGE_LENGTH = 200

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(request: Request):
    """Run registered readiness checks and report aggregate readiness state."""

    readiness_checks: list[ReadinessCheck] = getattr(request.app.state, "readyz_checks", [])

    async def _run_check_with_timeout(check):
        try:
            await asyncio.wait_for(check(), timeout=READINESS_CHECK_TIMEOUT)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(
                f"Check timed out after {READINESS_CHECK_TIMEOUT}s"
            ) from exc

    results = await asyncio.gather(
        *(_run_check_with_timeout(check) for _, check in readiness_checks),
        return_exceptions=True,
    )

    checks: dict[str, str] = {}
    for (name, _), result in zip(readiness_checks, results):
        if isinstance(result, Exception):
            message = str(result)
            if len(message) > MAX_ERROR_MESSAGE_LENGTH:
                message = f"{message[:MAX_ERROR_MESSAGE_LENGTH]}..."
            checks[name] = f"fail: {message}"
        else:
            checks[name] = "ok"

    if all(status == "ok" for status in checks.values()):
        return {"status": "ready", "checks": checks}

    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "checks": checks},
    )
