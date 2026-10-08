# ClaimGraph AI — Security, RBAC & Audit Compliance

> **Security Thesis**: Financial fraud systems process highly sensitive PII and financial records. Architecture implements zero-trust authorization, strict role-based access control (RBAC), password hashing via Argon2/bcrypt, and immutable audit logs.

---

## 1. Authentication & Session Management
- **Stateless JWT Tokens**: Signed with HMAC-SHA256 (`HS256`) using environment-managed `JWT_SECRET_KEY`.
- **Token Separation**: Distinct `access` (15-minute expiry) and `refresh` tokens (7-day expiry).
- **Password Protection**: Passwords salted and hashed with bcrypt (cost factor 12) before persistence.

---

## 2. Role-Based Access Control (RBAC)

Hierarchy enforced through FastAPI dependency injection (`require_roles`):

| Role | Claims Management | AI Investigations | Fraud Ring Graph | Audit Logs | System Settings |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CUSTOMER** | Own Claims Only | ❌ | ❌ | ❌ | Profile Only |
| **ANALYST** | View All | Read-Only | Read-Only | ❌ | ❌ |
| **INVESTIGATOR** | Full Management | Execute & Adjudicate | Full Traversal | Read-Only | ❌ |
| **ADMIN** | Full Management | Full Management | Full Traversal | Full Access | Full Access |

---

## 3. Immutable Audit Trail
- Every state transition, claim creation, and investigator decision (`APPROVE`, `REJECT`, `ESCALATE`) logs:
  - `user_id`: Operator or system agent responsible
  - `action`: Specific event name (`CLAIM_CREATED`, `CLAIM_DECIDED_APPROVE`, etc.)
  - `entity_type` & `entity_id`: Primary record affected
  - `details`: Exact JSON payload capturing state before and after change
  - `ip_address` & `user_agent`: Client network provenance
  - `created_at`: Timezone-aware UTC timestamp
- Tamper-evident: Records are append-only.
