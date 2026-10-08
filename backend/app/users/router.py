"""
ClaimGraph AI — Users Router.

Protected endpoints for user management and RBAC administration.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_client_ip, get_current_user, require_roles
from app.common.schemas import SuccessResponse
from app.core.database import get_db_session
from app.users.models import User, UserRole
from app.users.schemas import UserDetailResponse, UserResponse, UserUpdate
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=SuccessResponse[List[UserResponse]],
    summary="List users (Admin, Investigator, Analyst)",
)
async def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _operator: User = Depends(require_roles(UserRole.ADMIN, UserRole.INVESTIGATOR, UserRole.ANALYST)),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[List[UserResponse]]:
    """Retrieve paginated user accounts."""
    users = await UserService.list_users(db=db, limit=limit, offset=offset, role=role)
    return SuccessResponse(
        data=[UserResponse.model_validate(u) for u in users],
        message="Users retrieved",
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserDetailResponse],
    summary="Get user by ID",
)
async def get_user(
    user_id: str,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[UserDetailResponse]:
    """Retrieve full user profile by ID."""
    user = await UserService.get_user_by_id(db=db, user_id=user_id)
    return SuccessResponse(
        data=UserDetailResponse.model_validate(user),
        message="User details retrieved",
    )


@router.patch(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Update user details (Admin only)",
)
async def update_user(
    user_id: str,
    data: UserUpdate,
    request: Request,
    admin_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[UserResponse]:
    """Modify user role, active status, or name. Restricted to Admin."""
    ip = get_client_ip(request)
    updated = await UserService.update_user(
        db=db,
        user_id=user_id,
        data=data,
        operator_id=admin_user.id,
        ip_address=ip,
    )
    return SuccessResponse(
        data=UserResponse.model_validate(updated),
        message="User updated successfully",
    )
