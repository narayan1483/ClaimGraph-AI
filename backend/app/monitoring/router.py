"""
ClaimGraph AI — Model Monitoring API Router.

Endpoints for real-time model inference metrics and Population Stability Index drift detection.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_active_user
from app.monitoring.service import ModelMonitoringService
from app.users.models import User

router = APIRouter(prefix="/monitoring", tags=["Model Monitoring"])


@router.get("/metrics", summary="Get model inference performance & telemetry")
async def get_monitoring_metrics(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Return model version, prediction count, average score, latency, and drift status."""
    return ModelMonitoringService.get_monitoring_metrics()


@router.get("/drift", summary="Get drift analysis via PSI")
async def get_drift_analysis(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Evaluate distribution shift between baseline training set and production inferences."""
    return ModelMonitoringService.get_drift_analysis()
