"""
ClaimGraph AI — Authentication Router.

Endpoints for user registration, authentication, token refresh, and identity inspection.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_client_ip, get_current_user
from app.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserMeResponse,
)
from app.auth.service import AuthService
from app.common.schemas import SuccessResponse
from app.core.database import get_db_session
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=SuccessResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Create a new user account and return signed JWT tokens."""
    ip = get_client_ip(request)
    ua = request.headers.get("User-Agent")
    tokens = await AuthService.register(db=db, data=data, ip_address=ip, user_agent=ua)
    return SuccessResponse(data=tokens, message="Registration successful")


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="Authenticate with credentials",
)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Authenticate with email and password, returning signed JWT tokens."""
    ip = get_client_ip(request)
    ua = request.headers.get("User-Agent")
    tokens = await AuthService.authenticate(
        db=db,
        email=data.email,
        password=data.password,
        ip_address=ip,
        user_agent=ua,
    )
    return SuccessResponse(data=tokens, message="Authentication successful")


@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="Refresh access token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Exchange a valid refresh token for a newly signed access/refresh token pair."""
    ip = get_client_ip(request)
    tokens = await AuthService.refresh_tokens(
        db=db,
        refresh_token=data.refresh_token,
        ip_address=ip,
    )
    return SuccessResponse(data=tokens, message="Token refreshed successfully")


@router.post(
    "/logout",
    response_model=SuccessResponse[None],
    summary="Terminate session",
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[None]:
    """Sign out the current user and write audit record."""
    ip = get_client_ip(request)
    await AuthService.logout(db=db, user=current_user, ip_address=ip)
    return SuccessResponse(data=None, message="Logged out successfully")


@router.get(
    "/me",
    response_model=SuccessResponse[UserMeResponse],
    summary="Current authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[UserMeResponse]:
    """Return the profile, role, and organization of the current authenticated user."""
    return SuccessResponse(
        data=UserMeResponse.model_validate(current_user),
        message="Profile retrieved",
    )
