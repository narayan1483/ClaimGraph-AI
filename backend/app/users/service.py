"""
ClaimGraph AI — User Management Service.

Business logic for user onboarding, profile association, and role administration.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.users.models import User, UserRole
from app.users.repository import OrganizationRepository, UserRepository
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    """Service providing user management business workflows."""

    @staticmethod
    async def create_user(
        db: AsyncSession,
        data: UserCreate,
        operator_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> User:
        """Register a new user, ensuring email uniqueness and profile seeding."""
        existing = await UserRepository.get_by_email(db, data.email)
        if existing:
            raise ConflictError(f"User with email '{data.email}' already exists.")

        if data.organization_id:
            org = await OrganizationRepository.get_by_id(db, data.organization_id)
            if not org:
                raise NotFoundError("Organization", data.organization_id)

        hashed = hash_password(data.password)
        user = await UserRepository.create_user(
            db=db,
            email=data.email,
            hashed_password=hashed,
            full_name=data.full_name,
            role=data.role,
            organization_id=data.organization_id,
        )

        # Auto-create associated profile based on role
        if data.role == UserRole.CUSTOMER:
            await UserRepository.create_customer_profile(db=db, user_id=user.id)
        elif data.role == UserRole.INVESTIGATOR:
            await UserRepository.create_investigator_profile(db=db, user_id=user.id)

        # Audit log creation
        await AuditService.log_event(
            db=db,
            action="USER_CREATED",
            entity_type="user",
            user_id=operator_id or user.id,
            entity_id=user.id,
            details={"email": user.email, "role": user.role.value},
            ip_address=ip_address,
        )

        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
        """Retrieve user with full profile relationships."""
        user = await UserRepository.get_by_id(db, user_id, with_profiles=True)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    @staticmethod
    async def list_users(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        role: Optional[UserRole] = None,
    ) -> List[User]:
        """Fetch list of users."""
        return await UserRepository.list_users(db, limit=limit, offset=offset, role=role)

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: str,
        data: UserUpdate,
        operator_id: str,
        ip_address: Optional[str] = None,
    ) -> User:
        """Update user attributes with audit logging."""
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)

        changes = {}
        if data.full_name is not None and data.full_name != user.full_name:
            changes["full_name"] = {"old": user.full_name, "new": data.full_name}
            user.full_name = data.full_name
        if data.role is not None and data.role != user.role:
            changes["role"] = {"old": user.role.value, "new": data.role.value}
            user.role = data.role
        if data.is_active is not None and data.is_active != user.is_active:
            changes["is_active"] = {"old": user.is_active, "new": data.is_active}
            user.is_active = data.is_active

        if changes:
            await AuditService.log_event(
                db=db,
                action="USER_UPDATED",
                entity_type="user",
                user_id=operator_id,
                entity_id=user.id,
                details=changes,
                ip_address=ip_address,
            )

        return user
