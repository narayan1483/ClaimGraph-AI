"""
ClaimGraph AI — Deterministic Hybrid Risk Engine.

Combines ML fraud probability, Knowledge Graph risk, document consistency,
image evidence, and policy compliance into an authoritative final risk score.
The LLM does NOT calculate the numerical score — this engine computes it deterministically.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("claimgraph.risk")


class EvidenceItem(BaseModel):
    """Categorized evidence item with clear attribution."""

    category: str = Field(..., description="FACT | ML SIGNAL | GRAPH SIGNAL | AI ANALYSIS | RECOMMENDATION")
    text: str = Field(..., description="Human-readable statement")
    weight: Optional[float] = None
    source: Optional[str] = None


class HybridRiskOutput(BaseModel):
    """Output from deterministic hybrid risk engine."""

    final_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH | CRITICAL")
    recommended_action: str = Field(..., description="NORMAL_PROCESSING | MANUAL_REVIEW | INVESTIGATION")
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class DeterministicHybridRiskEngine:
    """
    Mathematical composite risk aggregator.
    Weights:
    - ML Fraud Probability: 30%
    - Graph Risk Score: 25%
    - Document Inconsistency: 15%
    - Vision / Damage Inconsistency: 10%
    - Policy Inconsistency: 10%
    - Claim History & Velocity: 10%
    """

    WEIGHTS = {
        "ml_fraud_prob": 0.30,
        "graph_risk_score": 0.25,
        "doc_inconsistency": 0.15,
        "vision_inconsistency": 0.10,
        "policy_inconsistency": 0.10,
        "claim_velocity": 0.10,
    }

    @classmethod
    def evaluate(
        cls,
        ml_fraud_prob: float,
        graph_risk_score: float,
        doc_inconsistent: bool,
        vision_inconsistent: bool,
        policy_inconsistent: bool,
        prior_claims_count: int,
        claim_amount: float,
        ml_evidence: Optional[List[str]] = None,
        graph_evidence: Optional[List[str]] = None,
        doc_evidence: Optional[List[str]] = None,
        vision_evidence: Optional[List[str]] = None,
        policy_evidence: Optional[List[str]] = None,
    ) -> HybridRiskOutput:
        """Calculate final composite risk score and compile categorized evidence."""
        # Normalize component scores
        ml_score = max(0.0, min(1.0, float(ml_fraud_prob)))
        graph_score = max(0.0, min(1.0, float(graph_risk_score)))
        doc_score = 0.85 if doc_inconsistent else 0.05
        vision_score = 0.80 if vision_inconsistent else 0.05
        policy_score = 0.90 if policy_inconsistent else 0.05

        # Velocity score based on prior claims
        if prior_claims_count >= 3:
            velocity_score = 0.90
        elif prior_claims_count == 2:
            velocity_score = 0.60
        elif prior_claims_count == 1:
            velocity_score = 0.30
        else:
            velocity_score = 0.05

        # Monetary multiplier for large claims
        amount_penalty = 0.05 if claim_amount > 2000.0 else 0.0

        # Weighted calculation
        raw_score = (
            cls.WEIGHTS["ml_fraud_prob"] * ml_score
            + cls.WEIGHTS["graph_risk_score"] * graph_score
            + cls.WEIGHTS["doc_inconsistency"] * doc_score
            + cls.WEIGHTS["vision_inconsistency"] * vision_score
            + cls.WEIGHTS["policy_inconsistency"] * policy_score
            + cls.WEIGHTS["claim_velocity"] * velocity_score
            + amount_penalty
        )

        final_score = round(min(1.0, max(0.01, raw_score)), 2)

        # Classify risk level
        if final_score < 0.30:
            risk_level = "LOW"
            recommended_action = "NORMAL_PROCESSING"
        elif final_score < 0.60:
            risk_level = "MEDIUM"
            recommended_action = "MANUAL_REVIEW"
        elif final_score < 0.80:
            risk_level = "HIGH"
            recommended_action = "INVESTIGATION"
        else:
            risk_level = "CRITICAL"
            recommended_action = "INVESTIGATION"

        # Construct categorized evidence
        evidence_items: List[EvidenceItem] = []

        # 1. FACT
        evidence_items.append(
            EvidenceItem(
                category="FACT",
                text=f"Claim submitted for ${claim_amount:,.2f} with {prior_claims_count} documented prior claim(s) on file.",
                source="Core Database Records",
            )
        )

        # 2. ML SIGNAL
        ml_desc = f"Machine Learning model inferred fraud probability of {ml_score:.1%}."
        if ml_evidence:
            ml_desc += f" Primary factors: {'; '.join(ml_evidence[:2])}."
        evidence_items.append(
            EvidenceItem(
                category="ML SIGNAL",
                text=ml_desc,
                weight=round(ml_score * cls.WEIGHTS["ml_fraud_prob"], 3),
                source="XGBoost Classifier + SHAP Attribution",
            )
        )

        # 3. GRAPH SIGNAL
        graph_desc = f"Neo4j Knowledge Graph topology computed risk score of {graph_score:.1%}."
        if graph_evidence:
            graph_desc += f" Topological evidence: {'; '.join(graph_evidence[:2])}."
        evidence_items.append(
            EvidenceItem(
                category="GRAPH SIGNAL",
                text=graph_desc,
                weight=round(graph_score * cls.WEIGHTS["graph_risk_score"], 3),
                source="Neo4j Entity Resolution & Centrality Engine",
            )
        )

        # 4. AI ANALYSIS
        if doc_evidence:
            evidence_items.append(
                EvidenceItem(
                    category="AI ANALYSIS",
                    text=f"Document Analysis: {'; '.join(doc_evidence[:2])}",
                    source="Document Analysis Agent",
                )
            )
        if vision_evidence:
            evidence_items.append(
                EvidenceItem(
                    category="AI ANALYSIS",
                    text=f"Vision Analysis: {'; '.join(vision_evidence[:2])}",
                    source="Vision Analysis Agent",
                )
            )
        if policy_evidence:
            evidence_items.append(
                EvidenceItem(
                    category="AI ANALYSIS",
                    text=f"Policy RAG Verification: {'; '.join(policy_evidence[:2])}",
                    source="Policy RAG Agent",
                )
            )

        # 5. RECOMMENDATION
        rec_text = (
            f"Adjudication Recommendation: {recommended_action.replace('_', ' ')}. "
            f"Assigned risk level {risk_level} based on composite score of {final_score:.2f}."
        )
        if risk_level in ["HIGH", "CRITICAL"]:
            rec_text += " Requires mandatory Special Investigation Unit (SIU) interview and manual signoff before payment."
        evidence_items.append(
            EvidenceItem(
                category="RECOMMENDATION",
                text=rec_text,
                source="Hybrid Risk Engine Governance Matrix",
            )
        )

        score_breakdown = {
            "ml_fraud_component": round(ml_score * cls.WEIGHTS["ml_fraud_prob"], 3),
            "graph_risk_component": round(graph_score * cls.WEIGHTS["graph_risk_score"], 3),
            "document_inconsistency_component": round(doc_score * cls.WEIGHTS["doc_inconsistency"], 3),
            "vision_evidence_component": round(vision_score * cls.WEIGHTS["vision_inconsistency"], 3),
            "policy_compliance_component": round(policy_score * cls.WEIGHTS["policy_inconsistency"], 3),
            "claim_velocity_component": round(velocity_score * cls.WEIGHTS["claim_velocity"], 3),
            "raw_total": final_score,
        }

        return HybridRiskOutput(
            final_risk_score=final_score,
            risk_level=risk_level,
            recommended_action=recommended_action,
            score_breakdown=score_breakdown,
            evidence=evidence_items,
        )
