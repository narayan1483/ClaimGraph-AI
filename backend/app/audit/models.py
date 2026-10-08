"""
ClaimGraph AI — Audit Log Domain Model.

Append-only, tamper-evident audit trail of all security, authentication,
and claim actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.users.models import User


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Immutable audit entry."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "AUTH_LOGIN", "AUTH_REGISTER", "CLAIM_REVIEWED"
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g., "user", "auth", "claim"
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
