"""
ClaimGraph AI — Fraud Prediction & SHAP Explainability Service.

Loads the trained model bundle and performs deterministic risk scoring
along with feature attribution impacts using SHAP values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import shap

from app.core.logging import get_logger
from app.fraud.dataset_generator import FEATURE_COLUMNS
from app.fraud.trainer import ARTIFACTS_DIR, train_and_evaluate_models

logger = get_logger(__name__)

_MODEL_BUNDLE: Optional[Dict[str, Any]] = None
_SHAP_EXPLAINER: Optional[Any] = None


def get_model_bundle() -> Dict[str, Any]:
    """Retrieve or load cached model artifact bundle."""
    global _MODEL_BUNDLE, _SHAP_EXPLAINER
    if _MODEL_BUNDLE is None:
        model_path = ARTIFACTS_DIR / "best_model.joblib"
        if not model_path.exists():
            logger.info("training_initial_fraud_model")
            train_and_evaluate_models(save_artifacts=True)

        _MODEL_BUNDLE = joblib.load(model_path)
        logger.info("fraud_model_loaded", model=_MODEL_BUNDLE["model_name"], version=_MODEL_BUNDLE["model_version"])

        # Initialize SHAP explainer
        model = _MODEL_BUNDLE["model"]
        try:
            if hasattr(model, "predict_proba"):
                _SHAP_EXPLAINER = shap.TreeExplainer(model)
        except Exception as exc:
            logger.warning("shap_tree_explainer_init_fallback", error=str(exc))
            _SHAP_EXPLAINER = None

    return _MODEL_BUNDLE


def compute_risk_level(prob: float) -> str:
    """Classify numerical probability into standardized risk bands."""
    if prob >= 0.85:
        return "CRITICAL"
    if prob >= 0.70:
        return "HIGH"
    if prob >= 0.35:
        return "MEDIUM"
    return "LOW"


class FraudPredictionService:
    """Service providing fraud inference and SHAP explainability."""

    @classmethod
    def predict(cls, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Run inference on feature dictionary.
        Returns fraud_probability, risk_level, model_version, and top_factors.
        """
        bundle = get_model_bundle()
        model = bundle["model"]
        scaler = bundle["scaler"]
        requires_scaling = bundle.get("requires_scaling", False)
        feature_cols = bundle.get("feature_columns", FEATURE_COLUMNS)

        # Build feature vector in exact column order
        vec = [float(features.get(col, 0.0)) for col in feature_cols]
        X = np.array([vec])

        if requires_scaling:
            X_input = scaler.transform(X)
        else:
            X_input = X

        # Predict probability
        probs = model.predict_proba(X_input)
        fraud_prob = float(probs[0][1])
        risk_level = compute_risk_level(fraud_prob)

        # ── SHAP Explainability ──
        top_factors: List[Dict[str, Any]] = []
        global _SHAP_EXPLAINER
        if _SHAP_EXPLAINER is not None:
            try:
                shap_values = _SHAP_EXPLAINER.shap_values(X)
                # For binary classification TreeExplainer, shap_values can be array of shape (1, features) or list
                if isinstance(shap_values, list) and len(shap_values) == 2:
                    impacts = shap_values[1][0]
                elif hasattr(shap_values, "shape") and len(shap_values.shape) == 3:
                    impacts = shap_values[0, :, 1]
                else:
                    impacts = shap_values[0]

                # Pair features with impacts and sort by absolute contribution
                paired = []
                for idx, col in enumerate(feature_cols):
                    impact = float(impacts[idx])
                    paired.append({
                        "feature": col,
                        "impact": round(impact, 4),
                        "value": vec[idx],
                        "abs_impact": abs(impact),
                    })
                paired.sort(key=lambda x: x["abs_impact"], reverse=True)
                top_factors = [{k: v for k, v in item.items() if k != "abs_impact"} for item in paired[:5]]
            except Exception as exc:
                logger.warning("shap_computation_fallback", error=str(exc))

        # Fallback to feature importance if SHAP encountered an exception
        if not top_factors and hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            paired = []
            for idx, col in enumerate(feature_cols):
                imp = float(importances[idx])
                paired.append({"feature": col, "impact": round(imp, 4), "value": vec[idx]})
            paired.sort(key=lambda x: x["impact"], reverse=True)
            top_factors = paired[:5]

        return {
            "fraud_probability": round(fraud_prob, 4),
            "risk_score": round(fraud_prob, 4),
            "risk_level": risk_level,
            "top_factors": top_factors,
            "model_version": bundle.get("model_version", "v1.0.0"),
            "model_name": bundle.get("model_name", "BestModel"),
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
        }
