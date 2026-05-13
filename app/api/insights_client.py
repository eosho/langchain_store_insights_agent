from __future__ import annotations

import httpx
import logging

from functools import wraps
from typing import Any, Dict, List, Optional, Set
from datetime import date as Date
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)

from app.config.app_config import settings


logger = logging.getLogger("insights.client")

# HTTP status codes that are considered transient and safe to retry.
RETRYABLE_STATUS_CODES: Set[int] = {429, 500, 502, 503, 504}

# Transport-level exceptions that indicate transient network issues.
RETRYABLE_TRANSPORT_EXC = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
    httpx.PoolTimeout,
)
READINESS_CHECK_TIMEOUT_SECONDS = 2.0


class InsightsAPIError(Exception):
    """Domain error for the external Insights API."""

    def __init__(self, message: str, status: Optional[int] = None) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message.
            status: Optional HTTP status code; 0 for non-HTTP failures.
        """
        super().__init__(message)
        self.status = status


def _is_retryable(exc: BaseException) -> bool:
    """Return True if an exception is considered transient/retryable.

    This predicate is used by Tenacity to decide whether to retry a failed call.

    Args:
        exc: The exception raised by the wrapped function.

    Returns:
        True if the exception is retryable; False otherwise.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    if isinstance(exc, RETRYABLE_TRANSPORT_EXC):
        return True
    if isinstance(exc, InsightsAPIError):
        return (exc.status in RETRYABLE_STATUS_CODES) or (exc.status == 0)
    return False


def _retryable(name: str = "insights_api"):
    """Async retry decorator with exponential backoff for transient failures.

    The decorated coroutine may increment `self.total_requests` and
    `self.retries_attempted` counters on the client instance.

    Args:
        name: Metric/logging prefix used by the retry logger.

    Returns:
        A decorator that can be applied to async methods.
    """

    def decorator(func):
        @wraps(func)
        @retry(
            reraise=True,
            stop=stop_after_attempt(getattr(settings, "insights_api_max_attempts", 3)),
            wait=wait_exponential(
                multiplier=getattr(settings, "insights_api_backoff_multiplier", 0.5),
                min=getattr(settings, "insights_api_backoff_min_seconds", 0.5),
                max=getattr(settings, "insights_api_backoff_max_seconds", 2.0),
            ),
            retry=retry_if_exception(_is_retryable),
            before_sleep=before_sleep_log(
                logging.getLogger(f"retry.{name}"), logging.WARNING
            ),
        )
        async def wrapper(self, *args, **kwargs):
            # Track attempts in a simple, observable way.
            self.total_requests = getattr(self, "total_requests", 0) + 1
            try:
                return await func(self, *args, **kwargs)
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                # Count retryable statuses; Tenacity will decide whether to retry.
                if status in RETRYABLE_STATUS_CODES:
                    self.retries_attempted = getattr(self, "retries_attempted", 0) + 1
                    raise
                # Non-retryable: normalize as domain error for consistent handling.
                raise InsightsAPIError(
                    f"HTTP {status}: {e.response.text}", status=status
                ) from e
            except InsightsAPIError as e:
                # Count only when considered retryable by our policy.
                if (e.status in RETRYABLE_STATUS_CODES) or (e.status == 0):
                    self.retries_attempted = getattr(self, "retries_attempted", 0) + 1
                    raise
                raise

        return wrapper

    return decorator


class FreshAgentAPIClient:
    """Async HTTP wrapper for the external recommendations/insights service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int | float | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            base_url: Optional override for the Fresh Agent API base URL. Defaults to
                `settings.fresh_agent_api_base_url`.
            api_key: Optional override for the API key. Defaults to
                `settings.fresh_agent_api_key`.
            timeout: Optional per-request timeout (seconds). Defaults to
                `settings.fresh_agent_api_timeout_seconds`.

        Raises:
            ValueError: If no base URL is configured.
        """
        self.base_url = base_url or settings.FRESH_AGENT_API_BASE_URL
        self.api_key = api_key or settings.FRESH_AGENT_API_KEY
        self.timeout = timeout or settings.FRESH_AGENT_API_TIMEOUT_SECONDS

        if not self.base_url:
            raise ValueError("FRESH_AGENT_API_BASE_URL must be configured")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=int(self.timeout),
            headers=self._headers(),
        )

        # Telemetry counters (updated by the retry decorator).
        self.total_requests: int = 0
        self.retries_attempted: int = 0

    def _headers(self) -> Dict[str, str]:
        """Build the default request headers.

        Returns:
            A dictionary of HTTP headers including `Accept` and optional `Authorization`.
        """
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def aclose(self) -> None:
        """Close the underlying HTTP session.

        Should be called during FastAPI lifespan shutdown to release resources.
        """
        await self._client.aclose()

    async def readiness_check(self) -> None:
        """Verify the upstream insights API is reachable and responding successfully.

        This probes the same endpoint used by normal insights retrieval so readiness
        reflects real dependency availability.
        """
        resp = await self._client.get(
            "/api/v1/store-details", timeout=READINESS_CHECK_TIMEOUT_SECONDS
        )
        resp.raise_for_status()

    @_retryable("get_insights")
    async def get_insights(
        self,
        store_id: Optional[str] = None,
        date: Optional[Date] = None,
    ) -> List[Dict[str, Any]]:
        """List insights/recommendations from the upstream service.

        Args:
            store_id: Optional filter for a specific store identifier.
            date: Optional date filter (YYYY-mm-dd). If provided, forwarded as ISO8601 date.

        Returns:
            A list of summary dicts (each may contain 'insights' and 'recommendations').

        Raises:
            InsightsAPIError: If the response body is malformed (non-list) or
                if a non-retryable HTTP/transport error occurs.
            httpx.HTTPStatusError: For retryable HTTP status codes; the retry
                decorator decides whether to reattempt, and will re-raise after
                final attempt.
        """
        params: Dict[str, Any] = {}
        if store_id:
            params["store_id"] = store_id
        if date:
            # Upstream expects a date string; we forward ISO format YYYY-mm-dd.
            params["applicable_date"] = date.isoformat()

        resp = await self._client.get(f"/api/v1/store-details", params=params)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            # Let Tenacity handle retryable status codes.
            raise

        data = resp.json()
        if not isinstance(data, list):
            # Use status=0 to indicate a client-side/format error (non-HTTP).
            raise InsightsAPIError(
                "Unexpected response format (expected list)", status=0
            )
        return data
