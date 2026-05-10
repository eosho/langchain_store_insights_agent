"""Middleware for logging API requests and responses."""

from __future__ import annotations

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with timing information."""

    def __init__(self, app: ASGIApp, log_body: bool = True):
        """Initialize the logging middleware.

        Args:
            app: The ASGI application
            log_body: Whether to log request/response bodies (default: False for privacy)
        """
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware/handler in the chain

        Returns:
            The HTTP response
        """
        # Start timing
        start_time = time.time()

        # Extract request info
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"

        # Log request
        logger.info(f"→ {method} {url} from {client_host}")

        # Optionally log request body
        if self.log_body and method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                logger.debug(
                    f"Request body: {body.decode('utf-8')[:500]}..."
                )  # Limit to 500 chars
            except Exception as e:
                logger.warning(f"Could not read request body: {e}")

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            status_code = response.status_code
            log_level = logging.INFO if status_code < 400 else logging.ERROR
            logger.log(log_level, f"← {method} {url} {status_code} ({duration:.3f}s)")

            return response

        except Exception as e:
            # Log errors
            duration = time.time() - start_time
            logger.error(
                f"✗ {method} {url} ERROR: {str(e)} ({duration:.3f}s)", exc_info=True
            )
            raise
