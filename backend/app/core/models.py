"""
ClaimGraph AI — Consolidated Database Model Registry.

Imports all domain models to ensure Base.metadata is fully populated
for Alembic migrations and database initialization.
"""

from app.core.database import Base
from app.users.models import Organization, User, UserRole
from app.customers.models import Customer
from app.investigation.models import Investigator, InvestigationRecord
from app.audit.models import AuditLog
from app.devices.models import Product, Device
from app.claims.models import Claim, ClaimEvent, ClaimStatus, ClaimType

__all__ = [
    "Base",
    "Organization",
    "User",
    "UserRole",
    "Customer",
    "Investigator",
    "InvestigationRecord",
    "AuditLog",
    "Product",
    "Device",
    "Claim",
    "ClaimEvent",
    "ClaimStatus",
    "ClaimType",
]

