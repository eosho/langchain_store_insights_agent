from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeAlias

from .insights_client import FreshAgentAPIClient


ReadinessCheck: TypeAlias = tuple[str, Callable[[], Awaitable[None]]]


def build_readiness_checks(client: FreshAgentAPIClient) -> list[ReadinessCheck]:
    async def fresh_agent_api_check() -> None:
        response = await client._client.get("/api/v1/store-details", timeout=1.5)
        response.raise_for_status()

    return [("fresh_agent_api", fresh_agent_api_check)]
