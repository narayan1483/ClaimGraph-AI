# ClaimGraph AI — Neo4j Knowledge Graph & Fraud Ring Analytics

> **Graph Thesis**: Individual claims may look completely legitimate in isolation; fraud syndicates are exposed only through hidden relational connections (shared IMEIs, collusive repair shops, shared banking details, cyclical ownership).

---

## 1. Schema & Ontological Graph Model

### Nodes:
- `Customer`: Insured policyholder (attributes: `customer_id`, `name`, `risk_score`)
- `Device`: Physical asset (attributes: `device_id`, `serial_number`, `model`)
- `Product`: Catalog device model (attributes: `name`, `category`, `msrp`)
- `Claim`: Filed insurance event (attributes: `claim_id`, `amount`, `status`)
- `RepairShop`: Third-party service shop (attributes: `name`, `license_no`)
- `Location`: Geographic city/state/postal node
- `Policy`: Underwritten coverage contract

### Relationships:
- `(Customer)-[:CUSTOMER_OWNS_DEVICE]->(Device)`
- `(Customer)-[:CUSTOMER_SUBMITTED_CLAIM]->(Claim)`
- `(Device)-[:DEVICE_HAS_CLAIM]->(Claim)`
- `(Claim)-[:CLAIM_ASSIGNED_TO_REPAIR_SHOP]->(RepairShop)`
- `(Claim)-[:CLAIM_ASSOCIATED_WITH_LOCATION]->(Location)`
- `(Customer)-[:POLICY_HOLDER_OF]->(Policy)`

---

## 2. Graph Algorithms Implemented

### 1. Cycle & Ring Fraud Detection (Cypher)
Detects circular claim networks where devices or payouts cycle among related parties:
```cypher
MATCH path = (c:Customer)-[:CUSTOMER_OWNS_DEVICE]->(d:Device)
             -[:DEVICE_HAS_CLAIM]->(cl:Claim)
             -[:CLAIM_ASSIGNED_TO_REPAIR_SHOP]->(r:RepairShop)
             <-[:CLAIM_ASSIGNED_TO_REPAIR_SHOP]-(cl2:Claim)
             <-[:DEVICE_HAS_CLAIM]-(d2:Device)
             <-[:CUSTOMER_OWNS_DEVICE]-(c2:Customer)
WHERE c <> c2 AND (c)-[:SHARED_IDENTIFIER]-(c2)
RETURN path LIMIT 50;
```

### 2. High-Degree Centrality Anomalies
Repair shops or customers connected to an abnormal volume of high-value damage claims within a short time window.

### 3. Shortest Path Between Suspicious Entities
Discovers degrees of separation between newly filed claims and known fraud syndicates using bidirectional BFS.

---

## 3. Interview Defense: Why Neo4j over Relational SQL?
- Relational databases require `N` joins for `N`-hop traversals, resulting in exponential computational degradation `O(b^d)`.
- Neo4j provides **Index-Free Adjacency**: each node points directly to its connected edges in memory (`O(1)` per step).
- Cypher query language allows natural, declarative pattern matching for complex syndicated fraud topology.
