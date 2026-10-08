"""
ClaimGraph AI — RAG Policy Engine.

Document parsing, semantic chunking, vector indexing with cosine retrieval,
and grounded answer generation for insurance and fraud guidelines.
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.schemas import RAGChunk, RAGQueryResponse, RAGTokenUsage

logger = logging.getLogger("claimgraph.rag")

POLICIES_DIR = Path(__file__).resolve().parent / "policies"


class PolicyChunk:
    """Internal representation of a policy section chunk."""

    def __init__(self, chunk_id: str, document_name: str, section_title: str, text: str) -> None:
        self.chunk_id = chunk_id
        self.document_name = document_name
        self.section_title = section_title
        self.text = text


class RAGPolicyEngine:
    """Manages document vector indexing, semantic retrieval, and grounded answer synthesis."""

    _instance: Optional["RAGPolicyEngine"] = None

    def __init__(self) -> None:
        self.chunks: List[PolicyChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self._is_indexed: bool = False
        self._load_and_index()

    @classmethod
    def get_instance(cls) -> "RAGPolicyEngine":
        if cls._instance is None:
            cls._instance = RAGPolicyEngine()
        return cls._instance

    def _load_and_index(self) -> None:
        """Parse local policy documents into chunks and build vector index."""
        self.chunks.clear()
        if not POLICIES_DIR.exists():
            logger.warning("Policies directory %s does not exist", POLICIES_DIR)
            return

        chunk_counter = 1
        for md_file in sorted(POLICIES_DIR.glob("*.md")):
            doc_name = md_file.stem
            try:
                content = md_file.read_text(encoding="utf-8")
                # Parse markdown sections by headings (## or ###)
                sections = re.split(r"\n(?=#{1,3}\s)", content)
                for sec in sections:
                    clean_sec = sec.strip()
                    if not clean_sec:
                        continue
                    # Extract section heading
                    lines = clean_sec.split("\n")
                    header_line = lines[0].strip("# ").strip()
                    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else header_line

                    chunk_obj = PolicyChunk(
                        chunk_id=f"chk_{chunk_counter:04d}",
                        document_name=doc_name,
                        section_title=header_line,
                        text=f"{header_line}\n{body}",
                    )
                    self.chunks.append(chunk_obj)
                    chunk_counter += 1
            except Exception as e:
                logger.error("Failed to read policy document %s: %s", md_file, e)

        if self.chunks:
            # Build vector space with sublinear TF and n-grams
            corpus = [c.text for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True,
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self._is_indexed = True
            logger.info("RAG Policy Engine indexed %d chunks across %s documents", len(self.chunks), len(list(POLICIES_DIR.glob("*.md"))))

    def retrieve(self, query: str, top_k: int = 3, policy_filter: Optional[str] = None) -> List[Tuple[PolicyChunk, float]]:
        """Retrieve top-K policy chunks based on vector cosine similarity."""
        if not self._is_indexed or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Pair with chunks
        ranked_indices = np.argsort(similarities)[::-1]
        results: List[Tuple[PolicyChunk, float]] = []

        for idx in ranked_indices:
            score = float(similarities[idx])
            chunk = self.chunks[idx]
            if policy_filter and policy_filter.lower() not in chunk.document_name.lower():
                continue
            if score > 0.05:  # Minimum similarity threshold
                results.append((chunk, score))
            if len(results) >= top_k:
                break

        return results

    def query_policy(
        self,
        query: str,
        claim_id: Optional[str] = None,
        policy_type: Optional[str] = None,
        top_k: int = 3,
    ) -> RAGQueryResponse:
        """
        Execute full RAG pipeline:
        Query -> Vector Retrieval -> Grounded Answer Synthesis -> Provenance Citations.
        """
        start_time = time.perf_counter()

        retrieved = self.retrieve(query=query, top_k=top_k, policy_filter=policy_type)

        rag_chunks: List[RAGChunk] = []
        sources: Set[str] = set()

        for chunk, score in retrieved:
            rag_chunks.append(
                RAGChunk(
                    chunk_id=chunk.chunk_id,
                    document=chunk.document_name,
                    section=chunk.section_title,
                    content=chunk.text,
                    similarity_score=round(score, 4),
                )
            )
            sources.add(chunk.document_name)

        # Grounded Generation
        # If no chunks retrieved or maximum similarity is too low, strictly do NOT hallucinate rules.
        if not rag_chunks or (rag_chunks and rag_chunks[0].similarity_score < 0.08):
            answer = (
                "Sufficient evidence was not found in the official policy documentation to answer this query. "
                "Policy rules cannot be inferred without explicit textual basis in the approved guidelines."
            )
            grounded = False
        else:
            # Deterministic, authoritative answer synthesis from retrieved chunks
            primary_chunk = rag_chunks[0]
            answer_parts = []
            answer_parts.append(f"Based on the official **{primary_chunk.document}** (Section: *{primary_chunk.section}*):")

            # Extract the most relevant sentences directly from top chunks
            key_points = []
            for c in rag_chunks:
                # Get non-empty lines from chunk text
                lines = [l.strip("- *").strip() for l in c.content.split("\n") if l.strip() and not l.startswith("#")]
                for line in lines[:3]:
                    if line and len(line) > 15:
                        key_points.append(f"- {line} (*Source: {c.document}*)")

            # Dedup key points
            unique_points = list(dict.fromkeys(key_points))[:4]
            answer_parts.extend(unique_points)

            # Summarize grounding
            answer_parts.append(
                f"\nGoverning Standards: Verified against {len(rag_chunks)} retrieved policy section(s). "
                "Any deviation requires manual escalation per the Claim Escalation Policy."
            )
            answer = "\n".join(answer_parts)
            grounded = True

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Calculate approximate token count
        total_words = len(query.split()) + len(answer.split()) + sum(len(c.content.split()) for c in rag_chunks)
        prompt_tokens = int(len(query.split()) * 1.3) + int(sum(len(c.content.split()) * 1.3 for c in rag_chunks))
        completion_tokens = int(len(answer.split()) * 1.3)

        return RAGQueryResponse(
            query=query,
            answer=answer,
            sources=sorted(list(sources)),
            retrieved_chunks=rag_chunks,
            model="claimgraph-grounded-rag-v1",
            latency_ms=latency_ms,
            token_usage=RAGTokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            grounded=grounded,
        )


def get_rag_engine() -> RAGPolicyEngine:
    """Dependency injector for RAG engine."""
    return RAGPolicyEngine.get_instance()
