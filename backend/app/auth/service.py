"""
ClaimGraph AI — Authentication Service.

Coordinates user authentication, token issuance, refresh cycles, and audit trails.
"""

from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.auth.schemas import RegisterRequest, TokenResponse
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserResponse
from app.users.service import UserService

settings = get_settings()


class AuthService:
    """Service handling credential verification and JWT token lifecycle."""

    @classmethod
    def _generate_token_response(cls, user: User) -> TokenResponse:
        """Create token pair and build TokenResponse."""
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            org_id=user.organization_id,
        )
        refresh_token = create_refresh_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            org_id=user.organization_id,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user),
        )

    @classmethod
    async def authenticate(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Validate user credentials and return new token pair."""
        user = await UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            # Log failed attempt
            await AuditService.log_event(
                db=db,
                action="AUTH_LOGIN_FAILED",
                entity_type="auth",
                user_id=user.id if user else None,
                details={"attempted_email": email},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise UnauthorizedError("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedError("Account is inactive.")

        # Log successful login
        await AuditService.log_event(
            db=db,
            action="AUTH_LOGIN_SUCCESS",
            entity_type="auth",
            user_id=user.id,
            details={"email": user.email, "role": user.role.value},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return cls._generate_token_response(user)

    @classmethod
    async def register(
        cls,
        db: AsyncSession,
        data: RegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Register a new user account and immediately authenticate."""
        user_create = UserCreate(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
            organization_id=data.organization_id,
        )
        user = await UserService.create_user(db=db, data=user_create, ip_address=ip_address)

        await AuditService.log_event(
            db=db,
            action="AUTH_REGISTER_SUCCESS",
            entity_type="auth",
            user_id=user.id,
            details={"email": user.email, "role": user.role.value},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return cls._generate_token_response(user)

    @classmethod
    async def refresh_tokens(
        cls,
        db: AsyncSession,
        refresh_token: str,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Issue new token pair using a valid refresh token."""
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await UserRepository.get_by_id(db, payload.sub)
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid refresh token or inactive account.")

        await AuditService.log_event(
            db=db,
            action="AUTH_TOKEN_REFRESHED",
            entity_type="auth",
            user_id=user.id,
            ip_address=ip_address,
        )

        return cls._generate_token_response(user)

    @classmethod
    async def logout(
        cls,
        db: AsyncSession,
        user: User,
        ip_address: Optional[str] = None,
    ) -> None:
        """Record user logout in audit trail."""
        await AuditService.log_event(
            db=db,
            action="AUTH_LOGOUT",
            entity_type="auth",
            user_id=user.id,
            ip_address=ip_address,
        )
