"""
ClaimGraph AI — Application Factory.

Creates and configures the FastAPI application with all middleware,
exception handlers, and routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.redis import close_redis
from app.core.neo4j import close_neo4j
from app.core.kafka import close_kafka_producer
from app.api.v1.router import api_v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown hooks."""
    settings = get_settings()
    setup_logging(
        log_level=settings.app_log_level,
        json_output=settings.app_env != "development",
    )
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )
    yield
    # ── Graceful shutdown ──
    logger.info("application_shutting_down")
    await close_redis()
    await close_neo4j()
    await close_kafka_producer()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    settings = get_settings()

    # Initialise logging early so factory-time logs are structured
    setup_logging(
        log_level=settings.app_log_level,
        json_output=settings.app_env != "development",
    )

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Agentic Insurance Claims & Fraud Intelligence Platform. "
            "Combines ML fraud detection, knowledge graphs, agentic AI, "
            "and human-in-the-loop workflows for enterprise claim intelligence."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom Middleware ────────────────────────────────────────
    app.add_middleware(RequestContextMiddleware)

    # ── Exception Handlers ──────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ─────────────────────────────────────────────────
    app.include_router(api_v1_router)

    logger.info("application_configured", routes=len(app.routes))
    return app


app = create_app()

