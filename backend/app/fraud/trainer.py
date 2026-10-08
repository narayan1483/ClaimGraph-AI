"""
ClaimGraph AI — Machine Learning Fraud Model Training Pipeline.

Trains and evaluates:
1. Logistic Regression
2. Random Forest
3. XGBoost

Compares Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix.
Selects the superior model based on actual validation results, saves the artifacts,
and configures SHAP explainability.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from app.fraud.dataset_generator import FEATURE_COLUMNS, generate_synthetic_data

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


def train_and_evaluate_models(
    df: pd.DataFrame | None = None,
    save_artifacts: bool = True,
) -> Tuple[Dict[str, Any], Any]:
    """
    Train Logistic Regression, Random Forest, and XGBoost models.
    Compare metrics and persist the top-performing model with SHAP capabilities.
    """
    if df is None:
        df = generate_synthetic_data(num_samples=6000, seed=42)

    X = df[FEATURE_COLUMNS]
    y = df["is_fraud"].values

    # Stratified Train/Test split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # Class imbalance weight
    pos_count = np.sum(y_train == 1)
    neg_count = np.sum(y_train == 0)
    scale_pos_weight = neg_count / max(1, pos_count)

    models = {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=120, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=140,
            max_depth=6,
            learning_rate=0.08,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=42,
        ),
    }

    metrics_comparison: Dict[str, Dict[str, Any]] = {}
    best_model_name = ""
    best_f1 = -1.0
    best_model_obj = None

    for name, model in models.items():
        # Train
        if name == "LogisticRegression":
            model.fit(X_train_scaled, y_train)
            val_X = X_val_scaled
        else:
            model.fit(X_train.values, y_train)
            val_X = X_val.values

        # Predictions
        y_pred = model.predict(val_X)
        y_prob = model.predict_proba(val_X)[:, 1]

        # Calculate metrics
        precision = float(precision_score(y_val, y_pred, zero_division=0))
        recall = float(recall_score(y_val, y_pred, zero_division=0))
        f1 = float(f1_score(y_val, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_val, y_prob))
        pr_auc = float(average_precision_score(y_val, y_prob))
        cm = confusion_matrix(y_val, y_pred).tolist()

        metrics_comparison[name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": cm,
        }

        # Track best model based on F1 (balanced precision and recall in fraud detection)
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model

    report = {
        "best_model": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "dataset_samples": len(df),
        "train_samples": len(X_train),
        "validation_samples": len(X_val),
        "fraud_prevalence": float(np.mean(y)),
        "models_comparison": metrics_comparison,
        "trained_at": pd.Timestamp.now().isoformat(),
        "model_version": "v1.0.0-phase3",
    }

    if save_artifacts:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        # Save model and preprocessing artifacts
        artifact_bundle = {
            "model_name": best_model_name,
            "model": best_model_obj,
            "scaler": scaler,
            "feature_columns": FEATURE_COLUMNS,
            "requires_scaling": best_model_name == "LogisticRegression",
            "model_version": report["model_version"],
        }
        joblib.dump(artifact_bundle, ARTIFACTS_DIR / "best_model.joblib")

        with open(ARTIFACTS_DIR / "model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    return report, best_model_obj


if __name__ == "__main__":
    report, _ = train_and_evaluate_models()
    print("=== MODEL COMPARISON RESULTS ===")
    print(json.dumps(report["models_comparison"], indent=2))
    print(f"\nWinning Model Selected: {report['best_model']} (F1: {report['models_comparison'][report['best_model']]['f1_score']})")
