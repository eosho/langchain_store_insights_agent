from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING
from typing import TypeAlias

if TYPE_CHECKING:
    from .insights_client import FreshAgentAPIClient


ReadinessCheck: TypeAlias = tuple[str, Callable[[], Awaitable[None]]]


def build_readiness_checks(client: FreshAgentAPIClient) -> list[ReadinessCheck]:
    """Build startup-time readiness checks consumed by the `/readyz` endpoint."""

    async def fresh_agent_api_check() -> None:
        try:
            await client.readiness_check()
        except Exception as exc:
            raise RuntimeError(
                f"Fresh Agent API readiness check failed ({exc.__class__.__name__})"
            ) from exc

    return [("fresh_agent_api", fresh_agent_api_check)]
