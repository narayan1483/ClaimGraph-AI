"""
ClaimGraph AI — Knowledge Graph API Router.

Endpoints for subgraph visualization, graph risk scoring, and entity synchronization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.claims.models import Claim
from app.claims.repository import ClaimRepository
from app.core.database import get_db
from app.customers.models import Customer
from app.devices.models import Device, Product
from app.graph.models import GraphDataResponse, GraphRiskResult
from app.graph.service import KnowledgeGraphService, get_graph_service
from app.users.models import User
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


async def _ensure_claim_synced_to_graph(
    db: AsyncSession, claim_identifier: str, graph_service: KnowledgeGraphService
) -> Optional[Claim]:
    """Helper to fetch claim from DB and ensure it is indexed in the graph."""
    # Find claim
    claim: Optional[Claim] = None
    if claim_identifier.upper().startswith("CLM-"):
        claim = await ClaimRepository.get_by_claim_id(db, claim_identifier)
    else:
        claim = await ClaimRepository.get_by_id(db, claim_identifier)

    if not claim:
        return None

    # Fetch customer & device with relations
    stmt_cust = select(Customer).options(selectinload(Customer.user)).where(Customer.id == claim.customer_id)
    cust_res = await db.execute(stmt_cust)
    customer = cust_res.scalar_one_or_none()

    stmt_dev = select(Device).options(selectinload(Device.product)).where(Device.id == claim.device_id)
    dev_res = await db.execute(stmt_dev)
    device = dev_res.scalar_one_or_none()

    cust_name = customer.user.full_name if (customer and customer.user) else "Unknown Claimant"
    cust_phone = customer.phone_number if customer else None
    cust_email = customer.user.email if (customer and customer.user) else None
    dev_serial = device.serial_number if device else "SN-UNKNOWN"
    prod_name = device.product.name if (device and device.product) else "Electronic Asset"

    await graph_service.sync_claim_entities(
        claim_id=claim.claim_id,
        customer_id=claim.customer_id,
        customer_name=cust_name,
        device_id=claim.device_id,
        device_serial=dev_serial,
        product_name=prod_name,
        claim_type=claim.claim_type.value if hasattr(claim.claim_type, "value") else str(claim.claim_type),
        claim_amount=claim.claim_amount,
        location_name=claim.location or "Default Region",
        repair_shop_name=claim.repair_shop,
        customer_phone=cust_phone,
        customer_email=cust_email,
        document_names=["Proof_of_Loss_Invoice.pdf", "Diagnostic_Estimate.pdf"],
    )

    return claim


@router.get("/claim/{claim_id}", response_model=GraphDataResponse)
async def get_claim_graph(
    claim_id: str,
    hops: int = Query(default=2, ge=1, le=4, description="Graph traversal hops"),
    db: AsyncSession = Depends(get_db),
    graph_service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> GraphDataResponse:
    """
    Retrieve real Neo4j/topology knowledge graph nodes and relationships for a claim.
    Returns format directly visualizable in frontend graph components.
    """
    claim = await _ensure_claim_synced_to_graph(db, claim_id, graph_service)
    target_id = claim.claim_id if claim else claim_id

    subgraph = await graph_service.get_claim_subgraph(target_id, hops=hops)
    return subgraph


@router.get("/risk/{claim_id}", response_model=GraphRiskResult)
async def get_claim_graph_risk(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    graph_service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> GraphRiskResult:
    """
    Calculate graph risk score and extract human-readable graph evidence
    (e.g., shared devices, repeat claims, suspicious repair shops, fraud ring clusters).
    """
    claim = await _ensure_claim_synced_to_graph(db, claim_id, graph_service)
    target_id = claim.claim_id if claim else claim_id

    risk_result = await graph_service.calculate_graph_risk(target_id)
    return risk_result


@router.post("/sync/{claim_id}")
async def sync_claim_to_graph(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    graph_service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """Manually sync a claim and related entities into the knowledge graph."""
    claim = await _ensure_claim_synced_to_graph(db, claim_id, graph_service)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Claim {claim_id} not found in database")

    return {
        "status": "success",
        "message": f"Claim {claim.claim_id} synchronized to Neo4j knowledge graph.",
        "claim_id": claim.claim_id,
    }


@router.get("/analytics/clusters")
async def get_graph_clusters(
    graph_service: KnowledgeGraphService = Depends(get_graph_service),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """Return suspicious entity clusters and shared devices across the network."""
    clusters = await graph_service.query_claim_clusters()
    shared_devices = await graph_service.query_shared_devices()
    suspicious_shops = await graph_service.query_suspicious_repair_shops()

    return {
        "clusters": clusters,
        "shared_devices": shared_devices,
        "suspicious_repair_shops": suspicious_shops,
    }
