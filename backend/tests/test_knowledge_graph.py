"""
ClaimGraph AI — Knowledge Graph & Graph Risk Analytics Tests.
"""

import pytest
from app.graph.models import GraphNodeType, GraphRelationType
from app.graph.service import KnowledgeGraphService


@pytest.mark.asyncio
async def test_knowledge_graph_sync_and_subgraph():
    """Verify entity synchronization and subgraph extraction."""
    service = KnowledgeGraphService()

    # Sync a claim
    await service.sync_claim_entities(
        claim_id="CLM-TEST-001",
        customer_id="cust-123",
        customer_name="Alice Smith",
        device_id="dev-456",
        device_serial="SN-ALICE-99",
        product_name="Titan Pro Smartphone",
        claim_type="DAMAGE",
        claim_amount=850.0,
        location_name="New York, NY",
        repair_shop_name="Metro Tech Express",
        customer_email="alice@example.com",
    )

    # Subgraph retrieval
    subgraph = await service.get_claim_subgraph("CLM-TEST-001", hops=2)
    assert subgraph.node_count >= 5
    assert subgraph.link_count >= 4

    node_labels = [n.label for n in subgraph.nodes]
    assert "Alice Smith" in node_labels
    assert "Titan Pro Smartphone" in node_labels
    assert "Metro Tech Express" in node_labels


@pytest.mark.asyncio
async def test_graph_risk_calculation_isolated_vs_shared():
    """Verify graph risk scoring distinguishes isolated claims from shared-device rings."""
    service = KnowledgeGraphService()

    # 1. Single isolated claim
    await service.sync_claim_entities(
        claim_id="CLM-ISOLATED-1",
        customer_id="cust-iso-1",
        customer_name="Bob Jones",
        device_id="dev-iso-1",
        device_serial="SN-ISO-1",
        product_name="ApexBook 16",
        claim_type="MALFUNCTION",
        claim_amount=400.0,
        location_name="Denver, CO",
    )
    iso_risk = await service.calculate_graph_risk("CLM-ISOLATED-1")
    assert iso_risk.graph_risk_score < 0.25
    assert not iso_risk.shared_device_detected

    # 2. Collusion ring: Multiple customers claiming the EXACT same device
    await service.sync_claim_entities(
        claim_id="CLM-RING-A",
        customer_id="cust-ring-1",
        customer_name="Colluder One",
        device_id="dev-shared-HOT",
        device_serial="SN-FRAUD-RING-777",
        product_name="Titan Pro Smartphone",
        claim_type="DAMAGE",
        claim_amount=1200.0,
        location_name="Las Vegas, NV",
        repair_shop_name="Vance Brothers Salvage",
    )
    await service.sync_claim_entities(
        claim_id="CLM-RING-B",
        customer_id="cust-ring-2",
        customer_name="Colluder Two",
        device_id="dev-shared-HOT",
        device_serial="SN-FRAUD-RING-777",
        product_name="Titan Pro Smartphone",
        claim_type="THEFT",
        claim_amount=1200.0,
        location_name="Las Vegas, NV",
        repair_shop_name="Vance Brothers Salvage",
    )

    ring_risk = await service.calculate_graph_risk("CLM-RING-B")
    assert ring_risk.graph_risk_score >= 0.35
    assert ring_risk.shared_device_detected is True
    assert any("associated with" in ev for ev in ring_risk.evidence)


@pytest.mark.asyncio
async def test_graph_analytics_queries():
    """Verify queries for shared devices, suspicious shops, and clusters."""
    service = KnowledgeGraphService()

    # Query shared devices
    shared_devs = await service.query_shared_devices()
    assert isinstance(shared_devs, list)

    # Query clusters
    clusters = await service.query_claim_clusters()
    assert isinstance(clusters, list)
