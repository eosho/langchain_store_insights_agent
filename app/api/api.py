from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .insights_client import FreshAgentAPIClient
from .routes import health, insights, chat, version
from .middleware import LoggingMiddleware, RequestIDMiddleware
from graph import create_graph
from app.config.app_config import settings


logger = logging.getLogger(__name__)


API_PREFIX = "/v1/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context.

    - Initializes shared, long-lived resources and exposes them via `app.state`.
    - Ensures graceful shutdown of network clients and background resources.
    """
    # Shared clients/resources
    app.state.insights_client = FreshAgentAPIClient(
        base_url=settings.FRESH_AGENT_API_BASE_URL,
        api_key=settings.FRESH_AGENT_API_KEY,
    )
    app.state.chat_graph = create_graph()

    # Simple in-memory chat session store
    app.state.chat_sessions = {}
    try:
        yield
    except Exception as exc:
        logger.exception("Unhandled exception during app lifespan: %s", exc)
        raise
    finally:
        try:
            await app.state.insights_client.aclose()  # type: ignore[attr-defined]
        except Exception:
            logger.warning("Error while closing insights_client", exc_info=True)


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="Store Insights",
        lifespan=lifespan,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.router.prefix = "/v1/api"

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Add custom middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # API routers under a single prefix
    api = APIRouter(prefix=API_PREFIX)
    api.include_router(health.router)
    api.include_router(insights.router)
    api.include_router(chat.router)
    api.include_router(version.router)
    app.include_router(api)

    return app


app = create_app()
