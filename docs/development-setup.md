# Development Setup Guide — ClaimGraph AI

This guide walks you through setting up a local development environment for **ClaimGraph AI**.

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Python**: Version 3.11 or 3.12 (`python --version`)
- **Node.js**: Version 20.x or later (`node --version`)
- **npm**: Version 10.x or later (`npm --version`)
- **Docker & Docker Compose**: Optional, for running local databases (PostgreSQL, Neo4j, Redis, Kafka).

---

## 1. Initial Repository Setup

Clone or open the workspace and configure environment variables:

```bash
# In the repository root
cp .env.example .env
```

Review `.env` and adjust ports or credentials if needed for your local workstation.

---

## 2. Backend Setup (FastAPI)

### 2.1 Set Up Python Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### 2.3 Run Backend Tests

```bash
pytest
```

Expected output:
```
tests/test_config.py .....                                       [ 45%]
tests/test_health.py ...                                         [ 72%]
tests/test_schemas.py ...                                        [100%]
============================== 11 passed in 0.45s ==============================
```

### 2.4 Start Development Server

```bash
uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Verify endpoints:
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Liveness Probe**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- **Readiness Probe**: [http://127.0.0.1:8000/api/v1/health/ready](http://127.0.0.1:8000/api/v1/health/ready)

---

## 3. Frontend Setup (React 19 + TypeScript + Vite)

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Build Verification

Verify that TypeScript checks and Vite bundle pass cleanly:

```bash
npm run build
```

### 3.3 Start Frontend Development Server

```bash
npm run dev
```

Open your browser to: [http://localhost:5173](http://localhost:5173)

The dashboard will automatically connect to `http://localhost:8000/api/v1/health` via the Vite proxy and show the live **System Online** indicator and backend health stats.

---

## 4. Running Backing Services with Docker Compose

To run PostgreSQL, Neo4j, Redis, Zookeeper, and Kafka together:

```bash
# From workspace root
docker compose up -d postgres redis neo4j zookeeper kafka
```

Service interfaces:
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (Username: `neo4j`, Password: `claimgraph_dev_password`)
- **PostgreSQL**: Port `5432` (`claimgraph` database)
- **Redis**: Port `6379`
- **Kafka Broker**: Port `9092`

To shut down containers:
```bash
docker compose down
```
To shut down and wipe persistent volumes:
```bash
docker compose down -v
```
