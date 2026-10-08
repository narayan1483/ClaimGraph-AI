"""
ClaimGraph AI — Phase 3 Live ML Inference & Metric Demonstration Script.
"""

import json
from app.fraud.service import FraudPredictionService

def main():
    with open("backend/app/fraud/artifacts/model_metadata.json") as f:
        meta = json.load(f)

    print("==================================================")
    print("PHASE 3 EMPIRICAL ML MODEL BENCHMARKS")
    print("==================================================")
    print(f"Selected Best Model : {meta.get('best_model')}")
    print(f"Dataset Size         : {meta.get('dataset_samples')} samples (Train: {meta.get('train_samples')}, Val: {meta.get('validation_samples')})")
    print(f"Fraud Prevalence     : {meta.get('fraud_prevalence') * 100:.2f}%")
    print("Comparison Matrix (Measured on 1,500 Holdout Validation Claims):")
    for model_name, m in meta["models_comparison"].items():
        print(f"  * {model_name:20} -> Precision: {m['precision']:.4f} | Recall: {m['recall']:.4f} | F1: {m['f1_score']:.4f} | ROC-AUC: {m['roc_auc']:.4f} | PR-AUC: {m['pr_auc']:.4f}")

    print("\n==================================================")
    print("LIVE REAL-TIME PREDICTION EXECUTION (WITH SHAP)")
    print("==================================================")
    sample_features = {
        "claim_amount": 2800.0,
        "previous_claim_count": 5,
        "claims_last_30_days": 3,
        "average_claim_amount": 900.0,
        "amount_deviation": 1900.0,
        "amount_to_msrp_ratio": 1.65,
        "device_claim_count": 4,
        "customer_claim_frequency": 0.85,
        "location_frequency": 7,
        "repair_shop_frequency": 6,
        "days_since_last_claim": 8.0,
        "device_age": 90,
    }

    prediction = FraudPredictionService.predict(sample_features)
    print(f"Fraud Probability   : {prediction['fraud_probability']:.4f} ({prediction['fraud_probability'] * 100:.2f}%)")
    print(f"Assigned Risk Level : {prediction['risk_level']}")
    print(f"Model Name          : {prediction['model_name']}")
    print(f"Model Version       : {prediction['model_version']}")
    print(f"Prediction Time     : {prediction['prediction_timestamp']}")
    print("\nTop SHAP Explainability Risk Factors:")
    for factor in prediction['top_factors']:
        print(f"  [+] {factor['feature']:25} | Impact: {factor['impact']:+.4f} | Feature Value: {factor['value']}")

if __name__ == "__main__":
    main()
