"""
ClaimGraph AI — RBAC & Protected Routes Integration Tests.

Validates role enforcement (Admin, Investigator, Analyst, Customer)
and protected route barriers.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _register_user(client: AsyncClient, email: str, role: str) -> str:
    """Helper registering a user and returning their access token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "full_name": f"User {role}",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_unauthenticated_request_to_protected_route_fails(client: AsyncClient) -> None:
    """Accessing protected routes without a token should return 401 Unauthorized."""
    r1 = await client.get("/api/v1/users")
    assert r1.status_code == 401

    r2 = await client.get("/api/v1/auth/me")
    assert r2.status_code == 401

    r3 = await client.get("/api/v1/audit/logs")
    assert r3.status_code == 401


@pytest.mark.asyncio
async def test_customer_cannot_access_admin_users_list(client: AsyncClient) -> None:
    """CUSTOMER role should be rejected with 403 Forbidden on /api/v1/users."""
    customer_token = await _register_user(client, "regular.customer@example.com", "CUSTOMER")

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_admin_can_access_users_list(client: AsyncClient) -> None:
    """ADMIN role can list users."""
    admin_token = await _register_user(client, "admin@claimgraph.ai", "ADMIN")

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_investigator_can_access_audit_logs(client: AsyncClient) -> None:
    """INVESTIGATOR role can query audit logs."""
    inv_token = await _register_user(client, "lead.investigator@claimgraph.ai", "INVESTIGATOR")

    response = await client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_customer_cannot_access_audit_logs(client: AsyncClient) -> None:
    """CUSTOMER role cannot query audit logs."""
    customer_token = await _register_user(client, "intruder.customer@example.com", "CUSTOMER")

    response = await client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_user_role(client: AsyncClient) -> None:
    """ADMIN role can update another user's role."""
    admin_token = await _register_user(client, "superadmin@claimgraph.ai", "ADMIN")
    cust_token = await _register_user(client, "promoted.user@example.com", "CUSTOMER")

    # Get customer's ID via /me
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {cust_token}"})
    user_id = me_resp.json()["data"]["id"]

    # Admin promotes user to ANALYST
    patch_resp = await client.patch(
        f"/api/v1/users/{user_id}",
        json={"role": "ANALYST"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["role"] == "ANALYST"
