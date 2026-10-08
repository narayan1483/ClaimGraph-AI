"""
ClaimGraph AI — Analytics API Router.

Serves enterprise dashboard metrics, aggregated claims statistics,
risk distribution, and recent investigation feeds.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.service import AnalyticsService
from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.users.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])


@router.get("/dashboard", summary="Enterprise dashboard metrics")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve operational dashboard cards, distributions, high risk claims, and trends."""
    return await AnalyticsService.get_dashboard_summary(db=db)
