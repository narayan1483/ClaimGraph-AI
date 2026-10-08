"""
ClaimGraph AI — Claim & ClaimEvent Domain Models.

SQLAlchemy models for claims lifecycle, risk predictions, and state transition audit logs.
"""

from __future__ import annotations

from datetime import datetime, timezone
import enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.customers.models import Customer
    from app.devices.models import Device


class ClaimStatus(str, enum.Enum):
    """Enterprise claim lifecycle states."""

    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    FLAGGED_INVESTIGATION = "FLAGGED_INVESTIGATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class ClaimType(str, enum.Enum):
    """Types of insurance / warranty claims."""

    DAMAGE = "DAMAGE"
    THEFT = "THEFT"
    MALFUNCTION = "MALFUNCTION"
    LOSS = "LOSS"
    WARRANTY_REPAIR = "WARRANTY_REPAIR"


class Claim(Base, UUIDMixin, TimestampMixin):
    """Core insurance/warranty claim entity."""

    __tablename__ = "claims"

    claim_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim_type: Mapped[ClaimType] = mapped_column(
        Enum(ClaimType, native_enum=False, length=30), nullable=False, index=True
    )
    claim_amount: Mapped[float] = mapped_column(Float, nullable=False)
    incident_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    repair_shop: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)

    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus, native_enum=False, length=30),
        default=ClaimStatus.SUBMITTED,
        nullable=False,
        index=True,
    )

    # ML & Risk signals cache
    fraud_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="claims")
    device: Mapped["Device"] = relationship("Device", back_populates="claims")
    events: Mapped[List["ClaimEvent"]] = relationship(
        "ClaimEvent", back_populates="claim", cascade="all, delete-orphan", order_by="ClaimEvent.created_at.asc()"
    )


class ClaimEvent(Base, UUIDMixin):
    """Immutable log of claim state transitions and investigator interventions."""

    __tablename__ = "claim_events"

    claim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # User ID of operator/investigator
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    claim: Mapped["Claim"] = relationship("Claim", back_populates="events")
