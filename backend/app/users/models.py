"""
ClaimGraph AI — User & Organization Domain Models.

SQLAlchemy models for multi-tenant organizations, users, and RBAC roles.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.customers.models import Customer
    from app.investigation.models import Investigator
    from app.audit.models import AuditLog


class UserRole(str, enum.Enum):
    """Enterprise Role-Based Access Control personas."""

    ADMIN = "ADMIN"
    INVESTIGATOR = "INVESTIGATOR"
    ANALYST = "ANALYST"
    CUSTOMER = "CUSTOMER"


class Organization(Base, UUIDMixin, TimestampMixin):
    """Multi-tenant organization entity."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")


class User(Base, UUIDMixin, TimestampMixin):
    """Core platform user entity."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20),
        default=UserRole.CUSTOMER,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Tenant association (nullable for global admins or standalone users)
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    customer_profile: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    investigator_profile: Mapped[Optional["Investigator"]] = relationship(
        "Investigator", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
