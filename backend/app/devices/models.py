"""
ClaimGraph AI — Product & Device Domain Models.

SQLAlchemy models for catalog products and insured customer devices/assets.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.customers.models import Customer
    from app.claims.models import Claim


class Product(Base, UUIDMixin, TimestampMixin):
    """Insured product catalog entity (phone, laptop, automobile part, etc.)."""

    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Electronics, Auto, Appliances
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    msrp: Mapped[float] = mapped_column(Float, nullable=False)
    warranty_period_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)

    # Relationships
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="product")


class Device(Base, UUIDMixin, TimestampMixin):
    """Specific physical device or insured asset identified by serial number."""

    __tablename__ = "devices"

    serial_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, REPLACED, FLAGGED

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="devices")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="devices")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="device")
