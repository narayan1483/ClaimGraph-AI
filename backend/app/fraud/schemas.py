"""
ClaimGraph AI — Fraud Intelligence Schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FraudPredictionRequest(BaseModel):
    """Direct feature vector payload for ML inference."""

    claim_amount: float = Field(..., description="Claim requested amount in USD")
    previous_claim_count: int = Field(default=0, ge=0)
    claims_last_30_days: int = Field(default=0, ge=0)
    average_claim_amount: float = Field(default=0.0, ge=0)
    amount_deviation: float = Field(default=0.0)
    amount_to_msrp_ratio: float = Field(default=0.5, ge=0)
    device_claim_count: int = Field(default=1, ge=1)
    customer_claim_frequency: float = Field(default=0.0, ge=0)
    location_frequency: int = Field(default=1, ge=1)
    repair_shop_frequency: int = Field(default=0, ge=0)
    days_since_last_claim: float = Field(default=999.0, ge=0)
    device_age: int = Field(default=100, ge=0)


class FactorImpact(BaseModel):
    """SHAP or model contribution factor."""

    feature: str
    impact: float
    value: Optional[float] = None


class FraudPredictionResponse(BaseModel):
    """Standardized ML fraud detection output."""

    fraud_probability: float
    risk_score: float
    risk_level: str
    top_factors: List[FactorImpact]
    model_version: str
    model_name: str
    prediction_timestamp: str


class ModelMetricsResponse(BaseModel):
    """Comprehensive evaluation metrics comparing all candidate models."""

    best_model: str
    feature_columns: List[str]
    dataset_samples: int
    train_samples: int
    validation_samples: int
    fraud_prevalence: float
    models_comparison: Dict[str, Dict[str, Any]]
    model_version: str
    trained_at: str
