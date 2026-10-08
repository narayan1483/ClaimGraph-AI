"""
ClaimGraph AI — Redis Client.

Provides an async Redis connection with health-check support.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return the shared async Redis client, creating it on first call."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
        logger.info("redis_connected", url=settings.redis_url)
    return _redis_client


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("redis_disconnected")


async def redis_health_check() -> bool:
    """Return True if Redis responds to PING."""
    try:
        client = await get_redis()
        return await client.ping()
    except Exception as exc:
        logger.warning("redis_health_check_failed", error=str(exc))
        return False


import json
from typing import Any, Optional


async def cache_get(key: str) -> Optional[Any]:
    """Retrieve and deserialize a JSON cached value. Returns None on cache miss or failure."""
    try:
        client = await get_redis()
        val = await client.get(key)
        if val is not None:
            return json.loads(val)
        return None
    except Exception as exc:
        logger.debug("redis_cache_get_failed", key=key, error=str(exc))
        return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    """Serialize and cache a value with TTL. Returns False if Redis is unavailable."""
    try:
        client = await get_redis()
        val_str = json.dumps(value, default=str)
        await client.set(key, val_str, ex=ttl_seconds)
        return True
    except Exception as exc:
        logger.debug("redis_cache_set_failed", key=key, error=str(exc))
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from Redis cache."""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as exc:
        logger.debug("redis_cache_delete_failed", key=key, error=str(exc))
        return False

