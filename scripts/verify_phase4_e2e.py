"""
ClaimGraph AI — Phase 4 End-to-End Local Intelligence Verification Script.

Executes a complete real-world scenario:
1. Registers Investigator & Policyholder.
2. Creates an insured Device and submits a high-risk claim.
3. Triggers the 8-Agent LangGraph investigation pipeline (POST /api/v1/investigations/{claim_id}/run).
4. Fetches real Knowledge Graph data (GET /api/v1/graph/claim/{claim_id}).
5. Queries RAG policy intelligence (POST /api/v1/rag/query).
6. Displays the synthesized dossier, multi-agent findings, and deterministic hybrid risk score.
7. Simulates Human Investigator Adjudication (POST /api/v1/investigations/{id}/decision).
"""

import json
import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"


def main():
    print("=" * 70)
    print("CLAIMGRAPH AI — PHASE 4 CORE AI INTELLIGENCE VERIFICATION")
    print("=" * 70)

    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # 1. Health check
    try:
        health_resp = client.get("/health")
        print(f"[1] Backend Health Check: HTTP {health_resp.status_code}")
    except Exception as e:
        print(f"[!] Could not connect to {BASE_URL}: {e}")
        sys.exit(1)

    # 2. Register Investigator
    inv_email = "lead.investigator.phase4@claimgraph.ai"
    reg_inv_resp = client.post(
        "/auth/register",
        json={
            "email": inv_email,
            "password": "InvestigatorPassword123!",
            "full_name": "Narayan Prasad Maurya (Lead SIU)",
            "role": "INVESTIGATOR",
        },
    )
    if reg_inv_resp.status_code == 201:
        token = reg_inv_resp.json()["data"]["access_token"]
        print(f"[2] Registered Lead Investigator: {inv_email}")
    else:
        # Login if already exists
        login_resp = client.post(
            "/auth/login",
            json={"email": inv_email, "password": "InvestigatorPassword123!"},
        )
        token = login_resp.json()["data"]["access_token"]
        print(f"[2] Logged in existing Investigator: {inv_email}")

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Register Claimant
    cust_email = "claimant.phase4.suspicious@example.com"
    reg_cust_resp = client.post(
        "/auth/register",
        json={
            "email": cust_email,
            "password": "ClaimantPassword123!",
            "full_name": "Marcus Vance",
            "role": "CUSTOMER",
        },
    )
    if reg_cust_resp.status_code == 201:
        cust_user_id = reg_cust_resp.json()["data"]["user"]["id"]
    else:
        login_c = client.post("/auth/login", json={"email": cust_email, "password": "ClaimantPassword123!"}).json()["data"]
        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {login_c['access_token']}"})
        cust_user_id = me_resp.json()["data"]["id"]
    print(f"[3] Claimant Profile Verified: {cust_email} (ID: {cust_user_id})")

    # Get Customer entity ID
    cust_token = client.post("/auth/login", json={"email": cust_email, "password": "ClaimantPassword123!"}).json()["data"]["access_token"]
    me_cust = client.get("/auth/me", headers={"Authorization": f"Bearer {cust_token}"}).json()["data"]
    customer_id = me_cust.get("customer_profile", {}).get("id")

    # 4. Create Insured Device
    dev_resp = client.post(
        "/devices",
        headers=headers,
        json={
            "serial_number": "SN-PHASE4-TITAN-9902",
            "product_name": "Titan Pro Smartphone 256GB",
            "purchase_price": 1299.0,
            "category": "Electronics",
            "manufacturer": "Titan Mobile",
            "model_number": "TP-256",
        },
    )
    device_id = dev_resp.json()["data"]["id"]
    print(f"[4] Insured Device Registered: SN-PHASE4-TITAN-9902 (ID: {device_id})")

    # 5. Submit Suspicious Claim
    claim_payload = {
        "customer_id": customer_id,
        "device_id": device_id,
        "claim_type": "DAMAGE",
        "claim_amount": 2750.0,  # Exaggerated damage amount
        "incident_date": "2026-09-25T11:00:00Z",
        "description": "Dropped phone on marble counter. Screen cracked, motherboard fractured, water ingress reported.",
        "location": "Las Vegas, NV (High Risk Zone)",
        "repair_shop": "Vance Brothers Salvage & Repair (Flagged)",
    }
    claim_resp = client.post("/claims", headers=headers, json=claim_payload)
    claim_data = claim_resp.json()["data"]
    claim_id = claim_data["claim_id"]
    print(f"[5] Test Claim Created: #{claim_id} | Amount: ${claim_data['claim_amount']:,.2f}")

    # 6. Execute LangGraph AI Investigation
    print("\n" + "=" * 70)
    print(f"[6] RUNNING AI INVESTIGATION: POST /api/v1/investigations/{claim_id}/run")
    print("=" * 70)
    inv_resp = client.post(f"/investigations/{claim_id}/run", headers=headers)
    inv_data = inv_resp.json()

    print(f"Investigation ID     : {inv_data['investigation_id']}")
    print(f"ML Fraud Score       : {inv_data['fraud_score']:.1%}")
    print(f"Graph Risk Score     : {inv_data['graph_score']:.1%}")
    print(f"Final Risk Score     : {inv_data['final_risk_score']:.2f} / 1.00")
    print(f"Assigned Risk Level  : {inv_data['risk_level']}")
    print(f"Recommended Action   : {inv_data['recommendation']}")

    # 7. Knowledge Graph Query
    print("\n" + "=" * 70)
    print(f"[7] REAL KNOWLEDGE GRAPH DATA: GET /api/v1/graph/claim/{claim_id}")
    print("=" * 70)
    graph_resp = client.get(f"/graph/claim/{claim_id}", headers=headers)
    g_data = graph_resp.json()
    print(f"Total Nodes In Graph : {g_data['node_count']}")
    print(f"Total Edges In Graph : {g_data['link_count']}")
    print("Sample Nodes:")
    for n in g_data["nodes"][:4]:
        print(f"  • [{n['type']}] {n['label']} (ID: {n['id']})")
    print("Sample Relationships:")
    for link in g_data["links"][:4]:
        print(f"  • {link['source']} ---({link['type']})---> {link['target']}")

    # 8. RAG Policy Intelligence Query
    print("\n" + "=" * 70)
    print("[8] RAG POLICY INTELLIGENCE: POST /api/v1/rag/query")
    print("=" * 70)
    rag_query = "What are the escalation triggers for claims with ML probability over 0.70 or high risk?"
    rag_resp = client.post(
        "/rag/query",
        json={"query": rag_query, "claim_id": claim_id},
    )
    rag_data = rag_resp.json()
    print(f"Inquiry        : {rag_data['query']}")
    print(f"Sources Cited  : {', '.join(rag_data['sources'])}")
    print(f"Latency        : {rag_data['latency_ms']} ms | Tokens: {rag_data['token_usage']['total_tokens']}")
    print(f"Grounded Answer:\n{rag_data['answer']}")

    # 9. AI Investigation Dossier
    print("\n" + "=" * 70)
    print("[9] SYNTHESIZED MULTI-AGENT INVESTIGATION REPORT")
    print("=" * 70)
    print(inv_data["investigation_report"])

    # 10. Human Investigator Adjudication
    print("\n" + "=" * 70)
    print(f"[10] HUMAN INVESTIGATOR DECISION: POST /api/v1/investigations/{inv_data['investigation_id']}/decision")
    print("=" * 70)
    decision_resp = client.post(
        f"/investigations/{inv_data['investigation_id']}/decision",
        headers=headers,
        json={
            "decision": "ESCALATE",
            "notes": "Escalated to Special Investigation Unit (SIU) due to flagged repair shop Vance Brothers and elevated hybrid risk score.",
            "badge_number": "SIU-LEAD-NARAYAN-901",
        },
    )
    dec_data = decision_resp.json()
    print(f"Adjudication Result  : {dec_data['decision']}")
    print(f"New Claim Status     : {dec_data['new_claim_status']}")
    print(f"Confirmation Message : {dec_data['message']}")
    print(f"Timestamp            : {dec_data['decided_at']}")

    print("\n" + "=" * 70)
    print("PHASE 4 VERIFICATION COMPLETED WITH ZERO ERRORS!")
    print("=" * 70)


if __name__ == "__main__":
    main()
