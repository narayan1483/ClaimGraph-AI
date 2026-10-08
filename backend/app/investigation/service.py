"""
ClaimGraph AI — Investigation Service.

Orchestrates multi-agent AI execution, results persistence, and human decision workflows.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.state import InvestigationState
from app.agents.workflow import run_investigation_workflow
from app.audit.service import AuditService
from app.claims.models import Claim, ClaimEvent, ClaimStatus
from app.claims.repository import ClaimRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.core.kafka import (
    TOPIC_AI_INVESTIGATION_COMPLETED,
    TOPIC_CLAIM_APPROVED,
    TOPIC_CLAIM_REJECTED,
    TOPIC_CLAIM_REVIEWED,
    publish_kafka_event,
)
from app.customers.models import Customer
from app.devices.models import Device
from app.graph.service import KnowledgeGraphService
from app.investigation.models import InvestigationRecord
from app.investigation.schemas import (
    InvestigationDecisionRequest,
    InvestigationDecisionResponse,
    InvestigationRunResponse,
)

logger = logging.getLogger("claimgraph.investigation")


class InvestigationService:
    """Manages AI multi-agent investigations and human investigator adjudication."""

    @classmethod
    async def run_investigation(
        cls,
        db: AsyncSession,
        claim_identifier: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> InvestigationRunResponse:
        """Execute full 8-agent LangGraph investigation pipeline on a claim."""
        # 1. Fetch Claim
        if claim_identifier.upper().startswith("CLM-"):
            claim = await ClaimRepository.get_by_claim_id(db, claim_identifier)
        else:
            claim = await ClaimRepository.get_by_id(db, claim_identifier)

        if not claim:
            raise NotFoundError("Claim", claim_identifier)

        # 2. Fetch Customer and Device
        stmt_cust = select(Customer).options(selectinload(Customer.user)).where(Customer.id == claim.customer_id)
        cust_res = await db.execute(stmt_cust)
        customer = cust_res.scalar_one_or_none()

        stmt_dev = select(Device).options(selectinload(Device.product)).where(Device.id == claim.device_id)
        dev_res = await db.execute(stmt_dev)
        device = dev_res.scalar_one_or_none()

        # Count prior claims
        count_stmt = select(func.count(Claim.id)).where(
            Claim.customer_id == claim.customer_id, Claim.id != claim.id
        )
        prior_claims_count = (await db.execute(count_stmt)).scalar() or 0

        # Sync to graph first
        graph_svc = KnowledgeGraphService.get_instance()
        cust_name = customer.user.full_name if (customer and customer.user) else "Unknown Claimant"
        cust_email = customer.user.email if (customer and customer.user) else "claimant@example.com"
        dev_serial = device.serial_number if device else "SN-DEV-001"
        prod_name = device.product.name if (device and device.product) else "Consumer Electronic Unit"

        await graph_svc.sync_claim_entities(
            claim_id=claim.claim_id,
            customer_id=claim.customer_id,
            customer_name=cust_name,
            device_id=claim.device_id,
            device_serial=dev_serial,
            product_name=prod_name,
            claim_type=claim.claim_type.value if hasattr(claim.claim_type, "value") else str(claim.claim_type),
            claim_amount=claim.claim_amount,
            location_name=claim.location or "North American Region",
            repair_shop_name=claim.repair_shop,
            customer_email=cust_email,
        )

        # Build initial LangGraph state
        initial_state: InvestigationState = {
            "claim_id": claim.claim_id,
            "claim_data": {
                "claim_id": claim.claim_id,
                "claim_amount": claim.claim_amount,
                "claim_type": claim.claim_type.value if hasattr(claim.claim_type, "value") else str(claim.claim_type),
                "incident_date": claim.incident_date.isoformat(),
                "description": claim.description,
                "location": claim.location,
                "repair_shop": claim.repair_shop,
            },
            "customer_data": {
                "customer_id": claim.customer_id,
                "full_name": cust_name,
                "email": cust_email,
                "account_age_days": 180,
            },
            "device_data": {
                "device_id": claim.device_id,
                "serial_number": dev_serial,
                "product_name": prod_name,
                "purchase_price": device.purchase_price if device else 1000.0,
            },
            "prior_claims_count": prior_claims_count,
            "agent_results": {},
            "errors": [],
            "retry_counts": {},
        }

        # 3. Run multi-agent LangGraph workflow
        final_state = await run_investigation_workflow(initial_state)

        # 4. Create and persist InvestigationRecord
        inv_code = f"INV-2026-{uuid.uuid4().hex[:8].upper()}"
        inv_record = InvestigationRecord(
            investigation_id=inv_code,
            claim_id=claim.claim_id,
            fraud_score=final_state.get("ml_fraud_prob", 0.1),
            graph_score=final_state.get("graph_risk_score", 0.1),
            final_risk_score=final_state.get("final_risk_score", 0.15),
            risk_level=final_state.get("risk_level", "LOW"),
            recommendation=final_state.get("recommended_action", "NORMAL_PROCESSING"),
            evidence_json=final_state.get("categorized_evidence", []),
            agent_results_json=final_state.get("agent_results", {}),
            score_breakdown_json=final_state.get("score_breakdown", {}),
            investigation_report=final_state.get("investigation_report", "Report generated."),
            status="AWAITING_REVIEW",
        )
        db.add(inv_record)

        # 5. Update claim attributes
        claim.fraud_probability = final_state.get("ml_fraud_prob")
        claim.risk_level = final_state.get("risk_level")

        if final_state.get("risk_level") in ["HIGH", "CRITICAL"]:
            claim.status = ClaimStatus.FLAGGED_INVESTIGATION

        await db.commit()
        await db.refresh(inv_record)

        # 6. Audit Trail
        await AuditService.log_event(
            db=db,
            action="INVESTIGATION_COMPLETED",
            entity_type="investigation",
            user_id=actor_id,
            entity_id=inv_record.id,
            details={
                "investigation_id": inv_code,
                "claim_id": claim.claim_id,
                "final_risk_score": inv_record.final_risk_score,
                "risk_level": inv_record.risk_level,
                "recommendation": inv_record.recommendation,
            },
            ip_address=ip_address,
        )

        # 7. Asynchronous Kafka Event Notification
        await publish_kafka_event(
            TOPIC_AI_INVESTIGATION_COMPLETED,
            {
                "investigation_id": inv_code,
                "claim_id": claim.claim_id,
                "final_risk_score": inv_record.final_risk_score,
                "risk_level": inv_record.risk_level,
                "recommendation": inv_record.recommendation,
                "timestamp": inv_record.created_at.isoformat() if inv_record.created_at else None,
            },
        )

        return InvestigationRunResponse(
            investigation_id=inv_record.investigation_id,
            claim_id=inv_record.claim_id,
            fraud_score=inv_record.fraud_score,
            graph_score=inv_record.graph_score,
            final_risk_score=inv_record.final_risk_score,
            risk_level=inv_record.risk_level,
            recommendation=inv_record.recommendation,
            evidence=inv_record.evidence_json,
            agent_results=inv_record.agent_results_json,
            investigation_report=inv_record.investigation_report,
            score_breakdown=inv_record.score_breakdown_json,
            status=inv_record.status,
        )

    @classmethod
    async def get_investigation(cls, db: AsyncSession, claim_identifier: str) -> Optional[InvestigationRunResponse]:
        """Fetch latest investigation for a claim."""
        stmt = (
            select(InvestigationRecord)
            .where(InvestigationRecord.claim_id == claim_identifier)
            .order_by(InvestigationRecord.created_at.desc())
        )
        res = await db.execute(stmt)
        record = res.scalars().first()
        if not record:
            return None

        return InvestigationRunResponse(
            investigation_id=record.investigation_id,
            claim_id=record.claim_id,
            fraud_score=record.fraud_score,
            graph_score=record.graph_score,
            final_risk_score=record.final_risk_score,
            risk_level=record.risk_level,
            recommendation=record.recommendation,
            evidence=record.evidence_json,
            agent_results=record.agent_results_json,
            investigation_report=record.investigation_report,
            score_breakdown=record.score_breakdown_json,
            status=record.status,
        )

    @classmethod
    async def record_decision(
        cls,
        db: AsyncSession,
        investigation_id: str,
        payload: InvestigationDecisionRequest,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> InvestigationDecisionResponse:
        """Record human investigator adjudication decision."""
        # Find record
        stmt = select(InvestigationRecord).where(InvestigationRecord.investigation_id == investigation_id)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise NotFoundError("Investigation", investigation_id)

        # Find associated claim
        claim = await ClaimRepository.get_by_claim_id(db, record.claim_id)
        if not claim:
            raise NotFoundError("Claim", record.claim_id)

        decision_upper = payload.decision.upper()
        status_map = {
            "APPROVE": ClaimStatus.APPROVED,
            "REJECT": ClaimStatus.REJECTED,
            "ESCALATE": ClaimStatus.ESCALATED,
            "REQUEST_MORE_INFO": ClaimStatus.UNDER_REVIEW,
        }

        if decision_upper not in status_map:
            raise ValidationError(f"Invalid decision '{payload.decision}'. Must be one of: {list(status_map.keys())}")

        new_status = status_map[decision_upper]
        old_status = claim.status.value if hasattr(claim.status, "value") else str(claim.status)

        # Update record
        record.decision = decision_upper
        record.decision_notes = payload.notes
        record.status = "RESOLVED"
        record.decided_by_id = actor_id
        record.decided_at = datetime.now(timezone.utc)

        # Update claim
        claim.status = new_status

        # Create ClaimEvent
        event = ClaimEvent(
            claim_id=claim.id,
            from_status=old_status,
            to_status=new_status.value,
            actor_id=actor_id,
            reason=f"Human investigator decision: {decision_upper}. Notes: {payload.notes or 'None'}",
        )
        db.add(event)

        await db.commit()

        # Audit
        await AuditService.log_event(
            db=db,
            action=f"CLAIM_DECIDED_{decision_upper}",
            entity_type="claim",
            user_id=actor_id,
            entity_id=claim.id,
            details={
                "investigation_id": investigation_id,
                "decision": decision_upper,
                "notes": payload.notes,
                "badge_number": payload.badge_number,
            },
            ip_address=ip_address,
        )

        # Asynchronous Kafka Event Notifications
        review_payload = {
            "investigation_id": investigation_id,
            "claim_id": claim.claim_id,
            "decision": decision_upper,
            "decided_by_id": actor_id,
            "new_status": new_status.value,
        }
        await publish_kafka_event(TOPIC_CLAIM_REVIEWED, review_payload)
        if decision_upper == "APPROVE":
            await publish_kafka_event(TOPIC_CLAIM_APPROVED, review_payload)
        elif decision_upper == "REJECT":
            await publish_kafka_event(TOPIC_CLAIM_REJECTED, review_payload)

        return InvestigationDecisionResponse(
            investigation_id=record.investigation_id,
            claim_id=claim.claim_id,
            decision=decision_upper,
            new_claim_status=new_status.value,
            message=f"Investigation {investigation_id} adjudicated as {decision_upper}.",
            decided_at=record.decided_at.isoformat(),
        )
