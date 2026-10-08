"""
ClaimGraph AI — Authentication Schemas.

Pydantic models for authentication requests, tokens, and session payloads.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.users.models import UserRole
from app.users.schemas import UserDetailResponse, UserResponse


class LoginRequest(BaseModel):
    """User login credential payload."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class RegisterRequest(BaseModel):
    """Self-service registration payload."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = Field(default=UserRole.CUSTOMER)
    organization_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Token refresh payload."""

    refresh_token: str


class TokenResponse(BaseModel):
    """OAuth2 / JWT token response with user context."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserMeResponse(UserDetailResponse):
    """Detailed profile returned for /auth/me."""
    pass
