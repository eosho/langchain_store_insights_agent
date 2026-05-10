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
            self._log_request_timing(method, path, 500, start_time)
            raise

        self._log_request_timing(method, path, status_code, start_time)
        return response

    def _log_request_timing(
        self, method: str, path: str, status_code: int, start_time: float
    ) -> None:
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
