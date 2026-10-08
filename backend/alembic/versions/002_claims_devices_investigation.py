"""ClaimGraph AI — Migration 002: Products, Devices, Claims, Claim Events, Investigation Records.

Revision ID: 002_claims_devices_investigation
Revises: 001_initial_schema
Create Date: 2026-10-08 17:30:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_claims_devices_investigation"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Products ──
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=False),
        sa.Column("model_number", sa.String(length=100), nullable=False),
        sa.Column("msrp", sa.Float(), nullable=False),
        sa.Column("warranty_period_months", sa.Integer(), server_default=sa.text("12"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index("ix_products_category", "products", ["category"], unique=False)
    op.create_index("ix_products_model_number", "products", ["model_number"], unique=False)

    # ── 2. Devices ──
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], unique=False)
    op.create_index("ix_devices_product_id", "devices", ["product_id"], unique=False)
    op.create_index("ix_devices_customer_id", "devices", ["customer_id"], unique=False)

    # ── 3. Claims ──
    op.create_table(
        "claims",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("claim_id", sa.String(length=50), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("claim_type", sa.String(length=30), nullable=False),
        sa.Column("claim_amount", sa.Float(), nullable=False),
        sa.Column("incident_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(length=150), nullable=False),
        sa.Column("repair_shop", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="SUBMITTED", nullable=False),
        sa.Column("fraud_probability", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_claims_claim_id", "claims", ["claim_id"], unique=True)
    op.create_index("ix_claims_customer_id", "claims", ["customer_id"], unique=False)
    op.create_index("ix_claims_device_id", "claims", ["device_id"], unique=False)
    op.create_index("ix_claims_claim_type", "claims", ["claim_type"], unique=False)
    op.create_index("ix_claims_location", "claims", ["location"], unique=False)
    op.create_index("ix_claims_repair_shop", "claims", ["repair_shop"], unique=False)
    op.create_index("ix_claims_status", "claims", ["status"], unique=False)

    # ── 4. Claim Events ──
    op.create_table(
        "claim_events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_claim_events_claim_id", "claim_events", ["claim_id"], unique=False)

    # ── 5. Investigation Records ──
    op.create_table(
        "investigation_records",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("investigation_id", sa.String(length=50), nullable=False),
        sa.Column("claim_id", sa.String(length=50), nullable=False),
        sa.Column("fraud_score", sa.Float(), nullable=False),
        sa.Column("graph_score", sa.Float(), nullable=False),
        sa.Column("final_risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("recommendation", sa.String(length=50), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("agent_results_json", sa.JSON(), nullable=False),
        sa.Column("score_breakdown_json", sa.JSON(), nullable=False),
        sa.Column("investigation_report", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="AWAITING_REVIEW", nullable=False),
        sa.Column("decision", sa.String(length=30), nullable=True),
        sa.Column("decision_notes", sa.Text(), nullable=True),
        sa.Column("decided_by_id", sa.String(length=36), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_investigation_records_investigation_id", "investigation_records", ["investigation_id"], unique=True)
    op.create_index("ix_investigation_records_claim_id", "investigation_records", ["claim_id"], unique=False)


def downgrade() -> None:
    op.drop_table("investigation_records")
    op.drop_table("claim_events")
    op.drop_table("claims")
    op.drop_table("devices")
    op.drop_table("products")
