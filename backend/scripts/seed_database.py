"""
ClaimGraph AI — Database Seeding Script.

Generates realistic initial data in the local database:
- Admin, Investigator, and Customer user accounts
- Products catalog
- Insured devices
- Legitimate and fraudulent claims with realistic history
- Pre-trains and validates the ML fraud detection model
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog
from app.claims.models import Claim, ClaimStatus, ClaimType
from app.claims.repository import ClaimRepository
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.customers.models import Customer
from app.devices.models import Device, Product
from app.fraud.dataset_generator import PRODUCTS, LOCATIONS, REPAIR_SHOPS
from app.fraud.service import FraudPredictionService
from app.fraud.trainer import train_and_evaluate_models
from app.investigation.models import Investigator
from app.users.models import Organization, User, UserRole


async def seed_data() -> None:
    """Run database seeding workflow."""
    print("[*] Initializing ClaimGraph AI Seed...")

    # 1. Train and save ML model first
    print("\n[*] Training and benchmarking ML fraud models (LR, RF, XGBoost)...")
    report, _ = train_and_evaluate_models(save_artifacts=True)
    best_model = report["best_model"]
    f1 = report["models_comparison"][best_model]["f1_score"]
    roc_auc = report["models_comparison"][best_model]["roc_auc"]
    print(f"[OK] Top Model Selected: {best_model} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f}")

    async with async_session_factory() as db:
        # 2. Seed Organization
        org_res = await db.execute(select(Organization).where(Organization.slug == "apex-insurance"))
        org = org_res.scalar_one_or_none()
        if not org:
            org = Organization(
                name="Apex Insurance & Warranty Corp",
                slug="apex-insurance",
                description="Primary enterprise warranty and claims underwriting tenant",
            )
            db.add(org)
            await db.flush()
            print(f"[+] Organization seeded: {org.name}")

        # 3. Seed Users & Personas
        users_seed = [
            ("admin@claimgraph.ai", "AdminPass123!", "Narayan Prasad Maurya (System Admin)", UserRole.ADMIN),
            ("investigator@claimgraph.ai", "InvestigatorPass123!", "Sarah Connor (Lead Fraud Investigator)", UserRole.INVESTIGATOR),
            ("analyst@claimgraph.ai", "AnalystPass123!", "Marcus Brody (Operations Analyst)", UserRole.ANALYST),
            ("david.vance@example.com", "CustomerPass123!", "David Vance (Policyholder)", UserRole.CUSTOMER),
            ("elena.rostova@example.com", "CustomerPass123!", "Elena Rostova (Policyholder)", UserRole.CUSTOMER),
            ("ananya.sharma@example.com", "CustomerPass123!", "Ananya Sharma (Policyholder)", UserRole.CUSTOMER),
        ]

        created_users: dict[str, User] = {}
        for email, pwd, name, role in users_seed:
            user_res = await db.execute(select(User).where(User.email == email))
            user = user_res.scalar_one_or_none()
            if not user:
                user = User(
                    email=email,
                    hashed_password=hash_password(pwd),
                    full_name=name,
                    role=role,
                    organization_id=org.id,
                    is_active=True,
                    is_verified=True,
                )
                db.add(user)
                await db.flush()

                # Add profile
                if role == UserRole.CUSTOMER:
                    cust = Customer(
                        user_id=user.id,
                        phone_number=f"+1 555-01{random.randint(10, 99)}",
                        city=random.choice(["New York", "Chicago", "Detroit", "Miami"]),
                        country="US",
                    )
                    db.add(cust)
                print(f"[+] User seeded: {user.email} [{user.role.value}]")
            created_users[email] = user

        await db.commit()

        # 4. Seed Products
        created_products: list[Product] = []
        for p in PRODUCTS:
            p_res = await db.execute(select(Product).where(Product.model_number == p["model_number"]))
            prod = p_res.scalar_one_or_none()
            if not prod:
                prod = Product(
                    name=p["name"],
                    category=p["category"],
                    manufacturer=p["manufacturer"],
                    model_number=p["model_number"],
                    msrp=p["msrp"],
                )
                db.add(prod)
                await db.flush()
                print(f"[+] Product seeded: {prod.name} (${prod.msrp})")
            created_products.append(prod)

        await db.commit()

        # 5. Fetch customers
        cust_list_res = await db.execute(select(Customer))
        customers = list(cust_list_res.scalars().all())

        # 6. Seed Devices for Customers
        created_devices: list[Device] = []
        for i, cust in enumerate(customers):
            # Give each customer 1 or 2 devices
            for dev_idx in range(2):
                sn = f"SN-ASSET-00{i+1}{dev_idx+1}"
                d_res = await db.execute(select(Device).where(Device.serial_number == sn))
                dev = d_res.scalar_one_or_none()
                if not dev:
                    prod = random.choice(created_products)
                    dev = Device(
                        serial_number=sn,
                        product_id=prod.id,
                        customer_id=cust.id,
                        purchase_date=datetime.now(timezone.utc) - timedelta(days=random.randint(60, 400)),
                        purchase_price=prod.msrp,
                        status="ACTIVE",
                    )
                    db.add(dev)
                    await db.flush()
                created_devices.append(dev)

        await db.commit()

        # 7. Seed Initial Claims
        sample_claims_config = [
            {
                "claim_id": "CLM-2026-8841",
                "customer_idx": 0,
                "amount": 1420.0,
                "type": ClaimType.DAMAGE,
                "desc": "Severe screen shatter and water ingress while traveling.",
                "loc": "Detroit, MI (Cluster 4)",
                "shop": "Vance Brothers Salvage & Repair (Flagged)",
                "status": ClaimStatus.FLAGGED_INVESTIGATION,
            },
            {
                "claim_id": "CLM-2026-8839",
                "customer_idx": 1,
                "amount": 890.0,
                "type": ClaimType.MALFUNCTION,
                "desc": "Device motherboard failed to power on after firmware upgrade.",
                "loc": "Chicago, IL",
                "shop": "Certified Care Center Downtown",
                "status": ClaimStatus.UNDER_REVIEW,
            },
            {
                "claim_id": "CLM-2026-8831",
                "customer_idx": 2,
                "amount": 250.0,
                "type": ClaimType.WARRANTY_REPAIR,
                "desc": "Audio speaker port cracked, minor replacement needed.",
                "loc": "New York, NY",
                "shop": "Metro Tech Express",
                "status": ClaimStatus.APPROVED,
            },
        ]

        for cfg in sample_claims_config:
            c_res = await db.execute(select(Claim).where(Claim.claim_id == cfg["claim_id"]))
            if not c_res.scalar_one_or_none() and len(customers) > cfg["customer_idx"]:
                cust = customers[cfg["customer_idx"]]
                # Find device for customer
                d_res = await db.execute(select(Device).where(Device.customer_id == cust.id))
                dev = d_res.scalars().first()
                if dev:
                    claim = await ClaimRepository.create(
                        db=db,
                        customer_id=cust.id,
                        device_id=dev.id,
                        claim_type=cfg["type"],
                        claim_amount=cfg["amount"],
                        incident_date=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)),
                        description=cfg["desc"],
                        location=cfg["loc"],
                        repair_shop=cfg["shop"],
                        custom_claim_id=cfg["claim_id"],
                    )
                    claim.status = cfg["status"]

                    # Run ML prediction on the claim
                    pred = FraudPredictionService.predict({
                        "claim_amount": claim.claim_amount,
                        "previous_claim_count": 2 if cfg["status"] == ClaimStatus.FLAGGED_INVESTIGATION else 0,
                        "claims_last_30_days": 1,
                        "average_claim_amount": 900.0,
                        "amount_deviation": 520.0 if cfg["status"] == ClaimStatus.FLAGGED_INVESTIGATION else 0.0,
                        "amount_to_msrp_ratio": 1.1 if cfg["status"] == ClaimStatus.FLAGGED_INVESTIGATION else 0.3,
                        "device_claim_count": 2,
                        "customer_claim_frequency": 0.4,
                        "location_frequency": 4,
                        "repair_shop_frequency": 3 if "Flagged" in cfg["shop"] else 0,
                        "days_since_last_claim": 14.0 if cfg["status"] == ClaimStatus.FLAGGED_INVESTIGATION else 999.0,
                        "device_age": 120,
                    })
                    claim.fraud_probability = pred["fraud_probability"]
                    claim.risk_level = pred["risk_level"]
                    await db.flush()
                    print(f"[+] Claim seeded: {claim.claim_id} | Amount: ${claim.claim_amount} | Risk: {claim.risk_level} ({claim.fraud_probability*100:.1f}%)")

        await db.commit()
        print("\n[OK] Database Seeding & ML Benchmarking Complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
