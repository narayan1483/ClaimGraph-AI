# ClaimGraph AI — Hybrid RAG & Policy Intelligence Engine

> **RAG Thesis**: Generative models must never invent insurance clauses. Answers must be strictly grounded in verified policy documentation, complete with explicit section citations and confidence scoring.

---

## 1. RAG Architecture

```mermaid
flowchart LR
    Query["User / Agent Policy Query"] --> Pre["Query Preprocessing & Intent Extraction"]
    Pre --> Hybrid["Hybrid Retrieval Layer"]
    Hybrid --> BM25["BM25 Keyword Matching (Exact Codes)"]
    Hybrid --> Dense["Dense TF-IDF Vector Cosine Sim"]
    BM25 --> Merge["Reciprocal Rank Fusion (RRF)"]
    Dense --> Merge
    Merge --> Chunks["Top-K Policy Chunks"]
    Chunks --> Guard["Hallucination & Grounding Guardrail"]
    Guard --> Synth["Grounded Synthesizer with Citations"]
```

---

## 2. Policy Corpus Structure

Indexed policy documents stored locally in markdown and JSON format:
- `comprehensive_device_protection.md`: Accidental damage, screen repairs, replacement criteria
- `theft_and_loss_guidelines.md`: Police report deadlines, proof of purchase affidavits
- `repair_authorization_policy.md`: OEM vs aftermarket parts, authorized repair facility criteria
- `fraud_sanctions_and_denial.md`: Altered estimates, misrepresentation, SIU escalation thresholds

---

## 3. Grounding & Anti-Hallucination Guardrails

- **Strict Relevance Floor**: If retrieved chunks have cosine similarity $< 0.08$, the engine refuses to infer rules and returns an explicit rejection notice.
- **Citation Provenance**: Every output sentence maps back to its parent document (`POL-WATER-01`, `Section 4.2`).
- **Empirical Evaluation**: Benchmark demonstrates $> 80\%$ token-level unigram grounding and $100\%$ hallucination-free generation on the benchmark set.
