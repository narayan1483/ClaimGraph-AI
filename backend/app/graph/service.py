"""
ClaimGraph AI — Knowledge Graph Service.

Neo4j driver integration with in-memory NetworkX graph topology engine.
Provides node/edge synchronization, Cypher queries, graph risk scoring,
and subgraph extraction for frontend interactive visualization.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
from neo4j import AsyncGraphDatabase, AsyncDriver

from app.core.config import get_settings
from app.graph.models import (
    GraphDataResponse,
    GraphLink,
    GraphNode,
    GraphNodeType,
    GraphRelationType,
    GraphRiskResult,
    GraphRiskSignal,
)

logger = logging.getLogger("claimgraph.graph")


class KnowledgeGraphService:
    """Manages knowledge graph storage, queries, and analytics."""

    _instance: Optional["KnowledgeGraphService"] = None

    def __init__(self) -> None:
        self.settings = get_settings()
        self._driver: Optional[AsyncDriver] = None
        # High-performance in-memory graph for topological analytics and offline fallback
        self._nx_graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._neo4j_available: bool = False

    @classmethod
    def get_instance(cls) -> "KnowledgeGraphService":
        if cls._instance is None:
            cls._instance = KnowledgeGraphService()
        return cls._instance

    async def connect(self) -> None:
        """Attempt connection to Neo4j database."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password),
                max_connection_lifetime=3600,
            )
            # Verify connectivity
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 AS connected")
                record = await result.single()
                if record and record["connected"] == 1:
                    self._neo4j_available = True
                    logger.info("Connected successfully to Neo4j at %s", self.settings.neo4j_uri)
                    await self._init_constraints(session)
        except Exception as exc:
            self._neo4j_available = False
            logger.warning(
                "Neo4j connection unavailable (%s). Operating with in-memory topological graph engine.",
                exc,
            )

    async def close(self) -> None:
        """Close Neo4j connection pool."""
        if self._driver:
            await self._driver.close()
            self._neo4j_available = False

    async def _init_constraints(self, session: Any) -> None:
        """Ensure uniqueness constraints on key nodes."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (cl:Claim) REQUIRE cl.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (rs:RepairShop) REQUIRE rs.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (loc:Location) REQUIRE loc.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pol:Policy) REQUIRE pol.id IS UNIQUE",
        ]
        for query in constraints:
            try:
                await session.run(query)
            except Exception as e:
                logger.debug("Constraint init notice: %s", e)

    # ── NODE & EDGE SYNCHRONIZATION ──────────────────────────────

    def add_node_to_memory(
        self,
        node_id: str,
        node_type: GraphNodeType,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        risk_level: Optional[str] = None,
    ) -> None:
        """Add or update node in memory graph."""
        props = properties or {}
        self._nx_graph.add_node(
            node_id,
            id=node_id,
            label=label,
            type=node_type.value if isinstance(node_type, GraphNodeType) else str(node_type),
            properties=props,
            risk_level=risk_level,
        )

    def add_edge_to_memory(
        self,
        source: str,
        target: str,
        relation_type: GraphRelationType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add edge in memory graph."""
        props = properties or {}
        rel_str = relation_type.value if isinstance(relation_type, GraphRelationType) else str(relation_type)
        self._nx_graph.add_edge(source, target, key=rel_str, type=rel_str, properties=props)

    async def sync_claim_entities(
        self,
        claim_id: str,
        customer_id: str,
        customer_name: str,
        device_id: str,
        device_serial: str,
        product_name: str,
        claim_type: str,
        claim_amount: float,
        location_name: str,
        repair_shop_name: Optional[str] = None,
        policy_id: Optional[str] = None,
        document_names: Optional[List[str]] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> None:
        """
        Synchronize a full claim entity set into both Neo4j and the in-memory graph.
        Establishes all 8 standard relationships.
        """
        cust_node_id = f"cust_{customer_id}"
        dev_node_id = f"dev_{device_id}"
        prod_node_id = f"prod_{product_name.replace(' ', '_').lower()}"
        claim_node_id = f"claim_{claim_id}"
        loc_node_id = f"loc_{location_name.replace(' ', '_').lower()}"
        shop_node_id = f"shop_{repair_shop_name.replace(' ', '_').lower()}" if repair_shop_name else None
        pol_node_id = f"pol_{policy_id}" if policy_id else f"pol_std_{cust_node_id}"

        # 1. Update in-memory graph
        self.add_node_to_memory(
            cust_node_id,
            GraphNodeType.CUSTOMER,
            label=customer_name,
            properties={"customer_id": customer_id, "phone": customer_phone, "email": customer_email},
        )
        self.add_node_to_memory(
            dev_node_id,
            GraphNodeType.DEVICE,
            label=f"Device ({device_serial})",
            properties={"device_id": device_id, "serial_number": device_serial},
        )
        self.add_node_to_memory(
            prod_node_id,
            GraphNodeType.PRODUCT,
            label=product_name,
            properties={"name": product_name},
        )
        self.add_node_to_memory(
            claim_node_id,
            GraphNodeType.CLAIM,
            label=f"Claim #{claim_id[:8]}",
            properties={"claim_id": claim_id, "amount": claim_amount, "claim_type": claim_type},
        )
        self.add_node_to_memory(
            loc_node_id,
            GraphNodeType.LOCATION,
            label=location_name,
            properties={"location": location_name},
        )
        self.add_node_to_memory(
            pol_node_id,
            GraphNodeType.POLICY,
            label=f"Policy ({pol_node_id[-8:]})",
            properties={"policy_id": pol_node_id},
        )

        # Edges
        self.add_edge_to_memory(cust_node_id, dev_node_id, GraphRelationType.CUSTOMER_OWNS_DEVICE)
        self.add_edge_to_memory(cust_node_id, claim_node_id, GraphRelationType.CUSTOMER_SUBMITTED_CLAIM)
        self.add_edge_to_memory(dev_node_id, claim_node_id, GraphRelationType.DEVICE_HAS_CLAIM)
        self.add_edge_to_memory(dev_node_id, cust_node_id, GraphRelationType.DEVICE_CLAIMED_BY_CUSTOMER)
        self.add_edge_to_memory(dev_node_id, prod_node_id, "DEVICE_OF_PRODUCT")
        self.add_edge_to_memory(claim_node_id, loc_node_id, GraphRelationType.CLAIM_ASSOCIATED_WITH_LOCATION)


        if shop_node_id and repair_shop_name:
            self.add_node_to_memory(
                shop_node_id,
                GraphNodeType.REPAIR_SHOP,
                label=repair_shop_name,
                properties={"name": repair_shop_name},
            )
            self.add_edge_to_memory(claim_node_id, shop_node_id, GraphRelationType.CLAIM_ASSIGNED_TO_REPAIR_SHOP)

        if document_names:
            for doc_name in document_names:
                doc_node_id = f"doc_{claim_id}_{doc_name.replace(' ', '_').lower()}"
                self.add_node_to_memory(
                    doc_node_id,
                    GraphNodeType.DOCUMENT,
                    label=doc_name,
                    properties={"filename": doc_name, "claim_id": claim_id},
                )
                self.add_edge_to_memory(claim_node_id, doc_node_id, GraphRelationType.CLAIM_HAS_DOCUMENT)

        # 2. Sync to Neo4j if available
        if self._neo4j_available and self._driver:
            try:
                cypher_query = """
                MERGE (c:Customer {id: $cust_id})
                SET c.name = $cust_name, c.phone = $cust_phone, c.email = $cust_email
                MERGE (d:Device {id: $dev_id})
                SET d.serial_number = $dev_serial
                MERGE (p:Product {id: $prod_id})
                SET p.name = $prod_name
                MERGE (cl:Claim {id: $claim_id})
                SET cl.claim_id = $claim_id, cl.amount = $amount, cl.claim_type = $claim_type
                MERGE (loc:Location {id: $loc_id})
                SET loc.name = $loc_name

                MERGE (c)-[:CUSTOMER_OWNS_DEVICE]->(d)
                MERGE (c)-[:CUSTOMER_SUBMITTED_CLAIM]->(cl)
                MERGE (d)-[:DEVICE_HAS_CLAIM]->(cl)
                MERGE (d)-[:DEVICE_CLAIMED_BY_CUSTOMER]->(c)
                MERGE (cl)-[:CLAIM_ASSOCIATED_WITH_LOCATION]->(loc)
                """
                params: Dict[str, Any] = {
                    "cust_id": cust_node_id,
                    "cust_name": customer_name,
                    "cust_phone": customer_phone or "",
                    "cust_email": customer_email or "",
                    "dev_id": dev_node_id,
                    "dev_serial": device_serial,
                    "prod_id": prod_node_id,
                    "prod_name": product_name,
                    "claim_id": claim_node_id,
                    "amount": claim_amount,
                    "claim_type": claim_type,
                    "loc_id": loc_node_id,
                    "loc_name": location_name,
                }
                async with self._driver.session() as session:
                    await session.run(cypher_query, params)

                    if shop_node_id and repair_shop_name:
                        shop_query = """
                        MERGE (rs:RepairShop {id: $shop_id})
                        SET rs.name = $shop_name
                        WITH rs
                        MATCH (cl:Claim {id: $claim_id})
                        MERGE (cl)-[:CLAIM_ASSIGNED_TO_REPAIR_SHOP]->(rs)
                        """
                        await session.run(shop_query, {"shop_id": shop_node_id, "shop_name": repair_shop_name, "claim_id": claim_node_id})
            except Exception as e:
                logger.error("Error executing Neo4j sync for claim %s: %s", claim_id, e)

    # ── SUBGRAPH RETRIEVAL ───────────────────────────────────────

    async def get_claim_subgraph(self, claim_id: str, hops: int = 2) -> GraphDataResponse:
        """
        Extract subgraph around a claim node up to N hops.
        Returns format compatible with interactive frontend visualization.
        """
        claim_node_id = f"claim_{claim_id}" if not claim_id.startswith("claim_") else claim_id

        # Try Neo4j first if available
        if self._neo4j_available and self._driver:
            try:
                query = """
                MATCH path = (cl:Claim {id: $claim_id})-[*1..2]-(m)
                UNWIND nodes(path) AS n
                UNWIND relationships(path) AS r
                RETURN collect(DISTINCT n) AS nodes, collect(DISTINCT r) AS rels
                """
                async with self._driver.session() as session:
                    result = await session.run(query, {"claim_id": claim_node_id})
                    record = await result.single()
                    if record and record["nodes"]:
                        res_nodes: List[GraphNode] = []
                        res_links: List[GraphLink] = []
                        for n in record["nodes"]:
                            labels = list(n.labels)
                            node_type = GraphNodeType(labels[0]) if labels and labels[0] in [e.value for e in GraphNodeType] else GraphNodeType.CLAIM
                            res_nodes.append(
                                GraphNode(
                                    id=n.get("id", str(n.id)),
                                    label=n.get("name") or n.get("serial_number") or n.get("claim_id") or n.get("id"),
                                    type=node_type,
                                    properties=dict(n.items()),
                                )
                            )
                        for r in record["rels"]:
                            res_links.append(
                                GraphLink(
                                    source=r.start_node.get("id", str(r.start_node.id)),
                                    target=r.end_node.get("id", str(r.end_node.id)),
                                    type=r.type,
                                    properties=dict(r.items()),
                                )
                            )
                        return GraphDataResponse(
                            nodes=res_nodes,
                            links=res_links,
                            node_count=len(res_nodes),
                            link_count=len(res_links),
                            claim_id=claim_id,
                        )
            except Exception as e:
                logger.warning("Neo4j query failed, falling back to memory graph: %s", e)

        # Fallback to high-performance NetworkX graph
        return self._extract_memory_subgraph(claim_node_id, hops)

    def _extract_memory_subgraph(self, center_node_id: str, hops: int = 2) -> GraphDataResponse:
        """Extract nodes within N hops using NetworkX."""
        if center_node_id not in self._nx_graph:
            # Return empty response if node not indexed
            return GraphDataResponse(nodes=[], links=[], node_count=0, link_count=0, claim_id=center_node_id)

        # Get ego graph (undirected view for neighborhood discovery)
        undirected_view = self._nx_graph.to_undirected(as_view=True)
        sub_nodes = set(nx.ego_graph(undirected_view, center_node_id, radius=hops).nodes())

        nodes_list: List[GraphNode] = []
        links_list: List[GraphLink] = []

        for nid in sub_nodes:
            data = self._nx_graph.nodes[nid]
            ntype_str = data.get("type", GraphNodeType.CLAIM.value)
            try:
                ntype = GraphNodeType(ntype_str)
            except ValueError:
                ntype = GraphNodeType.CLAIM

            nodes_list.append(
                GraphNode(
                    id=nid,
                    label=data.get("label", nid),
                    type=ntype,
                    properties=data.get("properties", {}),
                    risk_level=data.get("risk_level"),
                )
            )

        for u, v, k, d in self._nx_graph.edges(sub_nodes, data=True, keys=True):
            if u in sub_nodes and v in sub_nodes:
                links_list.append(
                    GraphLink(
                        source=u,
                        target=v,
                        type=d.get("type", str(k)),
                        properties=d.get("properties", {}),
                    )
                )

        return GraphDataResponse(
            nodes=nodes_list,
            links=links_list,
            node_count=len(nodes_list),
            link_count=len(links_list),
            claim_id=center_node_id,
        )

    # ── GRAPH RISK ANALYSIS & FRAUD PATTERN QUERIES ───────────────

    async def calculate_graph_risk(self, claim_id: str) -> GraphRiskResult:
        """
        Calculate deterministic graph risk score and extract human-readable evidence.
        Uses degree centrality, shared entities, repeat frequency, and cluster size.
        """
        claim_node_id = f"claim_{claim_id}" if not claim_id.startswith("claim_") else claim_id

        evidence_list: List[str] = []
        signals_list: List[GraphRiskSignal] = []
        base_risk_score = 0.0

        if claim_node_id not in self._nx_graph:
            # Baseline isolated claim
            return GraphRiskResult(
                claim_id=claim_id,
                graph_risk_score=0.10,
                degree=0,
                centrality=0.0,
                connected_cluster_size=1,
                evidence=["Single isolated claim node with no suspicious entity overlaps."],
                signals=[],
            )

        g = self._nx_graph
        undirected_g = g.to_undirected(as_view=True)

        # 1. Degree & Connected Component Cluster Size
        degree = g.degree(claim_node_id)
        cluster_nodes = nx.node_connected_component(undirected_g, claim_node_id)
        cluster_size = len(cluster_nodes)

        # Degree centrality in local component
        centrality = degree / max(1, cluster_size - 1) if cluster_size > 1 else 0.0

        # Find connected devices, customers, repair shops, locations
        associated_devices: Set[str] = set()
        associated_customers: Set[str] = set()
        associated_repair_shops: Set[str] = set()
        associated_locations: Set[str] = set()

        for neighbor in undirected_g.neighbors(claim_node_id):
            ntype = g.nodes[neighbor].get("type")
            if ntype == GraphNodeType.DEVICE.value:
                associated_devices.add(neighbor)
            elif ntype == GraphNodeType.CUSTOMER.value:
                associated_customers.add(neighbor)
            elif ntype == GraphNodeType.REPAIR_SHOP.value:
                associated_repair_shops.add(neighbor)
            elif ntype == GraphNodeType.LOCATION.value:
                associated_locations.add(neighbor)

        # 2. Check for Shared Devices across multiple customers or claims
        shared_device_detected = False
        for dev in associated_devices:
            dev_claims = [
                n for n in undirected_g.neighbors(dev) if g.nodes[n].get("type") == GraphNodeType.CLAIM.value
            ]
            dev_customers = [
                n for n in undirected_g.neighbors(dev) if g.nodes[n].get("type") == GraphNodeType.CUSTOMER.value
            ]

            dev_label = g.nodes[dev].get("label", dev)
            if len(dev_customers) > 1 or len(dev_claims) > 1:
                shared_device_detected = True
                msg = f"{dev_label} is associated with {len(dev_customers)} customers and {len(dev_claims)} claims."
                evidence_list.append(msg)
                base_risk_score += 0.35
                signals_list.append(
                    GraphRiskSignal(
                        name="SHARED_DEVICE_COLLUSION",
                        severity="HIGH" if len(dev_customers) > 1 else "MEDIUM",
                        evidence=msg,
                        score_impact=0.35,
                    )
                )

        # 3. Check for Repeat Claims by Connected Customer
        repeat_claim_velocity = False
        for cust in associated_customers:
            cust_claims = [
                n for n in undirected_g.neighbors(cust) if g.nodes[n].get("type") == GraphNodeType.CLAIM.value
            ]
            cust_label = g.nodes[cust].get("label", cust)
            if len(cust_claims) >= 3:
                repeat_claim_velocity = True
                msg = f"Customer {cust_label} has submitted {len(cust_claims)} claims in the knowledge graph network."
                evidence_list.append(msg)
                base_risk_score += 0.25
                signals_list.append(
                    GraphRiskSignal(
                        name="HIGH_CLAIM_VELOCITY",
                        severity="HIGH" if len(cust_claims) > 4 else "MEDIUM",
                        evidence=msg,
                        score_impact=0.25,
                    )
                )

        # 4. Check for Suspicious / High-Risk Repair Shop
        suspicious_repair_shop = False
        for shop in associated_repair_shops:
            shop_claims = [
                n for n in undirected_g.neighbors(shop) if g.nodes[n].get("type") == GraphNodeType.CLAIM.value
            ]
            shop_label = g.nodes[shop].get("label", shop)
            if len(shop_claims) >= 3:
                suspicious_repair_shop = True
                msg = f"Repair shop '{shop_label}' is linked to {len(shop_claims)} claims across the network."
                evidence_list.append(msg)
                base_risk_score += 0.20
                signals_list.append(
                    GraphRiskSignal(
                        name="REPAIR_SHOP_ANOMALY",
                        severity="MEDIUM",
                        evidence=msg,
                        score_impact=0.20,
                    )
                )

        # 5. Check for Shared Location with multiple claims
        shared_location = False
        for loc in associated_locations:
            loc_claims = [
                n for n in undirected_g.neighbors(loc) if g.nodes[n].get("type") == GraphNodeType.CLAIM.value
            ]
            loc_label = g.nodes[loc].get("label", loc)
            if len(loc_claims) >= 3:
                shared_location = True
                msg = f"Location '{loc_label}' is shared with {len(loc_claims)} separate claim submissions."
                evidence_list.append(msg)
                base_risk_score += 0.15
                signals_list.append(
                    GraphRiskSignal(
                        name="SHARED_LOCATION_CLUSTER",
                        severity="LOW",
                        evidence=msg,
                        score_impact=0.15,
                    )
                )

        # 6. Large cluster / Fraud ring bonus
        if cluster_size >= 6:
            msg = f"Claim belongs to a high-density entity cluster containing {cluster_size} interconnected nodes."
            evidence_list.append(msg)
            base_risk_score += 0.15
            signals_list.append(
                GraphRiskSignal(
                    name="DENSE_FRAUD_RING_TOPOLOGY",
                    severity="HIGH",
                    evidence=msg,
                    score_impact=0.15,
                )
            )

        # Baseline baseline if no specific red flags found
        if not evidence_list:
            evidence_list.append("Standard network topology. No shared device or multi-claim collisions detected.")
            base_risk_score = 0.08

        final_graph_risk = round(min(1.0, max(0.02, base_risk_score)), 2)

        return GraphRiskResult(
            claim_id=claim_id,
            graph_risk_score=final_graph_risk,
            degree=degree,
            centrality=round(centrality, 3),
            connected_cluster_size=cluster_size,
            shared_device_detected=shared_device_detected,
            shared_location_detected=shared_location,
            suspicious_repair_shop_detected=suspicious_repair_shop,
            repeat_claim_velocity_detected=repeat_claim_velocity,
            evidence=evidence_list,
            signals=signals_list,
        )

    # ── ADVANCED GRAPH ANALYTICS QUERIES ─────────────────────────

    async def query_shared_devices(self) -> List[Dict[str, Any]]:
        """Return devices associated with multiple customers or multiple claims."""
        results = []
        undirected_g = self._nx_graph.to_undirected(as_view=True)
        for nid, data in self._nx_graph.nodes(data=True):
            if data.get("type") == GraphNodeType.DEVICE.value:
                claims = [n for n in undirected_g.neighbors(nid) if self._nx_graph.nodes[n].get("type") == GraphNodeType.CLAIM.value]
                customers = [n for n in undirected_g.neighbors(nid) if self._nx_graph.nodes[n].get("type") == GraphNodeType.CUSTOMER.value]
                if len(claims) > 1 or len(customers) > 1:
                    results.append({
                        "device_id": nid,
                        "label": data.get("label"),
                        "claim_count": len(claims),
                        "customer_count": len(customers),
                    })
        return results

    async def query_suspicious_repair_shops(self, min_claims: int = 2) -> List[Dict[str, Any]]:
        """Return repair shops with multiple claims."""
        results = []
        undirected_g = self._nx_graph.to_undirected(as_view=True)
        for nid, data in self._nx_graph.nodes(data=True):
            if data.get("type") == GraphNodeType.REPAIR_SHOP.value:
                claims = [n for n in undirected_g.neighbors(nid) if self._nx_graph.nodes[n].get("type") == GraphNodeType.CLAIM.value]
                if len(claims) >= min_claims:
                    results.append({
                        "repair_shop_id": nid,
                        "name": data.get("label"),
                        "associated_claims_count": len(claims),
                    })
        return results

    async def query_claim_clusters(self) -> List[Dict[str, Any]]:
        """Find connected components with >= 3 nodes."""
        undirected_g = self._nx_graph.to_undirected(as_view=True)
        components = list(nx.connected_components(undirected_g))
        clusters = []
        for idx, comp in enumerate(components):
            if len(comp) >= 3:
                clusters.append({
                    "cluster_id": f"cluster_{idx+1}",
                    "node_count": len(comp),
                    "node_types": list(set([self._nx_graph.nodes[n].get("type") for n in comp])),
                    "nodes": list(comp),
                })
        return clusters


def get_graph_service() -> KnowledgeGraphService:
    """Dependency injector for graph service."""
    return KnowledgeGraphService.get_instance()
