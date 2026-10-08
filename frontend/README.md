# ClaimGraph AI — Frontend Architecture & UI Documentation

> **React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons**

---

## 1. Overview
The ClaimGraph AI frontend is an enterprise-grade workbench for fraud analysts, claims adjusters, and Special Investigation Unit (SIU) detectives.

---

## 2. Directory Layout
```
frontend/src/
├── assets/          # Static logos, graphics, and SVG assets
├── components/      # Shared components (ProtectedRoute, Navbar, Modals)
├── contexts/        # React contexts (AuthContext, ThemeContext)
├── hooks/           # Custom React hooks
├── layouts/         # Dashboard layout, sidebar navigation, header
├── pages/           # Application views:
│   ├── ClaimDetailsPage.tsx       # Full claim dossier & evidence timeline
│   ├── ClaimsPage.tsx             # Claims management and filtering
│   ├── CreateClaimModal.tsx       # Multi-step claim submission wizard
│   ├── DashboardPage.tsx          # Enterprise operational KPI cards & charts
│   ├── FraudMetricsPage.tsx       # XGBoost ROC-AUC & confusion matrix
│   ├── InvestigationPage.tsx      # LangGraph 8-agent real-time trace & HITL
│   ├── KnowledgeGraphPage.tsx     # Neo4j fraud ring visualizer
│   ├── LoginPage.tsx              # Secure JWT authentication
│   ├── PolicyIntelligencePage.tsx # Grounded RAG policy copilot
│   ├── AuditLogsPage.tsx          # Security & compliance audit trail
│   ├── AIEvaluationPage.tsx       # RAG faithfulness & agent benchmark runner
│   └── ModelMonitoringPage.tsx    # PSI drift detection & latency percentiles
├── services/        # Axios API client with automatic JWT token attachment
└── types/           # TypeScript interfaces and response schemas
```

---

## 3. Key Pages & Features

1. **Enterprise Dashboard (`/`)**: Total claims, fraud rate %, high risk claims, pending reviews, charts over time, and suspicious graph entities.
2. **Claims Workbench (`/claims`)**: List, filter by risk band (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and open claim dossiers.
3. **Investigation Center (`/investigation`)**: Run LangGraph 8-agent DAG, visualize live node progress, review categorized evidence, and submit certified investigator decisions (`APPROVE`, `REJECT`, `ESCALATE`).
4. **Knowledge Graph (`/graph`)**: View entity counts, analyze fraud rings, and detect shared hardware/repair shop clusters.
5. **Policy Intelligence (`/policy`)**: Query policies with semantic search and review grounded answers with provenance citations.
6. **Model Performance & Drift (`/model-performance`, `/drift`)**: XGBoost metrics, confusion matrix, P95 latency, and PSI drift tracking.
7. **AI Evaluation (`/ai-evaluation`)**: Empirical RAG faithfulness, answer relevance, retrieval MRR, and live benchmark execution.
8. **Audit Trail (`/audit`)**: Tamper-evident chronological log of all claim transitions, actors, IP addresses, and decisions.

---

## 4. Local Development & Build

```bash
# Install dependencies
npm install

# Start local development server (http://localhost:5173)
npm run dev

# Compile TypeScript and build production bundle
npm run build
```
