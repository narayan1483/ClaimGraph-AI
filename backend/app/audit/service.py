"""
ClaimGraph AI — Audit Log Service.

Records security and domain events to the audit_logs table and structured loggers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for appending and querying audit records."""

    @staticmethod
    async def log_event(
        db: AsyncSession,
        action: str,
        entity_type: str,
        user_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log_entry)
        await db.flush()

        logger.info(
            "audit_event_logged",
            action=action,
            entity_type=entity_type,
            user_id=user_id,
            entity_id=entity_id,
        )
        return log_entry

    @staticmethod
    async def get_recent_logs(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        """Fetch audit log records ordered by creation date descending."""
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
        if action:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())
