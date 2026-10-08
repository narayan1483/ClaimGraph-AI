"""
ClaimGraph AI — LangGraph Agents, Risk Engine & Investigation API Tests.
"""

import pytest
from httpx import AsyncClient

from app.agents.state import InvestigationState
from app.agents.workflow import run_investigation_workflow
from app.risk.engine import DeterministicHybridRiskEngine


def test_deterministic_hybrid_risk_engine():
    """Verify deterministic risk scoring formulas and evidence categorization."""
    # 1. Low risk scenario
    low_out = DeterministicHybridRiskEngine.evaluate(
        ml_fraud_prob=0.08,
        graph_risk_score=0.05,
        doc_inconsistent=False,
        vision_inconsistent=False,
        policy_inconsistent=False,
        prior_claims_count=0,
        claim_amount=350.0,
    )
    assert low_out.final_risk_score < 0.30
    assert low_out.risk_level == "LOW"
    assert low_out.recommended_action == "NORMAL_PROCESSING"

    # 2. Critical risk scenario
    crit_out = DeterministicHybridRiskEngine.evaluate(
        ml_fraud_prob=0.88,
        graph_risk_score=0.75,
        doc_inconsistent=True,
        vision_inconsistent=True,
        policy_inconsistent=True,
        prior_claims_count=4,
        claim_amount=2800.0,
        doc_evidence=["Invoice estimate diverges from verified parts cost."],
        vision_evidence=["Observed severe shatter damage contradicts minor scratch narrative."],
    )
    assert crit_out.final_risk_score >= 0.70
    assert crit_out.risk_level in ["HIGH", "CRITICAL"]
    assert crit_out.recommended_action == "INVESTIGATION"

    # Verify evidence categories
    categories = set(e.category for e in crit_out.evidence)
    assert "FACT" in categories
    assert "ML SIGNAL" in categories
    assert "GRAPH SIGNAL" in categories
    assert "AI ANALYSIS" in categories
    assert "RECOMMENDATION" in categories


@pytest.mark.asyncio
async def test_langgraph_multi_agent_workflow_execution():
    """Verify end-to-end execution of the 8-agent LangGraph workflow."""
    initial_state: InvestigationState = {
        "claim_id": "CLM-AG-TEST-001",
        "claim_data": {
            "claim_id": "CLM-AG-TEST-001",
            "claim_amount": 1200.0,
            "claim_type": "DAMAGE",
            "incident_date": "2026-09-20T10:00:00Z",
            "description": "Dropped laptop while traveling. Screen cracked and chassis warped.",
            "location": "Chicago, IL",
            "repair_shop": "Metro Tech Express",
        },
        "customer_data": {
            "customer_id": "cust-ag-1",
            "full_name": "Test Customer",
            "email": "test@example.com",
            "account_age_days": 240,
        },
        "device_data": {
            "device_id": "dev-ag-1",
            "serial_number": "SN-LAPTOP-909",
            "product_name": "ApexBook 16-inch Laptop",
            "purchase_price": 2400.0,
        },
        "prior_claims_count": 0,
        "agent_results": {},
        "errors": [],
        "retry_counts": {},
    }

    final_state = await run_investigation_workflow(initial_state)

    # Verify all 8 agents executed
    results = final_state.get("agent_results", {})
    expected_agents = [
        "Claim Understanding Agent",
        "Document Analysis Agent",
        "Vision Analysis Agent",
        "Fraud Analysis Agent",
        "Graph Investigation Agent",
        "Policy/RAG Agent",
        "Risk Analysis Agent",
        "Investigation Report Agent",
    ]
    for agent in expected_agents:
        assert agent in results, f"Missing result for {agent}"
        assert results[agent]["status"] == "SUCCESS"
        assert results[agent]["confidence"] > 0.5
        assert len(results[agent]["evidence"]) > 0

    assert final_state["human_review_required"] is True
    assert final_state["is_completed"] is True
    assert len(final_state["investigation_report"]) > 100


@pytest.mark.asyncio
async def test_investigation_api_run_and_decision(client: AsyncClient, db_session):
    """Verify investigation API end-to-end run, retrieval, and decision endpoints."""
    from datetime import datetime, timezone
    from sqlalchemy import select
    from app.customers.models import Customer
    from app.devices.models import Device, Product

    # 1. Register investigator
    inv_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "lead.inv.test@claimgraph.ai",
            "password": "Password123!",
            "full_name": "Lead Investigator",
            "role": "INVESTIGATOR",
        },
    )
    assert inv_reg.status_code == 201
    inv_token = inv_reg.json()["data"]["access_token"]
    user_headers = {"Authorization": f"Bearer {inv_token}"}

    # 2. Register customer
    cust_reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "claimant.investigation@example.com",
            "password": "Password123!",
            "full_name": "Dave Claimant",
            "role": "CUSTOMER",
        },
    )
    assert cust_reg.status_code == 201
    cust_user_id = cust_reg.json()["data"]["user"]["id"]

    # 3. Create Product & Device
    prod = Product(
        name="Titan Pro Smartphone 256GB",
        category="Electronics",
        manufacturer="Titan Mobile",
        model_number="TP-256",
        msrp=1200.0,
    )
    db_session.add(prod)
    await db_session.flush()

    cust_obj = (
        await db_session.execute(select(Customer).where(Customer.user_id == cust_user_id))
    ).scalar_one()

    dev = Device(
        serial_number="SN-INV-TEST-001",
        product_id=prod.id,
        customer_id=cust_obj.id,
        purchase_date=datetime.now(timezone.utc),
        purchase_price=1199.0,
        status="ACTIVE",
    )
    db_session.add(dev)
    await db_session.commit()

    # 4. Create Claim
    claim_res = await client.post(
        "/api/v1/claims",
        headers=user_headers,
        json={
            "customer_id": cust_obj.id,
            "device_id": dev.id,
            "claim_type": "DAMAGE",
            "claim_amount": 450.0,
            "incident_date": "2026-09-10T14:30:00Z",
            "description": "Screen cracked when slipped off desk.",
            "location": "New York, NY",
            "repair_shop": "Metro Tech Express",
        },
    )
    assert claim_res.status_code == 201
    claim_data = claim_res.json()["data"]
    claim_id = claim_data["claim_id"]

    # 5. Run AI investigation
    run_res = await client.post(f"/api/v1/investigations/{claim_id}/run", headers=user_headers)
    assert run_res.status_code == 200
    inv_data = run_res.json()
    assert inv_data["claim_id"] == claim_id
    assert "investigation_id" in inv_data
    assert "final_risk_score" in inv_data
    assert "risk_level" in inv_data
    assert "recommendation" in inv_data
    assert len(inv_data["agent_results"]) == 8
    assert len(inv_data["investigation_report"]) > 0

    # 6. Retrieve existing investigation
    get_res = await client.get(f"/api/v1/investigations/{claim_id}", headers=user_headers)
    assert get_res.status_code == 200
    assert get_res.json()["investigation_id"] == inv_data["investigation_id"]


    # 3. Human investigator adjudication decision
    inv_id = inv_data["investigation_id"]
    dec_res = await client.post(
        f"/api/v1/investigations/{inv_id}/decision",
        headers=user_headers,
        json={
            "decision": "APPROVE",
            "notes": "Verified genuine accidental impact damage and authorized OEM repairer.",
            "badge_number": "INV-LEAD-7741",
        },
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["decision"] == "APPROVE"
    assert dec_res.json()["new_claim_status"] == "APPROVED"
