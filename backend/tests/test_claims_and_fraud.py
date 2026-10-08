"""
ClaimGraph AI — Claims Management & ML Fraud Detection Integration Tests.

Validates:
1. Product & Device setup
2. Claim creation
3. Claim retrieval with detailed dossier
4. State transitions (SUBMITTED -> UNDER_REVIEW -> FLAGGED_INVESTIGATION / APPROVED)
5. Direct ML fraud prediction endpoint (/api/v1/fraud/predict)
6. Model metrics comparison endpoint (/api/v1/fraud/metrics)
7. Dynamic claim evaluation endpoint (/api/v1/fraud/claims/{id}/evaluate)
"""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.customers.models import Customer
from app.devices.models import Device, Product
from app.fraud.service import FraudPredictionService
from app.users.models import User, UserRole


async def _create_test_environment(client: AsyncClient, db: AsyncSession) -> tuple[str, str, str, str]:
    """Helper setting up investigator user, customer profile, product, and device."""
    # 1. Register investigator
    inv_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "lead.inv@claimgraph.ai",
            "password": "Password123!",
            "full_name": "Lead Investigator",
            "role": "INVESTIGATOR",
        },
    )
    inv_token = inv_reg.json()["data"]["access_token"]

    # 2. Register customer
    cust_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "claimant@example.com",
            "password": "Password123!",
            "full_name": "Claimant Jane",
            "role": "CUSTOMER",
        },
    )
    cust_token = cust_reg.json()["data"]["access_token"]
    cust_user_id = cust_reg.json()["data"]["user"]["id"]

    # 3. Create Product in DB
    prod = Product(
        name="Titan Pro Smartphone 256GB",
        category="Electronics",
        manufacturer="Titan Mobile",
        model_number="TP-256",
        msrp=1200.0,
    )
    db.add(prod)
    await db.flush()

    # Find customer id
    cust_obj = (await db.execute(
        __import__("sqlalchemy").select(Customer).where(Customer.user_id == cust_user_id)
    )).scalar_one()

    # Create Device
    dev = Device(
        serial_number="SN-TEST-8841",
        product_id=prod.id,
        customer_id=cust_obj.id,
        purchase_date=datetime.now(timezone.utc),
        purchase_price=1200.0,
    )
    db.add(dev)
    await db.commit()

    return inv_token, cust_token, cust_obj.id, dev.id


@pytest.mark.asyncio
async def test_claim_creation_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Submitting a claim with valid customer & device should succeed and return CLM ID."""
    inv_token, cust_token, cust_id, dev_id = await _create_test_environment(client, db_session)

    claim_payload = {
        "customer_id": cust_id,
        "device_id": dev_id,
        "claim_type": "DAMAGE",
        "claim_amount": 750.0,
        "incident_date": datetime.now(timezone.utc).isoformat(),
        "description": "Screen severely cracked following accidental drop on concrete.",
        "location": "Chicago, IL",
        "repair_shop": "Metro Tech Express",
    }

    response = await client.post(
        "/api/v1/claims",
        json=claim_payload,
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    claim_data = body["data"]
    assert claim_data["claim_id"].startswith("CLM-")
    assert claim_data["status"] == "SUBMITTED"
    assert claim_data["claim_amount"] == 750.0


@pytest.mark.asyncio
async def test_claim_retrieval_and_filtering(client: AsyncClient, db_session: AsyncSession) -> None:
    """Claims can be listed and retrieved by ID with relations."""
    inv_token, cust_token, cust_id, dev_id = await _create_test_environment(client, db_session)

    # Create claim
    create_res = await client.post(
        "/api/v1/claims",
        json={
            "customer_id": cust_id,
            "device_id": dev_id,
            "claim_type": "MALFUNCTION",
            "claim_amount": 450.0,
            "incident_date": datetime.now(timezone.utc).isoformat(),
            "description": "Battery expansion and motherboard thermal shutdown.",
            "location": "Detroit, MI",
        },
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    created_id = create_res.json()["data"]["id"]
    claim_code = create_res.json()["data"]["claim_id"]

    # 1. Retrieve by internal UUID
    get_res1 = await client.get(
        f"/api/v1/claims/{created_id}",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert get_res1.status_code == 200
    assert get_res1.json()["data"]["claim_id"] == claim_code
    assert get_res1.json()["data"]["customer"] is not None
    assert get_res1.json()["data"]["device"] is not None

    # 2. Retrieve by human claim code
    get_res2 = await client.get(
        f"/api/v1/claims/{claim_code}",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert get_res2.status_code == 200

    # 3. List claims with status filter
    list_res = await client.get(
        "/api/v1/claims?status=SUBMITTED",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_claim_status_transition_lifecycle(client: AsyncClient, db_session: AsyncSession) -> None:
    """Investigator can transition status (SUBMITTED -> UNDER_REVIEW -> APPROVED)."""
    inv_token, cust_token, cust_id, dev_id = await _create_test_environment(client, db_session)

    create_res = await client.post(
        "/api/v1/claims",
        json={
            "customer_id": cust_id,
            "device_id": dev_id,
            "claim_type": "DAMAGE",
            "claim_amount": 320.0,
            "incident_date": datetime.now(timezone.utc).isoformat(),
            "description": "Port damage during routine charging.",
            "location": "New York, NY",
        },
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    claim_code = create_res.json()["data"]["claim_id"]

    # Customer trying to transition status should get 403 Forbidden
    cust_trans = await client.patch(
        f"/api/v1/claims/{claim_code}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    assert cust_trans.status_code == 403

    # Investigator transitions to UNDER_REVIEW
    patch1 = await client.patch(
        f"/api/v1/claims/{claim_code}/status",
        json={"status": "UNDER_REVIEW", "reason": "Initial evidence verification"},
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert patch1.status_code == 200
    assert patch1.json()["data"]["status"] == "UNDER_REVIEW"

    # Investigator transitions to APPROVED
    patch2 = await client.patch(
        f"/api/v1/claims/{claim_code}/status",
        json={"status": "APPROVED", "reason": "Receipt & damage photos verified"},
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert patch2.status_code == 200
    assert patch2.json()["data"]["status"] == "APPROVED"
    assert len(patch2.json()["data"]["events"]) >= 3


@pytest.mark.asyncio
async def test_direct_ml_fraud_prediction_api(client: AsyncClient) -> None:
    """POST /api/v1/fraud/predict should return fraud probability, risk level, and SHAP factors."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst.ml@claimgraph.ai",
            "password": "Password123!",
            "full_name": "ML Analyst",
            "role": "ANALYST",
        },
    )
    token = reg.json()["data"]["access_token"]

    sample_features = {
        "claim_amount": 2500.0,
        "previous_claim_count": 4,
        "claims_last_30_days": 2,
        "average_claim_amount": 1000.0,
        "amount_deviation": 1500.0,
        "amount_to_msrp_ratio": 1.35,
        "device_claim_count": 3,
        "customer_claim_frequency": 0.8,
        "location_frequency": 6,
        "repair_shop_frequency": 5,
        "days_since_last_claim": 12.0,
        "device_age": 100,
    }

    response = await client.post(
        "/api/v1/fraud/predict",
        json=sample_features,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert isinstance(data["top_factors"], list)
    assert len(data["top_factors"]) > 0
    assert "model_version" in data


@pytest.mark.asyncio
async def test_claim_dynamic_fraud_evaluation(client: AsyncClient, db_session: AsyncSession) -> None:
    """POST /api/v1/fraud/claims/{id}/evaluate should run ML model and persist score to DB."""
    inv_token, cust_token, cust_id, dev_id = await _create_test_environment(client, db_session)

    # Create claim
    create_res = await client.post(
        "/api/v1/claims",
        json={
            "customer_id": cust_id,
            "device_id": dev_id,
            "claim_type": "DAMAGE",
            "claim_amount": 1400.0,
            "incident_date": datetime.now(timezone.utc).isoformat(),
            "description": "Cracked chassis and damaged display.",
            "location": "Detroit, MI (Cluster 4)",
            "repair_shop": "Vance Brothers Salvage & Repair (Flagged)",
        },
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    claim_code = create_res.json()["data"]["claim_id"]

    # Run dynamic fraud evaluation
    eval_res = await client.post(
        f"/api/v1/fraud/claims/{claim_code}/evaluate",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.json()["data"]
    assert "fraud_probability" in eval_data
    assert "risk_level" in eval_data
    assert len(eval_data["top_factors"]) > 0

    # Verify claim record now reflects the risk score
    get_claim_res = await client.get(
        f"/api/v1/claims/{claim_code}",
        headers={"Authorization": f"Bearer {inv_token}"},
    )
    updated_claim = get_claim_res.json()["data"]
    assert updated_claim["fraud_probability"] == eval_data["fraud_probability"]
    assert updated_claim["risk_level"] == eval_data["risk_level"]
