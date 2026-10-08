"""
ClaimGraph AI — Customer Domain Model.

Policyholder / claimant profile linked to a User account.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.users.models import User
    from app.devices.models import Device
    from app.claims.models import Claim


class Customer(Base, UUIDMixin, TimestampMixin):
    """Customer / policyholder entity."""

    __tablename__ = "customers"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="US", nullable=False)

    # Initial risk & compliance flags
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer_profile")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="customer")
    claims: Mapped[list["Claim"]] = relationship("Claim", back_populates="customer")
