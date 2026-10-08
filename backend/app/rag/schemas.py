"""
ClaimGraph AI — RAG Policy Intelligence Schemas.

Pydantic models for policy question-answering requests, chunk citations,
and grounded intelligence responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """User or agent query against policy documents."""

    query: str = Field(..., min_length=2, description="Natural language inquiry regarding policy or guidelines")
    claim_id: Optional[str] = Field(None, description="Optional associated claim ID for context")
    policy_type: Optional[str] = Field(None, description="Filter to specific policy document")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of top chunks to retrieve")


class RAGChunk(BaseModel):
    """Retrieved document chunk with provenance."""

    chunk_id: str
    document: str
    section: str
    content: str
    similarity_score: float


class RAGTokenUsage(BaseModel):
    """Token consumption accounting."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class RAGQueryResponse(BaseModel):
    """Complete grounded answer response."""

    query: str
    answer: str
    sources: List[str] = Field(default_factory=list, description="Unique policy document source names")
    retrieved_chunks: List[RAGChunk] = Field(default_factory=list)
    model: str = Field(default="claimgraph-grounded-rag-v1")
    latency_ms: float = Field(..., description="Query processing latency in milliseconds")
    token_usage: RAGTokenUsage = Field(default_factory=RAGTokenUsage)
    grounded: bool = Field(default=True, description="Whether the answer is grounded in retrieved chunks")
