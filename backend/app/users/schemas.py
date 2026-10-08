"""
ClaimGraph AI — User Schemas.

Pydantic schemas for User, Organization, Customer, and Investigator entities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.users.models import UserRole


# ── Organization Schemas ──────────────────────────────────────────

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime


# ── Customer Profile Schemas ─────────────────────────────────────

class CustomerProfileBase(BaseModel):
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "US"


class CustomerProfileResponse(CustomerProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    risk_score: float
    is_flagged: bool


# ── Investigator Profile Schemas ─────────────────────────────────

class InvestigatorProfileBase(BaseModel):
    badge_number: Optional[str] = None
    specialization: Optional[str] = None


class InvestigatorProfileResponse(InvestigatorProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    cases_resolved: int


# ── User Schemas ──────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.CUSTOMER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)
    organization_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    organization_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserDetailResponse(UserResponse):
    customer_profile: Optional[CustomerProfileResponse] = None
    investigator_profile: Optional[InvestigatorProfileResponse] = None
    organization: Optional[OrganizationResponse] = None
