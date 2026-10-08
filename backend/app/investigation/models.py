"""
ClaimGraph AI — Investigator & Investigation Record Domain Models.

SQLAlchemy models for investigator profiles and multi-agent AI investigation records.
"""

from __future__ import annotations

from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.users.models import User


class Investigator(Base, UUIDMixin, TimestampMixin):
    """Fraud investigator profile entity."""

    __tablename__ = "investigators"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    badge_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    specialization: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # e.g., "Electronics", "Automotive", "Warranty Fraud"
    cases_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="investigator_profile")


class InvestigationRecord(Base, UUIDMixin, TimestampMixin):
    """Record of an automated AI multi-agent claim investigation."""

    __tablename__ = "investigation_records"

    investigation_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    claim_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Quantitative composite scores
    fraud_score: Mapped[float] = mapped_column(Float, nullable=False)
    graph_score: Mapped[float] = mapped_column(Float, nullable=False)
    final_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)

    # Detailed agent traces & evidence logs
    evidence_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    agent_results_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    score_breakdown_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    investigation_report: Mapped[str] = mapped_column(Text, nullable=False)

    # Human-in-the-loop Adjudication status
    status: Mapped[str] = mapped_column(String(30), default="AWAITING_REVIEW", nullable=False)
    decision: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # APPROVE, REJECT, ESCALATE, REQUEST_MORE_INFO
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
