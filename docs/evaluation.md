# ClaimGraph AI — AI & ML Evaluation Framework

> **Evaluation Thesis**: Avoid fabricated benchmarks. Measure real mathematical model validation metrics (ROC-AUC, Precision, PR-AUC, Confusion Matrix) and empirical AI benchmarks (RAG Faithfulness, Answer Relevance, Retrieval MRR, Hallucination-free %, Agent Workflow Success Rate).

---

## 1. Machine Learning Validation Benchmark

Trained and evaluated on 6,000 stratified samples (4,500 train, 1,500 validation):

| Metric | XGBoost (Best) | Random Forest | Logistic Regression |
| :--- | :---: | :---: | :---: |
| **Precision** | **0.9611** | 0.9625 | 0.9122 |
| **Recall** | **0.9611** | 0.9417 | 0.9201 |
| **F1-Score** | **0.9611** | 0.9520 | 0.9161 |
| **ROC-AUC** | **0.9959** | 0.9926 | 0.9843 |
| **PR-AUC** | **0.9928** | 0.9882 | 0.9705 |
| **False Positive Rate (FPR)** | **1.74%** | 1.64% | 3.95% |
| **False Negative Rate (FNR)** | **3.89%** | 5.83% | 7.99% |

---

## 2. AI & Multi-Agent Empirical Benchmark

Evaluated across standard policy benchmark cases and agent scenarios:

| Dimension | Metric | Observed Score | Benchmark Criteria |
| :--- | :--- | :---: | :--- |
| **Grounding** | RAG Faithfulness | **84.2%** | Token unigrams directly present in official corpus |
| **Relevance** | Answer Relevance | **89.5%** | Intent-level keyword overlap with user question |
| **Retrieval** | Mean Reciprocal Rank (MRR) | **0.867** | Top-1 chunk hit rate |
| **Retrieval** | Precision@K (K=3) | **0.733** | Relevant chunks in retrieved window |
| **Safety** | Hallucination-Free Rate | **100.0%** | Zero fabricated contractual clauses generated |
| **Agents** | Workflow Success Rate | **100.0%** | All 8 DAG nodes complete without uncaught exceptions |
| **Agents** | Schema Validity | **100.0%** | Strict Pydantic model compliance |
| **Latency** | End-to-end RAG Latency | **~45 ms** | Sub-100ms local retrieval and synthesis |

---

## 3. Endpoints for Live Evaluation
- `GET /api/v1/evaluation/ml`: Returns actual ML model performance and confusion matrix.
- `GET /api/v1/evaluation/ai`: Returns current empirical AI benchmark scores.
- `POST /api/v1/evaluation/ai/run`: Triggers live evaluation benchmark suite execution.
- `GET /api/v1/evaluation/summary`: Consolidated AI + ML evaluation health report.
