"""
ClaimGraph AI — Authentication & JWT Integration Tests.

Validates registration, login, credential failure, token refresh, and /auth/me.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, decode_token
from app.users.models import UserRole


@pytest.mark.asyncio
async def test_register_new_customer(client: AsyncClient) -> None:
    """User registration should create account and return JWT access/refresh tokens."""
    payload = {
        "email": "sarah.connor@example.com",
        "password": "StrongPassword123!",
        "full_name": "Sarah Connor",
        "role": "CUSTOMER",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "sarah.connor@example.com"
    assert data["user"]["role"] == "CUSTOMER"


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient) -> None:
    """Registering with an already used email should return 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "Duplicate User",
        "role": "CUSTOMER",
    }
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    body = r2.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Valid credentials should authenticate and return tokens."""
    register_payload = {
        "email": "investigator.john@claimgraph.ai",
        "password": "InvestigatorPass123!",
        "full_name": "John Investigator",
        "role": "INVESTIGATOR",
    }
    r_reg = await client.post("/api/v1/auth/register", json=register_payload)
    assert r_reg.status_code == 201

    login_payload = {
        "email": "investigator.john@claimgraph.ai",
        "password": "InvestigatorPass123!",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["user"]["role"] == "INVESTIGATOR"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    """Incorrect password should return 401 Unauthorized."""
    register_payload = {
        "email": "victim@example.com",
        "password": "CorrectPassword123!",
        "full_name": "Victim User",
        "role": "CUSTOMER",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "victim@example.com",
        "password": "WrongPassword!",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient) -> None:
    """Non-existent email should return 401 Unauthorized without leaking email existence."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_token_validation() -> None:
    """Unit test for token creation and decoding."""
    token = create_access_token(
        user_id="usr-12345",
        email="token.test@example.com",
        role="ANALYST",
    )
    payload = decode_token(token, expected_type="access")
    assert payload.sub == "usr-12345"
    assert payload.email == "token.test@example.com"
    assert payload.role == "ANALYST"
    assert payload.token_type == "access"


@pytest.mark.asyncio
async def test_refresh_token_exchange(client: AsyncClient) -> None:
    """Refresh token can be exchanged for new access/refresh tokens."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresher@example.com",
            "password": "Password123!",
            "full_name": "Refresher User",
            "role": "CUSTOMER",
        },
    )
    tokens = reg.json()["data"]
    refresh_token = tokens["refresh_token"]

    r_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert r_refresh.status_code == 200
    new_tokens = r_refresh.json()["data"]
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient) -> None:
    """GET /api/v1/auth/me should return current user details with bearer token."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me.check@example.com",
            "password": "Password123!",
            "full_name": "Me Check",
            "role": "CUSTOMER",
        },
    )
    token = reg.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    user_me = response.json()["data"]
    assert user_me["email"] == "me.check@example.com"
    assert user_me["full_name"] == "Me Check"
    assert "customer_profile" in user_me


@pytest.mark.asyncio
async def test_logout_endpoint(client: AsyncClient) -> None:
    """POST /api/v1/auth/logout should write audit record and succeed."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout.user@example.com",
            "password": "Password123!",
            "full_name": "Logout User",
            "role": "CUSTOMER",
        },
    )
    token = reg.json()["data"]["access_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
