"""
ClaimGraph AI — Tests for Phase 5: Evaluation, Monitoring & Enterprise Dashboard.

Validates:
- AI evaluation endpoints (RAG faithfulness, agent performance, benchmarks)
- ML model evaluation metrics (Precision, Recall, ROC-AUC, FPR, FNR, Confusion Matrix)
- Model monitoring & PSI drift detection
- Enterprise dashboard analytics aggregation with Redis caching
"""

import pytest
from httpx import AsyncClient


async def _get_auth_token(client: AsyncClient) -> str:
    """Register and return a valid JWT token."""
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "phase5.tester@claimgraph.ai",
            "password": "Password123!",
            "full_name": "Phase 5 Tester",
            "role": "ADMIN",
        },
    )
    if res.status_code == 201:
        return res.json()["data"]["access_token"]
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "phase5.tester@claimgraph.ai", "password": "Password123!"},
    )
    return login.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_ml_evaluation_metrics(client: AsyncClient):
    """Verify empirical ML evaluation metrics extracted from trained model artifacts."""
    token = await _get_auth_token(client)
    response = await client.get(
        "/api/v1/evaluation/ml",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "XGBoost"
    assert "primary_metrics" in data
    assert data["primary_metrics"]["precision"] > 0.90
    assert data["primary_metrics"]["recall"] > 0.90
    assert data["primary_metrics"]["roc_auc"] > 0.95
    assert "confusion_matrix" in data
    assert data["primary_metrics"]["false_positive_rate"] >= 0.0


@pytest.mark.asyncio
async def test_ai_evaluation_metrics(client: AsyncClient):
    """Verify AI evaluation metrics (RAG faithfulness, relevance, agent success rate)."""
    token = await _get_auth_token(client)
    response = await client.get(
        "/api/v1/evaluation/ai",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "rag_evaluation" in data
    assert "agent_evaluation" in data
    assert data["rag_evaluation"]["rag_faithfulness"] > 0.0
    assert data["rag_evaluation"]["hallucination_free_percentage"] >= 80.0
    assert data["agent_evaluation"]["agent_success_rate"] == 1.0


@pytest.mark.asyncio
async def test_model_monitoring_metrics_and_drift(client: AsyncClient):
    """Verify real-time model telemetry and PSI drift analysis endpoints."""
    token = await _get_auth_token(client)
    # 1. Telemetry
    res_metrics = await client.get(
        "/api/v1/monitoring/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_metrics.status_code == 200
    data_metrics = res_metrics.json()
    assert data_metrics["prediction_count"] > 0
    assert "latency" in data_metrics
    assert data_metrics["drift_status"] in ["STABLE", "MODERATE_DRIFT", "SIGNIFICANT_DRIFT"]

    # 2. Drift
    res_drift = await client.get(
        "/api/v1/monitoring/drift",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_drift.status_code == 200
    data_drift = res_drift.json()
    assert "psi_value" in data_drift
    assert "baseline_distribution" in data_drift
    assert "production_distribution" in data_drift


@pytest.mark.asyncio
async def test_enterprise_dashboard_summary(client: AsyncClient):
    """Verify enterprise dashboard operational aggregations and charts."""
    token = await _get_auth_token(client)
    response = await client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary_cards" in data
    assert "charts" in data
    assert "system_status" in data
    assert "total_claims" in data["summary_cards"]
    assert "fraud_rate_percentage" in data["summary_cards"]

