from __future__ import annotations

import json
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("app.timing")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Emit structured request timing logs for every request."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration_ms = max(int((time.perf_counter() - start_time) * 1000), 0)
            logger.info(
                json.dumps(
                    {
                        "method": method,
                        "path": path,
                        "status_code": 500,
                        "duration_ms": duration_ms,
                    }
                )
            )
            raise

        duration_ms = max(int((time.perf_counter() - start_time) * 1000), 0)
        logger.info(
            json.dumps(
                {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                }
            )
        )
        return response
