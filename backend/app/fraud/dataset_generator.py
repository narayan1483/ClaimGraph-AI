"""
ClaimGraph AI — Synthetic Insurance/Warranty Fraud Dataset Generator.

Generates reproducible, statistically realistic claim records with engineered
features and both legitimate and fraudulent behavior patterns.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


# ── Canonical Seeds & Catalog ─────────────────────────────────────

PRODUCTS = [
    {"name": "Titan Pro Smartphone 256GB", "category": "Electronics", "manufacturer": "Titan Mobile", "model_number": "TP-256", "msrp": 1199.0},
    {"name": "ApexBook 16-inch Laptop M3", "category": "Electronics", "manufacturer": "Apex Compute", "model_number": "AB-16", "msrp": 2399.0},
    {"name": "Quantum OLED TV 65-inch", "category": "Appliances", "manufacturer": "Quantum Visual", "model_number": "QO-65", "msrp": 1850.0},
    {"name": "AeroDrive Transmission Module", "category": "Automotive", "manufacturer": "AeroAuto Parts", "model_number": "AD-TR8", "msrp": 3400.0},
    {"name": "HyperSound Studio Headphones", "category": "Electronics", "manufacturer": "HyperSound Labs", "model_number": "HS-STUDIO", "msrp": 399.0},
    {"name": "Solaris Smart Inverter 5kW", "category": "Appliances", "manufacturer": "Solaris Power", "model_number": "SS-5000", "msrp": 1650.0},
    {"name": "Precision Turbocharger Unit", "category": "Automotive", "manufacturer": "AeroAuto Parts", "model_number": "PT-900", "msrp": 2100.0},
    {"name": "PulseWave Smartwatch Ultra", "category": "Electronics", "manufacturer": "Titan Mobile", "model_number": "PW-ULTRA", "msrp": 799.0},
]

LOCATIONS = [
    "New York, NY", "Chicago, IL", "Houston, TX", "Phoenix, AZ", "Miami, FL",
    "Los Angeles, CA", "Seattle, WA", "Atlanta, GA", "Denver, CO", "Dallas, TX",
    "Las Vegas, NV (High Risk Zone)", "Detroit, MI (Cluster 4)", "Orlando, FL (Ring Alpha)",
]

SUSPICIOUS_LOCATIONS = [
    "Las Vegas, NV (High Risk Zone)",
    "Detroit, MI (Cluster 4)",
    "Orlando, FL (Ring Alpha)",
]

REPAIR_SHOPS = [
    "Certified Care Center Downtown",
    "National Authorized Service Hub",
    "Metro Tech Express",
    "Apex QuickFix Partner",
    "Vance Brothers Salvage & Repair (Flagged)",
    "ShadowLine Mechanics LLC (Flagged)",
    "Precision Collision Center",
]

SUSPICIOUS_REPAIR_SHOPS = [
    "Vance Brothers Salvage & Repair (Flagged)",
    "ShadowLine Mechanics LLC (Flagged)",
]

CLAIM_TYPES = ["DAMAGE", "THEFT", "MALFUNCTION", "LOSS", "WARRANTY_REPAIR"]


def generate_synthetic_data(num_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic claims dataframe containing raw metadata, engineered features,
    and ground truth `is_fraud` label.
    """
    np.random.seed(seed)
    random.seed(seed)

    records: List[Dict[str, Any]] = []

    # 1. Generate customer pool
    num_customers = max(200, num_samples // 4)
    customers = [f"CUST-{i:05d}" for i in range(1, num_customers + 1)]

    # Assign fraud tendency to 12% of customer population (fraud rings / serial fraudsters)
    fraudulent_customers = set(random.sample(customers, int(num_customers * 0.12)))

    # 2. Generate device pool
    num_devices = max(300, num_samples // 3)
    devices = [f"SN-DEV-{i:06d}" for i in range(1, num_devices + 1)]
    reused_devices = set(random.sample(devices, int(num_devices * 0.08)))  # Reused devices fraud ring

    customer_history: Dict[str, List[datetime]] = {c: [] for c in customers}
    customer_amounts: Dict[str, List[float]] = {c: [] for c in customers}
    device_claims_count: Dict[str, int] = {d: 0 for d in devices}
    location_counts: Dict[str, int] = {loc: 0 for loc in LOCATIONS}
    repair_shop_counts: Dict[str, int] = {shop: 0 for shop in REPAIR_SHOPS}

    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)

    for i in range(num_samples):
        # Determine if this sample will simulate fraud
        is_fraudster_cust = random.random() < 0.22
        if is_fraudster_cust:
            cust_id = random.choice(list(fraudulent_customers))
        else:
            cust_id = random.choice(customers)

        prod = random.choice(PRODUCTS)
        msrp = prod["msrp"]

        # Select or reuse device
        if cust_id in fraudulent_customers and random.random() < 0.40:
            dev_sn = random.choice(list(reused_devices))
        else:
            dev_sn = random.choice(devices)

        # Simulation date
        days_forward = random.randint(1, 600)
        incident_date = base_time + timedelta(days=days_forward, hours=random.randint(1, 23))
        device_age = random.randint(10, 1200)

        # Historical behavior before this incident
        prev_dates = customer_history[cust_id]
        prev_amounts = customer_amounts[cust_id]
        previous_claim_count = len(prev_dates)

        if previous_claim_count > 0:
            days_since_last_claim = max(1, (incident_date - prev_dates[-1]).days)
            claims_last_30_days = sum(1 for d in prev_dates if (incident_date - d).days <= 30)
            avg_claim_amount = float(np.mean(prev_amounts))
        else:
            days_since_last_claim = 999.0
            claims_last_30_days = 0
            avg_claim_amount = msrp * 0.45

        # Determine location & repair shop
        if cust_id in fraudulent_customers and random.random() < 0.65:
            location = random.choice(SUSPICIOUS_LOCATIONS)
            repair_shop = random.choice(SUSPICIOUS_REPAIR_SHOPS)
        else:
            location = random.choice(LOCATIONS)
            repair_shop = random.choice(REPAIR_SHOPS) if random.random() > 0.3 else None

        # Determine fraud pattern and claim amount
        fraud_score_bias = 0.0
        fraud_triggers = []

        if cust_id in fraudulent_customers:
            fraud_score_bias += 0.35

            # Pattern A: Excessive Velocity
            if random.random() < 0.50:
                claims_last_30_days += random.randint(1, 4)
                days_since_last_claim = random.randint(3, 20)
                fraud_triggers.append("rapid_successive_claims")
                fraud_score_bias += 0.30

            # Pattern B: Inflated Claim Amount
            if random.random() < 0.45:
                claim_amount = round(msrp * random.uniform(0.95, 1.45), 2)
                fraud_triggers.append("inflated_amount_exceeding_msrp")
                fraud_score_bias += 0.25
            else:
                claim_amount = round(msrp * random.uniform(0.40, 0.85), 2)

            # Pattern C: Shared Device Ring
            if dev_sn in reused_devices:
                device_claims_count[dev_sn] += random.randint(2, 5)
                fraud_triggers.append("device_multi_customer_ring")
                fraud_score_bias += 0.25

            # Pattern D: Collusion Repair Shop
            if repair_shop in SUSPICIOUS_REPAIR_SHOPS:
                fraud_triggers.append("suspicious_repair_shop")
                fraud_score_bias += 0.20
        else:
            # Legitimate claim behavior
            claim_amount = round(msrp * random.uniform(0.10, 0.65), 2)
            if random.random() < 0.03:  # rare edge case / false positive
                fraud_score_bias += 0.15

        # Calculated features
        amount_deviation = round(claim_amount - avg_claim_amount, 2)
        amount_to_msrp_ratio = round(claim_amount / msrp, 4)
        customer_claim_frequency = round((previous_claim_count + 1) / max(30, (device_age / 30)), 4)
        dev_claims = device_claims_count[dev_sn] + 1
        loc_freq = location_counts[location] + 1
        shop_freq = (repair_shop_counts[repair_shop] + 1) if repair_shop else 0

        # Update running state
        customer_history[cust_id].append(incident_date)
        customer_amounts[cust_id].append(claim_amount)
        device_claims_count[dev_sn] = dev_claims
        location_counts[location] = loc_freq
        if repair_shop:
            repair_shop_counts[repair_shop] = shop_freq

        # Ground truth label: 1 if fraud conditions strongly met
        is_fraud = 1 if (fraud_score_bias >= 0.50 or (cust_id in fraudulent_customers and len(fraud_triggers) >= 2)) else 0

        claim_type = random.choice(CLAIM_TYPES)

        records.append({
            "claim_id": f"CLM-SYN-{i+1:05d}",
            "customer_id": cust_id,
            "device_serial": dev_sn,
            "product_name": prod["name"],
            "product_category": prod["category"],
            "msrp": msrp,
            "claim_type": claim_type,
            "claim_amount": claim_amount,
            "incident_date": incident_date.isoformat(),
            "location": location,
            "repair_shop": repair_shop or "None",
            # ── Engineered Features ──
            "previous_claim_count": previous_claim_count,
            "claims_last_30_days": claims_last_30_days,
            "average_claim_amount": round(avg_claim_amount, 2),
            "amount_deviation": amount_deviation,
            "amount_to_msrp_ratio": amount_to_msrp_ratio,
            "device_claim_count": dev_claims,
            "customer_claim_frequency": customer_claim_frequency,
            "location_frequency": loc_freq,
            "repair_shop_frequency": shop_freq,
            "days_since_last_claim": days_since_last_claim,
            "device_age": device_age,
            # Target
            "is_fraud": is_fraud,
        })

    df = pd.DataFrame(records)
    return df


FEATURE_COLUMNS = [
    "claim_amount",
    "previous_claim_count",
    "claims_last_30_days",
    "average_claim_amount",
    "amount_deviation",
    "amount_to_msrp_ratio",
    "device_claim_count",
    "customer_claim_frequency",
    "location_frequency",
    "repair_shop_frequency",
    "days_since_last_claim",
    "device_age",
]
