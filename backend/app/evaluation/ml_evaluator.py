"""
ClaimGraph AI — Machine Learning Model Evaluation Service.

Extracts and serves empirical metrics directly from the trained ML model artifacts:
- Precision, Recall, F1, ROC-AUC, PR-AUC
- Confusion Matrix (TN, FP, FN, TP)
- False Positive Rate (FPR) and False Negative Rate (FNR)
- Model comparison benchmarks (Logistic Regression vs Random Forest vs XGBoost)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.core.logging import get_logger
from app.fraud.trainer import ARTIFACTS_DIR

logger = get_logger(__name__)


class MLEvaluationService:
    """Provides empirical ML performance metrics from trained models."""

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Load model metadata and compute derived rates (FPR, FNR)."""
        metadata_path = ARTIFACTS_DIR / "model_metadata.json"
        if not metadata_path.exists():
            return {
                "error": "Model metadata not found. Run model training first.",
                "status": "NOT_INITIALIZED",
            }

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        best_name = metadata.get("best_model", "XGBoost")
        comparison = metadata.get("models_comparison", {})
        best_metrics = comparison.get(best_name, {})

        cm = best_metrics.get("confusion_matrix", [[0, 0], [0, 0]])
        tn = cm[0][0] if len(cm) > 0 and len(cm[0]) > 0 else 0
        fp = cm[0][1] if len(cm) > 0 and len(cm[0]) > 1 else 0
        fn = cm[1][0] if len(cm) > 1 and len(cm[1]) > 0 else 0
        tp = cm[1][1] if len(cm) > 1 and len(cm[1]) > 1 else 0

        # Derived Rates
        total_actual_neg = tn + fp
        total_actual_pos = tp + fn

        fpr = round(fp / total_actual_neg, 5) if total_actual_neg > 0 else 0.0
        fnr = round(fn / total_actual_pos, 5) if total_actual_pos > 0 else 0.0
        accuracy = round((tp + tn) / max(1, tn + fp + fn + tp), 4)

        return {
            "model_name": best_name,
            "model_version": metadata.get("model_version", "v1.0.0"),
            "trained_at": metadata.get("trained_at"),
            "dataset_samples": metadata.get("dataset_samples", 6000),
            "train_samples": metadata.get("train_samples", 4500),
            "validation_samples": metadata.get("validation_samples", 1500),
            "fraud_prevalence": metadata.get("fraud_prevalence", 0.3085),
            "primary_metrics": {
                "precision": best_metrics.get("precision", 0.0),
                "recall": best_metrics.get("recall", 0.0),
                "f1_score": best_metrics.get("f1_score", 0.0),
                "roc_auc": best_metrics.get("roc_auc", 0.0),
                "pr_auc": best_metrics.get("pr_auc", 0.0),
                "accuracy": accuracy,
                "false_positive_rate": fpr,
                "false_negative_rate": fnr,
            },
            "confusion_matrix": {
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp,
                "raw_matrix": cm,
            },
            "feature_columns": metadata.get("feature_columns", []),
            "models_comparison": comparison,
        }
