"""
ClaimGraph AI — Claims API Router.

Endpoints for claim submission, query filtering, state transitions, and fraud evaluation.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_client_ip, get_current_user, require_roles
from app.claims.models import ClaimStatus, ClaimType
from app.claims.schemas import (
    ClaimCreate,
    ClaimDetailResponse,
    ClaimResponse,
    ClaimUpdateStatus,
)
from app.claims.service import ClaimService
from app.common.schemas import PaginatedResponse, SuccessResponse
from app.core.database import get_db_session
from app.users.models import User, UserRole

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post(
    "",
    response_model=SuccessResponse[ClaimResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new claim",
)
async def create_claim(
    data: ClaimCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ClaimResponse]:
    """Register a new warranty or insurance claim."""
    ip = get_client_ip(request)
    claim = await ClaimService.create_claim(
        db=db,
        data=data,
        actor_id=current_user.id,
        ip_address=ip,
    )
    return SuccessResponse(
        data=ClaimResponse.model_validate(claim),
        message=f"Claim '{claim.claim_id}' created successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[ClaimResponse],
    summary="List and filter claims",
)
async def list_claims(
    status: Optional[ClaimStatus] = Query(None, description="Filter by status"),
    claim_type: Optional[ClaimType] = Query(None, description="Filter by claim type"),
    search: Optional[str] = Query(None, description="Search by ID, location, description, or repair shop"),
    date_from: Optional[datetime] = Query(None, description="Filter incident date from"),
    date_to: Optional[datetime] = Query(None, description="Filter incident date to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse[ClaimResponse]:
    """Retrieve paginated claims with multifaceted filtering."""
    offset = (page - 1) * page_size
    claims, total = await ClaimService.list_claims(
        db=db,
        status=status,
        claim_type=claim_type,
        search=search,
        date_from=date_from,
        date_to=date_to,
        limit=page_size,
        offset=offset,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        data=[ClaimResponse.model_validate(c) for c in claims],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{claim_identifier}",
    response_model=SuccessResponse[ClaimDetailResponse],
    summary="Get claim details",
)
async def get_claim(
    claim_identifier: str,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ClaimDetailResponse]:
    """Retrieve full claim dossier including customer, device, and event history."""
    claim = await ClaimService.get_claim(db, claim_identifier)
    return SuccessResponse(
        data=ClaimDetailResponse.model_validate(claim),
        message="Claim retrieved successfully",
    )


@router.patch(
    "/{claim_identifier}/status",
    response_model=SuccessResponse[ClaimDetailResponse],
    summary="Transition claim status (Investigator / Admin)",
)
async def transition_claim_status(
    claim_identifier: str,
    data: ClaimUpdateStatus,
    request: Request,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ClaimDetailResponse]:
    """Execute lifecycle transition (UNDER_REVIEW, APPROVED, REJECTED, FLAGGED_INVESTIGATION)."""
    ip = get_client_ip(request)
    claim = await ClaimService.transition_status(
        db=db,
        claim_identifier=claim_identifier,
        to_status=data.status,
        actor_id=current_user.id,
        reason=data.reason,
        ip_address=ip,
    )
    # Reload with full relations
    detailed = await ClaimService.get_claim(db, claim.id)
    return SuccessResponse(
        data=ClaimDetailResponse.model_validate(detailed),
        message=f"Claim status updated to '{data.status.value}'",
    )
