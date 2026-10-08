# ClaimGraph AI — Local Development & Docker Setup

> **Deployment Statement**: "Designed for cloud deployment, currently runnable locally using Docker Compose."

---

## 1. Prerequisites
- **Docker** & **Docker Compose** (v24.0+)
- **Python** (3.12+) — for local CLI / test execution
- **Node.js** (v20+) & **npm** — for local frontend development
- Minimum RAM: 8GB (16GB recommended for running all containers concurrently)

---

## 2. One-Command Full Stack Startup

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/ClaimGraph-AI.git
cd ClaimGraph-AI

# 2. Copy environment template
cp .env.example .env

# 3. Start all services via Docker Compose
docker compose up --build -d
```

---

## 3. Container Services & Ports

| Container | Service | Port Mapping | Healthcheck |
| :--- | :--- | :---: | :---: |
| `claimgraph-frontend` | React 19 + Vite Dashboard | `http://localhost:3000` | Nginx HTTP 200 |
| `claimgraph-backend` | FastAPI 0.115 API Server | `http://localhost:8000` | `/api/v1/health` |
| `claimgraph-postgres` | PostgreSQL 16 + pgvector | `localhost:5432` | `pg_isready` |
| `claimgraph-neo4j` | Neo4j 5 Community Edition | `http://localhost:7474` (UI)<br>`bolt://localhost:7687` | Cypher ping |
| `claimgraph-redis` | Redis 7 Cache & Pub/Sub | `localhost:6379` | `redis-cli ping` |
| `claimgraph-kafka` | Apache Kafka Broker | `localhost:9092` | `kafka-topics list` |
| `claimgraph-zookeeper` | Zookeeper Coordination | `localhost:2181` | TCP port open |

---

## 4. One-Time Database Initialization

After containers are healthy, execute the database migration:
```bash
docker compose exec backend alembic upgrade head
```

---

## 5. Running Tests Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```
All 46 integration and unit tests will run against an isolated in-memory test database.
