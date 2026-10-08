"""
ClaimGraph AI — Evaluation Benchmark Datasets.

Contains standardized benchmark queries, claims, ground-truth labels,
and expected policy retrievals for rigorous automated AI & ML evaluation.
"""

from typing import Any, Dict, List

# Synthetic Ground Truth Evaluation Dataset for Policy RAG
POLICY_BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "id": "RAG-001",
        "question": "What is the policy limitation for water damage claims under standard comprehensive policies?",
        "expected_policy_id": "POL-WATER-01",
        "expected_keywords": ["water damage", "coverage limit", "flood exclusion", "deductible"],
        "reference_answer": "Water damage coverage applies to sudden and accidental leaks with standard $1,000 deductible. Flooding and ground water intrusion are excluded.",
        "ground_truth_context": "Standard comprehensive policies cover sudden and accidental discharge of water or steam with a $1,000 deductible. Surface flooding and groundwater seepage are explicitly excluded.",
    },
    {
        "id": "RAG-002",
        "question": "Is screen damage covered if the mobile device was dropped accidentally?",
        "expected_policy_id": "POL-DEVICE-SCREEN",
        "expected_keywords": ["accidental damage", "screen", "repair", "claim limits"],
        "reference_answer": "Accidental screen damage is covered under Tier 1 device protection subject to maximum two claims per 12-month period.",
        "ground_truth_context": "Tier 1 device protection includes accidental damage from handling (ADH) covering cracked screens up to 2 incidents every rolling 12 months.",
    },
    {
        "id": "RAG-003",
        "question": "What documentation is required to substantiate an electronics theft claim?",
        "expected_policy_id": "POL-THEFT-DOCS",
        "expected_keywords": ["police report", "proof of purchase", "serial number", "affidavit"],
        "reference_answer": "Electronics theft claims require a filed police report within 48 hours, proof of original purchase, device serial number/IMEI, and a signed claim affidavit.",
        "ground_truth_context": "To process theft claims, policyholders must submit an official police incident report within 48 hours of occurrence, valid proof of purchase showing serial number, and a notarized loss declaration.",
    },
    {
        "id": "RAG-004",
        "question": "Are refurbished replacement devices authorized when original parts are unavailable?",
        "expected_policy_id": "POL-REPAIR-PARTS",
        "expected_keywords": ["oem parts", "refurbished", "repair facility", "warranty"],
        "reference_answer": "Authorized repair centers may use certified OEM refurbished parts or replacements if new components are backordered exceeding 14 business days.",
        "ground_truth_context": "When OEM parts are unavailable or backordered beyond 14 business days, certified OEM-refurbished replacement units of equal or superior specifications are authorized.",
    },
    {
        "id": "RAG-005",
        "question": "What happens if a claimant submits altered or falsified repair estimates?",
        "expected_policy_id": "POL-FRAUD-SANCTIONS",
        "expected_keywords": ["falsification", "fraud", "denial", "investigation", "prosecution"],
        "reference_answer": "Submission of altered or fraudulent invoices results in immediate claim denial, policy cancellation, and mandatory referral to the Special Investigation Unit (SIU).",
        "ground_truth_context": "Any fraudulent statement, altered invoice, or fabricated estimate constitutes grounds for immediate claim forfeiture, retroactive policy rescission, and referral to law enforcement.",
    },
]

# Benchmark Claim Scenarios for Multi-Agent & Decision Evaluation
AGENT_BENCHMARK_SCENARIOS: List[Dict[str, Any]] = [
    {
        "claim_id": "BENCH-001",
        "claim_amount": 3400.0,
        "claim_type": "DAMAGE",
        "device_model": "iPhone 15 Pro Max",
        "prior_claims_count": 0,
        "is_fraud_ground_truth": False,
        "expected_recommendation": "APPROVE",
        "expected_risk_band": "LOW",
    },
    {
        "claim_id": "BENCH-002",
        "claim_amount": 18500.0,
        "claim_type": "THEFT",
        "device_model": "MacBook Pro M3 Max",
        "prior_claims_count": 4,
        "is_fraud_ground_truth": True,
        "expected_recommendation": "REJECT",
        "expected_risk_band": "CRITICAL",
    },
    {
        "claim_id": "BENCH-003",
        "claim_amount": 4200.0,
        "claim_type": "MALFUNCTION",
        "device_model": "Dell XPS 16",
        "prior_claims_count": 2,
        "is_fraud_ground_truth": True,
        "expected_recommendation": "ESCALATE",
        "expected_risk_band": "HIGH",
    },
]
