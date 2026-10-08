"""
ClaimGraph AI — Neo4j Client.

Provides async Neo4j driver management with health-check support.
"""

from __future__ import annotations

from neo4j import AsyncGraphDatabase, AsyncDriver

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_neo4j_driver: AsyncDriver | None = None


async def get_neo4j_driver() -> AsyncDriver:
    """Return the shared async Neo4j driver, creating it on first call."""
    global _neo4j_driver
    if _neo4j_driver is None:
        settings = get_settings()
        _neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=50,
        )
        logger.info("neo4j_connected", uri=settings.neo4j_uri)
    return _neo4j_driver


async def close_neo4j() -> None:
    """Gracefully close the Neo4j driver."""
    global _neo4j_driver
    if _neo4j_driver is not None:
        await _neo4j_driver.close()
        _neo4j_driver = None
        logger.info("neo4j_disconnected")


async def neo4j_health_check() -> bool:
    """Return True if Neo4j responds to a connectivity check."""
    try:
        driver = await get_neo4j_driver()
        await driver.verify_connectivity()
        return True
    except Exception as exc:
        logger.warning("neo4j_health_check_failed", error=str(exc))
        return False
