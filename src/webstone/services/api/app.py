"""FastAPI application factory.

Creates and configures the FastAPI app with all routes, middleware,
and startup/shutdown lifecycle hooks.

Start the server:
    uvicorn webstone.services.api.app:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webstone.config import get_settings
from webstone.services.api.routes import router as api_router
from webstone.services.websocket.handler import router as ws_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup → yield → shutdown."""
    settings = get_settings()
    logger.info("Webstone API starting (env=%s)", settings.env)

    # TODO: Initialize runtime components on startup:
    #   - Setup tracing: setup_tracing(settings.otel_service_name)
    #   - Setup metrics: setup_metrics()
    #   - Start worker pool
    #   - Connect to queue backend
    #   - Connect to memory stores

    yield

    # TODO: Graceful shutdown:
    #   - Stop worker pool (drain in-flight tasks)
    #   - Flush telemetry buffers
    logger.info("Webstone API shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Webstone Research Runtime",
        description="Agentic research orchestration API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router)

    return app


app = create_app()
