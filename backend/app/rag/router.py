"""
ClaimGraph AI — RAG Policy Intelligence API Router.

Endpoints for querying warranty policies, fraud guidelines, and escalation SOPs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from app.rag.engine import RAGPolicyEngine, get_rag_engine
from app.rag.schemas import RAGQueryRequest, RAGQueryResponse

router = APIRouter(prefix="/rag", tags=["RAG Policy Intelligence"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_policy_rag(
    payload: RAGQueryRequest,
    rag_engine: RAGPolicyEngine = Depends(get_rag_engine),
) -> RAGQueryResponse:
    """
    Query insurance warranty policies and fraud investigation guidelines.
    Returns strictly grounded answers with citations, retrieved chunks, and latency.
    """
    response = rag_engine.query_policy(
        query=payload.query,
        claim_id=payload.claim_id,
        policy_type=payload.policy_type,
        top_k=payload.top_k,
    )
    return response


@router.get("/policies")
async def list_available_policies(
    rag_engine: RAGPolicyEngine = Depends(get_rag_engine),
) -> Dict[str, Any]:
    """List loaded policy documents and indexed chunk statistics."""
    doc_names = sorted(list(set(c.document_name for c in rag_engine.chunks)))
    return {
        "indexed_documents": doc_names,
        "total_chunks": len(rag_engine.chunks),
        "status": "ready" if rag_engine._is_indexed else "indexing_failed",
    }
