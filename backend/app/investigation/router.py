"""
ClaimGraph AI — Investigation API Router.

Endpoints for triggering AI multi-agent investigations and recording human investigator decisions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_optional, require_roles
from app.core.database import get_db
from app.investigation.schemas import (
    InvestigationDecisionRequest,
    InvestigationDecisionResponse,
    InvestigationRunResponse,
)
from app.investigation.service import InvestigationService
from app.users.models import User, UserRole

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post("/{claim_id}/run", response_model=InvestigationRunResponse)
async def run_claim_investigation(
    claim_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> InvestigationRunResponse:
    """
    Trigger complete LangGraph AI multi-agent investigation on a claim.
    Executes:
    Claim Understanding -> Document Analysis -> Vision Analysis ->
    ML Fraud Analysis -> Graph Investigation -> Policy/RAG ->
    Risk Aggregation -> Investigation Report -> Human Review Checkpoint.
    """
    actor_id = current_user.id if current_user else None
    ip_addr = request.client.host if request.client else None

    result = await InvestigationService.run_investigation(
        db=db,
        claim_identifier=claim_id,
        actor_id=actor_id,
        ip_address=ip_addr,
    )
    return result


@router.get("/{claim_id}", response_model=InvestigationRunResponse)
async def get_claim_investigation(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> InvestigationRunResponse:
    """Retrieve existing investigation report and multi-agent findings for a claim."""
    result = await InvestigationService.get_investigation(db=db, claim_identifier=claim_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No investigation record found for claim '{claim_id}'. Run an investigation first.",
        )
    return result


@router.post("/{investigation_id}/decision", response_model=InvestigationDecisionResponse)
async def adjudicate_investigation(
    investigation_id: str,
    payload: InvestigationDecisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> InvestigationDecisionResponse:
    """
    Record mandatory human investigator adjudication decision (APPROVE, REJECT, ESCALATE, REQUEST_MORE_INFO).
    Updates claim state and logs permanent audit trail.
    """
    actor_id = current_user.id if current_user else None
    ip_addr = request.client.host if request.client else None

    return await InvestigationService.record_decision(
        db=db,
        investigation_id=investigation_id,
        payload=payload,
        actor_id=actor_id,
        ip_address=ip_addr,
    )
