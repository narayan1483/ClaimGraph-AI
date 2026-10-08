"""
ClaimGraph AI — Graph Models & Schemas.

Pydantic schemas for Neo4j Knowledge Graph nodes, relationships,
subgraph responses, and graph analytics risk scores.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodeType(str, Enum):
    """Knowledge Graph node types."""

    CUSTOMER = "Customer"
    DEVICE = "Device"
    PRODUCT = "Product"
    CLAIM = "Claim"
    TRANSACTION = "Transaction"
    REPAIR_SHOP = "RepairShop"
    LOCATION = "Location"
    POLICY = "Policy"
    DOCUMENT = "Document"


class GraphRelationType(str, Enum):
    """Knowledge Graph relationship types."""

    CUSTOMER_OWNS_DEVICE = "CUSTOMER_OWNS_DEVICE"
    CUSTOMER_SUBMITTED_CLAIM = "CUSTOMER_SUBMITTED_CLAIM"
    DEVICE_HAS_CLAIM = "DEVICE_HAS_CLAIM"
    CUSTOMER_HAS_TRANSACTION = "CUSTOMER_HAS_TRANSACTION"
    CLAIM_ASSOCIATED_WITH_LOCATION = "CLAIM_ASSOCIATED_WITH_LOCATION"
    CLAIM_ASSIGNED_TO_REPAIR_SHOP = "CLAIM_ASSIGNED_TO_REPAIR_SHOP"
    DEVICE_CLAIMED_BY_CUSTOMER = "DEVICE_CLAIMED_BY_CUSTOMER"
    CLAIM_HAS_DOCUMENT = "CLAIM_HAS_DOCUMENT"


class GraphNode(BaseModel):
    """Represents a node in the graph visualization."""

    id: str = Field(..., description="Unique node ID in graph")
    label: str = Field(..., description="Primary display label")
    type: GraphNodeType = Field(..., description="Node label/category")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary attributes")
    risk_level: Optional[str] = Field(None, description="LOW, MEDIUM, HIGH, CRITICAL if applicable")


class GraphLink(BaseModel):
    """Represents an edge / relationship in the graph visualization."""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Relationship label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge attributes")


class GraphDataResponse(BaseModel):
    """Complete graph or subgraph response suitable for frontend D3 / ForceGraph rendering."""

    nodes: List[GraphNode] = Field(default_factory=list)
    links: List[GraphLink] = Field(default_factory=list)
    node_count: int = 0
    link_count: int = 0
    claim_id: Optional[str] = None


class GraphRiskSignal(BaseModel):
    """Individual graph indicator contributing to the graph risk score."""

    name: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    evidence: str
    score_impact: float


class GraphRiskResult(BaseModel):
    """Graph-based fraud signals and risk score."""

    claim_id: str
    graph_risk_score: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0 graph risk score")
    degree: int = 0
    centrality: float = 0.0
    connected_cluster_size: int = 1
    shared_device_detected: bool = False
    shared_location_detected: bool = False
    suspicious_repair_shop_detected: bool = False
    repeat_claim_velocity_detected: bool = False
    evidence: List[str] = Field(default_factory=list, description="Human-readable evidence statements")
    signals: List[GraphRiskSignal] = Field(default_factory=list)
