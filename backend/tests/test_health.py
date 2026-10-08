"""
ClaimGraph AI — Health endpoint tests.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_healthy(client: AsyncClient) -> None:
    """GET /api/v1/health should return 200 with status=healthy."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "ClaimGraph AI"
    assert "version" in body
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_health_endpoint_contains_environment(client: AsyncClient) -> None:
    """Health response should include the environment field."""
    response = await client.get("/api/v1/health")
    body = response.json()
    assert "environment" in body
    assert body["environment"] in ("development", "staging", "production")


@pytest.mark.asyncio
async def test_openapi_schema_available(client: AsyncClient) -> None:
    """The OpenAPI schema should be served at /openapi.json."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "ClaimGraph AI"
