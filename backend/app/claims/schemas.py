"""
ClaimGraph AI — Claim & Event Pydantic Schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.claims.models import ClaimStatus, ClaimType
from app.users.schemas import UserResponse


class ProductBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    category: str
    manufacturer: str
    model_number: str
    msrp: float


class DeviceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    serial_number: str
    product_id: str
    customer_id: Optional[str] = None
    product: Optional[ProductBrief] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    status: str


class CustomerBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    risk_score: float
    is_flagged: bool
    user: Optional[UserResponse] = None


class ClaimEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    claim_id: str
    from_status: Optional[str] = None
    to_status: str
    actor_id: Optional[str] = None
    reason: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class ClaimBase(BaseModel):
    customer_id: str
    device_id: str
    claim_type: ClaimType
    claim_amount: float = Field(..., gt=0)
    incident_date: datetime
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=2)
    repair_shop: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdateStatus(BaseModel):
    status: ClaimStatus
    reason: Optional[str] = None


class ClaimResponse(ClaimBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    claim_id: str
    status: ClaimStatus
    fraud_probability: Optional[float] = None
    risk_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ClaimDetailResponse(ClaimResponse):
    customer: Optional[CustomerBrief] = None
    device: Optional[DeviceBrief] = None
    events: List[ClaimEventResponse] = []
