"""
ClaimGraph AI — Audit Logs Router.

Protected endpoints for viewing the system audit trail.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.schemas import AuditLogResponse
from app.audit.service import AuditService
from app.auth.dependencies import require_roles
from app.common.schemas import SuccessResponse
from app.core.database import get_db_session
from app.users.models import User, UserRole

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "/logs",
    response_model=SuccessResponse[List[AuditLogResponse]],
    summary="List audit events (Admin & Investigator only)",
)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by event action"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _operator: User = Depends(require_roles(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[List[AuditLogResponse]]:
    """Retrieve immutable audit log records."""
    logs = await AuditService.get_recent_logs(db=db, limit=limit, offset=offset, action=action)
    return SuccessResponse(
        data=[AuditLogResponse.model_validate(log) for log in logs],
        message="Audit logs retrieved",
    )
