"""
ClaimGraph AI — Investigation API Schemas.

Pydantic schemas for running multi-agent investigations, returning structured
results, and recording human investigator decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvestigationRunResponse(BaseModel):
    """Complete output returned by POST /api/v1/investigations/{claim_id}/run."""

    investigation_id: str
    claim_id: str
    fraud_score: float
    graph_score: float
    final_risk_score: float
    risk_level: str
    recommendation: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    agent_results: Dict[str, Any] = Field(default_factory=dict)
    investigation_report: str
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    status: str = "AWAITING_REVIEW"


class InvestigationDecisionRequest(BaseModel):
    """Payload for human investigator final adjudication decision."""

    decision: str = Field(..., description="APPROVE | REJECT | ESCALATE | REQUEST_MORE_INFO")
    notes: Optional[str] = Field(None, description="Investigator rationale and case notes")
    badge_number: Optional[str] = Field(None, description="Investigator credentials/badge ID")


class InvestigationDecisionResponse(BaseModel):
    """Response confirming human decision record."""

    investigation_id: str
    claim_id: str
    decision: str
    new_claim_status: str
    message: str
    decided_at: str
