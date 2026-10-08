"""
ClaimGraph AI — LangGraph Multi-Agent State Definition.

TypedDict and Pydantic models for shared investigation state, agent results,
and audit trails across the 8-agent workflow.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Standardized structured output for all specialized investigation agents."""

    agent_name: str
    status: str = "SUCCESS"  # SUCCESS, FAILED, RETRIED, SKIPPED
    result: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str
    latency_ms: float = 0.0


class InvestigationState(TypedDict, total=False):
    """
    Shared typed state flowing through LangGraph nodes.
    Each agent inspects and enriches this state.
    """

    # Claim & Entity Inputs
    claim_id: str
    claim_data: Dict[str, Any]
    customer_data: Dict[str, Any]
    device_data: Dict[str, Any]
    prior_claims_count: int

    # Agent Execution Registry
    agent_results: Dict[str, Dict[str, Any]]
    current_step: str
    errors: List[str]
    retry_counts: Dict[str, int]

    # Specialized Analytical Signals
    ml_fraud_prob: float
    ml_factors: List[str]
    graph_risk_score: float
    graph_evidence: List[str]
    doc_inconsistent: bool
    doc_evidence: List[str]
    vision_inconsistent: bool
    vision_evidence: List[str]
    policy_inconsistent: bool
    policy_evidence: List[str]

    # Risk Aggregation & Governance
    final_risk_score: float
    risk_level: str
    recommended_action: str
    score_breakdown: Dict[str, float]
    categorized_evidence: List[Dict[str, Any]]

    # Final Synthesis & Human-in-the-Loop Gate
    investigation_report: str
    human_review_required: bool
    is_completed: bool
