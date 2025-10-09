from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .insights_client import ExternalInsightsClient
from .routes import health, insights, chat
from .middleware import LoggingMiddleware, RequestIDMiddleware
from graph import StoreInsightsGraph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Shared clients/resources
    app.state.insights_client = ExternalInsightsClient()
    app.state.chat_graph = StoreInsightsGraph()

    # Simple in-memory chat session store
    app.state.chat_sessions = {}
    try:
        yield
    finally:
        await app.state.insights_client.aclose()  # type: ignore[attr-defined]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Store Insights",
        lifespan=lifespan,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.router.prefix = "/v1/api"

    # Add middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Routers
    app.include_router(health.router)
    app.include_router(insights.router)
    app.include_router(chat.router)

    return app


# uvicorn entrypoint: uvicorn app.api.app:app --reload
app = create_app()
