"""
ClaimGraph AI — Claim & Event Repository.

Database operations for claims management, filtering, searching, and event history.
"""

from __future__ import annotations

from datetime import datetime, timezone
import random
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.claims.models import Claim, ClaimEvent, ClaimStatus, ClaimType
from app.customers.models import Customer
from app.devices.models import Device, Product


class ClaimRepository:
    """Repository handling all database queries for Claim and ClaimEvent entities."""

    @staticmethod
    def generate_claim_code() -> str:
        """Generate human-readable claim identifier: CLM-2026-XXXX."""
        year = datetime.now(timezone.utc).year
        seq = random.randint(1000, 9999)
        return f"CLM-{year}-{seq}"

    @classmethod
    async def get_by_id(
        cls, db: AsyncSession, claim_pk: str, with_relations: bool = True
    ) -> Optional[Claim]:
        """Fetch claim by internal primary key UUID."""
        stmt = select(Claim).where(Claim.id == claim_pk)
        if with_relations:
            stmt = stmt.options(
                selectinload(Claim.customer).selectinload(Customer.user),
                selectinload(Claim.device).selectinload(Device.product),
                selectinload(Claim.events),
            )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_claim_id(
        cls, db: AsyncSession, claim_id: str, with_relations: bool = True
    ) -> Optional[Claim]:
        """Fetch claim by human-readable claim code (e.g. CLM-2026-1234)."""
        stmt = select(Claim).where(Claim.claim_id == claim_id.strip().upper())
        if with_relations:
            stmt = stmt.options(
                selectinload(Claim.customer).selectinload(Customer.user),
                selectinload(Claim.device).selectinload(Device.product),
                selectinload(Claim.events),
            )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        customer_id: str,
        device_id: str,
        claim_type: ClaimType,
        claim_amount: float,
        incident_date: datetime,
        description: str,
        location: str,
        repair_shop: Optional[str] = None,
        custom_claim_id: Optional[str] = None,
    ) -> Claim:
        """Create a new Claim and log initial SUBMITTED event."""
        claim_code = custom_claim_id or cls.generate_claim_code()

        claim = Claim(
            claim_id=claim_code,
            customer_id=customer_id,
            device_id=device_id,
            claim_type=claim_type,
            claim_amount=claim_amount,
            incident_date=incident_date,
            description=description,
            location=location,
            repair_shop=repair_shop,
            status=ClaimStatus.SUBMITTED,
        )
        db.add(claim)
        await db.flush()

        # Initial event entry
        event = ClaimEvent(
            claim_id=claim.id,
            from_status=None,
            to_status=ClaimStatus.SUBMITTED.value,
            reason="Claim submitted",
        )
        db.add(event)
        await db.flush()

        return claim

    @classmethod
    async def list_and_filter(
        cls,
        db: AsyncSession,
        status: Optional[ClaimStatus] = None,
        claim_type: Optional[ClaimType] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Claim], int]:
        """Query claims with filtering, keyword search, and total count."""
        stmt = select(Claim).options(
            selectinload(Claim.customer).selectinload(Customer.user),
            selectinload(Claim.device).selectinload(Device.product),
        )
        count_stmt = select(func.count()).select_from(Claim)

        # Filters
        if status:
            stmt = stmt.where(Claim.status == status)
            count_stmt = count_stmt.where(Claim.status == status)

        if claim_type:
            stmt = stmt.where(Claim.claim_type == claim_type)
            count_stmt = count_stmt.where(Claim.claim_type == claim_type)

        if date_from:
            stmt = stmt.where(Claim.incident_date >= date_from)
            count_stmt = count_stmt.where(Claim.incident_date >= date_from)

        if date_to:
            stmt = stmt.where(Claim.incident_date <= date_to)
            count_stmt = count_stmt.where(Claim.incident_date <= date_to)

        if search:
            search_pattern = f"%{search.strip()}%"
            filter_cond = or_(
                Claim.claim_id.ilike(search_pattern),
                Claim.location.ilike(search_pattern),
                Claim.description.ilike(search_pattern),
                Claim.repair_shop.ilike(search_pattern),
            )
            stmt = stmt.where(filter_cond)
            count_stmt = count_stmt.where(filter_cond)

        stmt = stmt.order_by(Claim.created_at.desc()).limit(limit).offset(offset)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        results = await db.execute(stmt)
        claims = list(results.scalars().all())

        return claims, total

    @classmethod
    async def add_event(
        cls,
        db: AsyncSession,
        claim: Claim,
        to_status: ClaimStatus,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> ClaimEvent:
        """Transition claim state and append an immutable ClaimEvent audit log."""
        from_status = claim.status.value
        claim.status = to_status

        event = ClaimEvent(
            claim_id=claim.id,
            from_status=from_status,
            to_status=to_status.value,
            actor_id=actor_id,
            reason=reason,
            metadata_json=metadata_json,
        )
        db.add(event)
        await db.flush()
        try:
            await db.refresh(claim, ["events"])
        except Exception:
            pass
        return event

    @classmethod
    async def update_risk_prediction(
        cls,
        db: AsyncSession,
        claim: Claim,
        fraud_probability: float,
        risk_level: str,
    ) -> Claim:
        """Update cached ML fraud probability and risk score on the claim."""
        claim.fraud_probability = fraud_probability
        claim.risk_level = risk_level
        await db.flush()
        return claim
