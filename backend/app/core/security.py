"""
ClaimGraph AI — Core Security & Cryptography.

Handles password hashing via bcrypt and JWT token generation/validation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TokenPayload(BaseModel):
    """Decoded JWT claims payload."""

    sub: str  # User ID
    email: str
    role: str
    org_id: str | None = None
    token_type: str = "access"  # "access" or "refresh"
    exp: datetime
    jti: str  # Unique token ID (useful for revocation)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception as exc:
        logger.warning("password_verification_failed", error=str(exc))
        return False


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    org_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "org_id": org_id,
        "token_type": "access",
        "exp": expire,
        "jti": str(uuid4()),
    }
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    user_id: str,
    email: str,
    role: str,
    org_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.jwt_refresh_token_expire_days)
    )
    to_encode: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "org_id": org_id,
        "token_type": "refresh",
        "exp": expire,
        "jti": str(uuid4()),
    }
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> TokenPayload:
    """
    Decode and validate a JWT token string.
    Raises UnauthorizedError if invalid, expired, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        token_type = payload.get("token_type")
        if token_type != expected_type:
            raise UnauthorizedError(
                f"Invalid token type: expected '{expected_type}', got '{token_type}'"
            )
        return TokenPayload(**payload)
    except JWTError as exc:
        logger.warning("jwt_decode_failed", error=str(exc))
        raise UnauthorizedError("Invalid or expired authentication token") from exc
