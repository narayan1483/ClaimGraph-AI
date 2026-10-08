"""
ClaimGraph AI — LangGraph Multi-Agent Workflow Engine.

Compiles and executes the directed acyclic graph (DAG) of the 8 specialized
investigation agents, passing shared typed investigation state.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    claim_understanding_node,
    document_analysis_node,
    graph_investigation_node,
    human_review_node,
    investigation_report_node,
    ml_fraud_analysis_node,
    policy_rag_node,
    risk_aggregation_node,
    vision_analysis_node,
)
from app.agents.state import InvestigationState

logger = logging.getLogger("claimgraph.workflow")


def create_investigation_graph() -> Any:
    """Build and compile the LangGraph 8-Agent Investigation DAG."""
    builder = StateGraph(InvestigationState)

    # Register Nodes
    builder.add_node("claim_understanding", claim_understanding_node)
    builder.add_node("document_analysis", document_analysis_node)
    builder.add_node("vision_analysis", vision_analysis_node)
    builder.add_node("ml_fraud_analysis", ml_fraud_analysis_node)
    builder.add_node("graph_investigation", graph_investigation_node)
    builder.add_node("policy_rag", policy_rag_node)
    builder.add_node("risk_aggregation", risk_aggregation_node)
    builder.add_node("investigation_report", investigation_report_node)
    builder.add_node("human_review", human_review_node)

    # Add Sequential Flow Edges
    builder.add_edge(START, "claim_understanding")
    builder.add_edge("claim_understanding", "document_analysis")
    builder.add_edge("document_analysis", "vision_analysis")
    builder.add_edge("vision_analysis", "ml_fraud_analysis")
    builder.add_edge("ml_fraud_analysis", "graph_investigation")
    builder.add_edge("graph_investigation", "policy_rag")
    builder.add_edge("policy_rag", "risk_aggregation")
    builder.add_edge("risk_aggregation", "investigation_report")
    builder.add_edge("investigation_report", "human_review")
    builder.add_edge("human_review", END)

    compiled_graph = builder.compile()
    return compiled_graph


_compiled_graph = None


def get_investigation_graph():
    """Singleton getter for compiled LangGraph graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = create_investigation_graph()
    return _compiled_graph


async def run_investigation_workflow(initial_state: InvestigationState) -> InvestigationState:
    """
    Execute the multi-agent investigation workflow over a claim.
    Returns the fully populated state including all agent findings,
    hybrid risk score, and synthesized dossier.
    """
    graph = get_investigation_graph()
    logger.info("Initiating LangGraph multi-agent investigation for claim %s", initial_state.get("claim_id"))

    # Execute graph asynchronously
    final_state = await graph.ainvoke(initial_state)

    logger.info(
        "Completed multi-agent investigation for claim %s. Final Risk Score: %s (%s)",
        final_state.get("claim_id"),
        final_state.get("final_risk_score"),
        final_state.get("risk_level"),
    )
    return final_state
