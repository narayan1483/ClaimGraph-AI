"""
ClaimGraph AI — Authentication & RBAC Dependencies.

FastAPI dependencies for JWT token extraction, user validation, and role enforcement.
"""

from __future__ import annotations

from typing import Callable, Sequence

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.users.models import User, UserRole
from app.users.repository import UserRepository

# Use HTTPBearer for clean Bearer token header handling
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Extract and validate JWT access token from Authorization header.
    Returns the loaded User object or raises UnauthorizedError.
    """
    if not credentials:
        raise UnauthorizedError("Missing Authorization bearer header")

    token = credentials.credentials
    payload = decode_token(token, expected_type="access")

    user = await UserRepository.get_by_id(db, payload.sub, with_profiles=True)
    if not user:
        raise UnauthorizedError("User associated with token no longer exists")

    if not user.is_active:
        raise ForbiddenError("User account has been deactivated")

    return user


get_current_active_user = get_current_user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User | None:
    """Extract current user if bearer token is provided and valid, otherwise return None."""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = decode_token(token, expected_type="access")
        user = await UserRepository.get_by_id(db, payload.sub, with_profiles=True)
        if user and user.is_active:
            return user
    except Exception:
        pass
    return None



def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """
    Factory creating a dependency that verifies the user has one of the allowed roles.
    Raises ForbiddenError if user's role is not authorized.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            role_names = [r.value for r in allowed_roles]
            raise ForbiddenError(
                f"Access denied: Required role in {role_names}, but user has '{current_user.role.value}'"
            )
        return current_user

    return role_checker


def get_client_ip(request: Request) -> str | None:
    """Extract client IP addressing forwarded proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
