"""
ClaimGraph AI — User & Organization Repository.

Database access abstraction for User, Organization, Customer, and Investigator entities.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.customers.models import Customer
from app.investigation.models import Investigator
from app.users.models import Organization, User, UserRole


class UserRepository:
    """Repository handling database queries for User and profiles."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str, with_profiles: bool = False) -> Optional[User]:
        """Fetch user by primary key."""
        stmt = select(User).where(User.id == user_id)
        if with_profiles:
            stmt = stmt.options(
                selectinload(User.customer_profile),
                selectinload(User.investigator_profile),
                selectinload(User.organization),
            )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str, with_profiles: bool = False) -> Optional[User]:
        """Fetch user by unique email address."""
        stmt = select(User).where(User.email == email.lower().strip())
        if with_profiles:
            stmt = stmt.options(
                selectinload(User.customer_profile),
                selectinload(User.investigator_profile),
                selectinload(User.organization),
            )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.CUSTOMER,
        organization_id: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
    ) -> User:
        """Insert a new user record."""
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role,
            organization_id=organization_id,
            is_active=is_active,
            is_verified=is_verified,
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def list_users(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        role: Optional[UserRole] = None,
        organization_id: Optional[str] = None,
    ) -> List[User]:
        """List users with optional role and organization filters."""
        stmt = select(User).order_by(User.created_at.desc())
        if role:
            stmt = stmt.where(User.role == role)
        if organization_id:
            stmt = stmt.where(User.organization_id == organization_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_customer_profile(
        db: AsyncSession,
        user_id: str,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: str = "US",
    ) -> Customer:
        """Create a customer profile for a user."""
        profile = Customer(
            user_id=user_id,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        db.add(profile)
        await db.flush()
        return profile

    @staticmethod
    async def create_investigator_profile(
        db: AsyncSession,
        user_id: str,
        badge_number: Optional[str] = None,
        specialization: Optional[str] = None,
    ) -> Investigator:
        """Create an investigator profile for a user."""
        profile = Investigator(
            user_id=user_id,
            badge_number=badge_number,
            specialization=specialization,
        )
        db.add(profile)
        await db.flush()
        return profile


class OrganizationRepository:
    """Repository handling database queries for multi-tenant organizations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, org_id: str) -> Optional[Organization]:
        """Fetch organization by primary key."""
        stmt = select(Organization).where(Organization.id == org_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Organization]:
        """Fetch organization by unique slug."""
        stmt = select(Organization).where(Organization.slug == slug.lower().strip())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_organization(
        db: AsyncSession,
        name: str,
        slug: str,
        description: Optional[str] = None,
    ) -> Organization:
        """Insert a new organization record."""
        org = Organization(
            name=name.strip(),
            slug=slug.lower().strip(),
            description=description,
        )
        db.add(org)
        await db.flush()
        return org
