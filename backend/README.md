# ClaimGraph AI — Backend Architecture & Service Documentation

> **FastAPI 0.115 + SQLAlchemy 2 (Async) + Neo4j + XGBoost + LangGraph + Redis + Kafka**

---

## 1. Overview
The ClaimGraph AI backend provides enterprise insurance claims intelligence, machine learning fraud prediction, graph relationship anomaly detection, and automated multi-agent investigation workflows.

---

## 2. Directory Structure
```
backend/
├── alembic/                  # Database migration scripts (001, 002)
├── app/
│   ├── agents/               # LangGraph 8-Agent investigation workflow
│   ├── analytics/            # Enterprise dashboard operational aggregations
│   ├── api/v1/               # API version 1 routing and health checks
│   ├── audit/                # Immutable security and compliance audit logging
│   ├── auth/                 # JWT authentication and RBAC guards
│   ├── claims/               # Core claims lifecycle and event auditing
│   ├── core/                 # Config, database, logging, redis, kafka, neo4j
│   ├── customers/            # Customer profiles and risk indicators
│   ├── devices/              # Product catalog and physical device tracking
│   ├── evaluation/           # Empirical AI (RAG) & ML evaluation benchmarks
│   ├── fraud/                # XGBoost classifier, SHAP explainability, dataset generator
│   ├── graph/                # Neo4j knowledge graph service and Cypher analytics
│   ├── investigation/        # Investigation record management and HITL decisioning
│   ├── monitoring/           # Inference telemetry and PSI drift detection
│   ├── multimodal/           # EXIF tamper detection, pHash, invoice validation
│   ├── rag/                  # Hybrid policy retrieval (BM25 + TF-IDF) and citations
│   ├── risk/                 # Composite risk scoring formulas
│   └── users/                # User accounts, organization tenants, roles
├── pyproject.toml            # Poetry / Pip dependencies and tool config
└── tests/                    # 46 Automated unit & integration tests
```

---

## 3. Key API Endpoints

### Authentication & Users
- `POST /api/v1/auth/register`: Register new user (Customer, Investigator, Admin)
- `POST /api/v1/auth/login`: Issue access & refresh JWT tokens
- `GET /api/v1/users/me`: Current authenticated user profile

### Claims & Fraud
- `POST /api/v1/claims`: Submit new claim (triggers fraud scoring and Kafka event)
- `GET /api/v1/claims`: List claims with pagination and risk filtering
- `POST /api/v1/fraud/predict`: Direct ML fraud probability and SHAP factors

### Knowledge Graph
- `GET /api/v1/graph/stats`: Node and relationship counts
- `GET /api/v1/graph/rings`: Fraud rings and cyclical relationship clusters
- `GET /api/v1/graph/centrality`: High-degree suspicious entities

### Investigation & Multi-Agent
- `POST /api/v1/investigations/{claim_id}/run`: Execute LangGraph 8-agent DAG
- `GET /api/v1/investigations/{claim_id}`: Retrieve completed investigation dossier
- `POST /api/v1/investigations/{inv_id}/decision`: Human investigator adjudication (`APPROVE`, `REJECT`, `ESCALATE`)

### Evaluation & Monitoring
- `GET /api/v1/evaluation/ml`: Real XGBoost validation metrics and confusion matrix
- `GET /api/v1/evaluation/ai`: Empirical RAG faithfulness and agent success rates
- `GET /api/v1/monitoring/metrics`: Inference counts, latency percentiles, error rates
- `GET /api/v1/monitoring/drift`: Population Stability Index (PSI) drift report
- `GET /api/v1/analytics/dashboard`: Operational KPIs, distributions, and trends

---

## 4. Local Execution & Testing

```bash
# Activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install package in development mode
pip install -e ".[dev]"

# Run test suite
pytest
```
