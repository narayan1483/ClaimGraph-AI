"""
ClaimGraph AI — Health Check Endpoints.

Provides liveness, readiness, and deep health checks for orchestration
platforms (Kubernetes, Docker Compose, load balancers).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.redis import redis_health_check
from app.core.neo4j import neo4j_health_check

logger = get_logger(__name__)
router = APIRouter(tags=["Health"])

settings = get_settings()


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, Any]:
    """
    Basic liveness probe — returns OK if the process is running.
    Used by Kubernetes liveness probe and load balancers.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready", summary="Readiness probe")
async def readiness() -> dict[str, Any]:
    """
    Deep readiness probe — checks connectivity to all backing services.
    Used by Kubernetes readiness probe; traffic is routed only when ready.
    """
    checks: dict[str, bool] = {}
    overall = True

    # PostgreSQL — check via SQLAlchemy engine
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        checks["postgres"] = True
    except Exception as exc:
        logger.warning("health_postgres_failed", error=str(exc))
        checks["postgres"] = False
        overall = False

    # Redis
    redis_ok = await redis_health_check()
    checks["redis"] = redis_ok
    if not redis_ok:
        overall = False

    # Neo4j
    neo4j_ok = await neo4j_health_check()
    checks["neo4j"] = neo4j_ok
    if not neo4j_ok:
        overall = False

    return {
        "status": "ready" if overall else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
