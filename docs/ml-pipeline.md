# ClaimGraph AI — Machine Learning Pipeline & MLOps Architecture

> **Pipeline Thesis**: Real tabular claims fraud features (claim amount deviation, claim velocity, repair shop frequency) trained on gradient-boosted trees with SHAP interpretability and Population Stability Index (PSI) drift monitoring.

---

## 1. Feature Engineering

12 engineered domain features extracted from claims and entity histories:

| Feature Name | Description | Intuition / Risk Signal |
| :--- | :--- | :--- |
| `claim_amount` | Requested reimbursement value | Extremely high amounts correlate with higher fraud exposure |
| `previous_claim_count` | Historical claim count for customer | Velocity metric; serial claimers show higher fraud propensity |
| `claims_last_30_days` | Short-term claim frequency burst | Sudden activity clusters indicate opportunistic or syndication fraud |
| `average_claim_amount` | Baseline historical claim size | Establishes the expected financial envelope |
| `amount_deviation` | Ratio of current claim to historical average | Large deviations (> 3.0x) represent anomalies |
| `amount_to_msrp_ratio` | Claim value divided by product MSRP | Claims claiming > 100% of MSRP require scrutiny |
| `device_claim_count` | Times this physical device was claimed | Re-claiming the same IMEI/serial number across users |
| `customer_claim_frequency` | Annualized claim filing frequency | Behavioral propensity |
| `location_frequency` | Number of claims filed from this geographic node | Regional organized fraud rings |
| `repair_shop_frequency` | Claims routed through specified shop | Collusive repair shops fabricating invoices |
| `days_since_last_claim` | Recency elapsed since previous claim | Short intervals (< 15 days) flag syndicates |
| `device_age` | Days between device purchase and incident date | Claims filed within 7 days of purchase (buyer's remorse/setup) |

---

## 2. Model Selection & Benchmark Results

Trained on 6,000 stratified samples (4,500 train, 1,500 validation, 30.85% fraud prevalence):

| Model Candidate | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.9122 | 0.9201 | 0.9161 | 0.9843 | 0.9705 |
| **Random Forest** | 0.9625 | 0.9417 | 0.9520 | 0.9926 | 0.9882 |
| **XGBoost (Selected)** | **0.9611** | **0.9611** | **0.9611** | **0.9959** | **0.9928** |

### Confusion Matrix (XGBoost Validation Set):
- **True Negatives (TN)**: 1,019
- **False Positives (FP)**: 18 (False Positive Rate: 1.74%)
- **False Negatives (FN)**: 18 (False Negative Rate: 3.89%)
- **True Positives (TP)**: 445

---

## 3. Explainable AI (XAI) with SHAP

- Uses `shap.TreeExplainer` on the gradient-boosted ensemble.
- For each prediction, computes exact Shapley feature attributions:
  $$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} [f(S \cup \{i\}) - f(S)]$$
- Outputs the **Top Risk Factors** explaining *why* the score was elevated, ensuring compliance with FCRA / adverse action notification standards.

---

## 4. Drift Detection (MLOps)

- **Metric**: Population Stability Index (PSI) computed over rolling inference windows vs baseline training distributions:
  $$\text{PSI} = \sum_{b=1}^{B} (A_b - E_b) \times \ln\left(\frac{A_b}{E_b}\right)$$
- **Thresholds**:
  - $\text{PSI} < 0.1$: **STABLE** (No action needed)
  - $0.1 \le \text{PSI} < 0.2$: **MODERATE DRIFT** (Warning, schedule retraining)
  - $\text{PSI} \ge 0.2$: **SIGNIFICANT DRIFT** (Trigger automated pipeline retrain)
