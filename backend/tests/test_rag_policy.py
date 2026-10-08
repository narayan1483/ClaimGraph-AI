"""
ClaimGraph AI — RAG Policy Intelligence Tests.
"""

import pytest
from app.rag.engine import RAGPolicyEngine


def test_rag_policy_engine_indexing():
    """Verify that synthetic policy documents are loaded and indexed."""
    engine = RAGPolicyEngine.get_instance()
    assert len(engine.chunks) > 0
    assert engine._is_indexed is True

    doc_names = set(c.document_name for c in engine.chunks)
    assert "warranty_policy" in doc_names
    assert "claim_policy" in doc_names
    assert "fraud_guidelines" in doc_names
    assert "investigation_sop" in doc_names
    assert "escalation_policy" in doc_names


def test_rag_retrieval_and_grounded_answer():
    """Verify accurate semantic retrieval for warranty and deductible inquiries."""
    engine = RAGPolicyEngine.get_instance()

    resp = engine.query_policy("What is the deductible for accidental damage protection (ADP)?", top_k=3)
    assert resp.grounded is True
    assert len(resp.sources) > 0
    assert "warranty_policy" in resp.sources
    assert len(resp.retrieved_chunks) > 0
    assert resp.latency_ms > 0
    assert resp.token_usage.total_tokens > 0
    assert "$49" in resp.answer or "deductible" in resp.answer.lower()


def test_rag_insufficient_evidence_for_unrelated_query():
    """Verify that ungrounded queries do not hallucinate policy rules."""
    engine = RAGPolicyEngine.get_instance()

    resp = engine.query_policy("Can quantum teleportation be used for deep sea submarine navigation?", top_k=3)
    assert resp.grounded is False
    assert "sufficient evidence was not found" in resp.answer.lower()
