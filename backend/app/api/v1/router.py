"""
ClaimGraph AI — API v1 Router.

Aggregates all v1 sub-routers under the /api/v1 prefix.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.audit.router import router as audit_router
from app.claims.router import router as claims_router
from app.devices.router import router as devices_router
from app.fraud.router import router as fraud_router
from app.graph.router import router as graph_router
from app.rag.router import router as rag_router
from app.multimodal.router import router as multimodal_router
from app.investigation.router import router as investigation_router

from app.analytics.router import router as analytics_router
from app.evaluation.router import router as evaluation_router
from app.monitoring.router import router as monitoring_router

api_v1_router = APIRouter(prefix="/api/v1")

# ── Foundation ────────────────────────────────────────────────────
api_v1_router.include_router(health_router)

# ── Phase 2: Auth, Users & Audit ──────────────────────────────────
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(audit_router)

# ── Phase 3: Claims, Devices & Fraud ML ───────────────────────────
api_v1_router.include_router(claims_router)
api_v1_router.include_router(devices_router)
api_v1_router.include_router(fraud_router)

# ── Phase 4: Core AI Intelligence Engine ──────────────────────────
api_v1_router.include_router(graph_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(multimodal_router)
api_v1_router.include_router(investigation_router)

# ── Phase 5: Dashboard Analytics, Evaluation & Monitoring ─────────
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(evaluation_router)
api_v1_router.include_router(monitoring_router)
