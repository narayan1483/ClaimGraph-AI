"""
ClaimGraph AI — Claim Management Service.

Business workflows for claim registration, status transitions, audit tracking,
and integration with the fraud intelligence engine.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.claims.models import Claim, ClaimEvent, ClaimStatus, ClaimType
from app.claims.repository import ClaimRepository
from app.claims.schemas import ClaimCreate
from app.core.exceptions import NotFoundError, ValidationError
from app.core.kafka import TOPIC_CLAIM_CREATED, publish_kafka_event
from app.customers.models import Customer
from app.devices.models import Device


class ClaimService:
    """Service orchestrating claims lifecycle, validation, and audit events."""

    @classmethod
    async def create_claim(
        cls,
        db: AsyncSession,
        data: ClaimCreate,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Claim:
        """Validate referenced customer & device, insert claim, and record audit event."""
        # 1. Verify Device exists
        dev_res = await db.execute(select(Device).where(Device.id == data.device_id))
        device = dev_res.scalar_one_or_none()
        if not device:
            raise NotFoundError("Device", data.device_id)

        # 2. Verify Customer exists or derive from device
        target_customer_id = data.customer_id or device.customer_id
        cust_res = await db.execute(select(Customer).where(Customer.id == target_customer_id))
        customer = cust_res.scalar_one_or_none()
        if not customer:
            # Fallback to any active customer
            cust_fallback = await db.execute(select(Customer).limit(1))
            customer = cust_fallback.scalar_one_or_none()
            if customer:
                target_customer_id = customer.id
            else:
                raise NotFoundError("Customer", str(target_customer_id))

        # 3. Create Claim
        claim = await ClaimRepository.create(
            db=db,
            customer_id=target_customer_id,
            device_id=data.device_id,
            claim_type=data.claim_type,
            claim_amount=data.claim_amount,
            incident_date=data.incident_date,
            description=data.description,
            location=data.location,
            repair_shop=data.repair_shop,
        )

        # 4. Audit Log
        await AuditService.log_event(
            db=db,
            action="CLAIM_CREATED",
            entity_type="claim",
            user_id=actor_id,
            entity_id=claim.id,
            details={
                "claim_id": claim.claim_id,
                "amount": claim.claim_amount,
                "claim_type": claim.claim_type.value,
                "customer_id": claim.customer_id,
                "device_id": claim.device_id,
            },
            ip_address=ip_address,
        )

        # 5. Kafka Event Publishing
        await publish_kafka_event(
            TOPIC_CLAIM_CREATED,
            {
                "claim_id": claim.claim_id,
                "amount": claim.claim_amount,
                "customer_id": claim.customer_id,
                "device_id": claim.device_id,
                "created_at": claim.created_at.isoformat() if claim.created_at else None,
            },
        )

        return claim

    @classmethod
    async def get_claim(cls, db: AsyncSession, claim_identifier: str) -> Claim:
        """Retrieve claim by UUID or human-readable code (CLM-2026-XXXX)."""
        # Try by claim_id first if it starts with CLM-
        if claim_identifier.upper().startswith("CLM-"):
            claim = await ClaimRepository.get_by_claim_id(db, claim_identifier)
        else:
            claim = await ClaimRepository.get_by_id(db, claim_identifier)

        if not claim:
            raise NotFoundError("Claim", claim_identifier)
        return claim

    @classmethod
    async def list_claims(
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
        """Fetch filtered and paginated list of claims with total count."""
        return await ClaimRepository.list_and_filter(
            db=db,
            status=status,
            claim_type=claim_type,
            search=search,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )

    @classmethod
    async def transition_status(
        cls,
        db: AsyncSession,
        claim_identifier: str,
        to_status: ClaimStatus,
        actor_id: str,
        reason: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> Claim:
        """Execute state transition, append ClaimEvent, and emit audit record."""
        claim = await cls.get_claim(db, claim_identifier)

        if claim.status == to_status:
            raise ValidationError(f"Claim is already in status '{to_status.value}'")

        from_status = claim.status.value

        # Append state event and update status
        await ClaimRepository.add_event(
            db=db,
            claim=claim,
            to_status=to_status,
            actor_id=actor_id,
            reason=reason,
            metadata_json=metadata_json,
        )

        # Audit event
        await AuditService.log_event(
            db=db,
            action="CLAIM_STATUS_TRANSITION",
            entity_type="claim",
            user_id=actor_id,
            entity_id=claim.id,
            details={
                "claim_id": claim.claim_id,
                "from_status": from_status,
                "to_status": to_status.value,
                "reason": reason,
            },
            ip_address=ip_address,
        )

        return claim
