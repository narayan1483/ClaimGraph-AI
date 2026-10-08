# ClaimGraph AI — Deterministic Risk Calibration Engine

> **Engine Thesis**: In regulated insurance and financial domains, decisions cannot legally depend on opaque, non-deterministic black-box LLM prompts. The Risk Engine calibrates mathematical probabilities, graph topologies, and factual heuristics into auditable risk bands.

---

## 1. Mathematical Calibration Formula

The composite risk score is computed as a weighted combination of three independent signals:

$$\text{Final Risk Score} = (w_{\text{ml}} \times S_{\text{ml}}) + (w_{\text{graph}} \times S_{\text{graph}}) + (w_{\text{agent}} \times S_{\text{agent}})$$

Where standard weights are:
- $w_{\text{ml}} = 0.45$: XGBoost calibrated fraud probability
- $w_{\text{graph}} = 0.35$: Neo4j graph ring & centrality penalty score
- $w_{\text{agent}} = 0.20$: Multimodal tamper & document heuristic penalty score

---

## 2. Hard Policy Overrides (Determinism Guardrails)

Certain critical fraud indicators trigger an immediate, non-negotiable override to **CRITICAL** risk regardless of other sub-scores:
1. **Perceptual Hash Duplicate**: Image identical to previously paid claim ($pHash \text{ Hamming distance} \le 3$).
2. **Serial Number Collision**: Same device claimed under different customer identity within 90 days.
3. **EXIF Temporal Mismatch**: Photo metadata date predates device purchase date by $> 30$ days.
4. **Altered Invoice Flag**: Document OCR shows mismatched mathematical totals or font modifications.

---

## 3. Standardized Risk Bands

| Score Range | Risk Band | Action Recommendation | Workflow Route |
| :---: | :---: | :---: | :---: |
| $0.00 - 0.34$ | **LOW** | `APPROVE` / Fast-Track Payout | Automated Straight-Through Processing |
| $0.35 - 0.69$ | **MEDIUM** | `NORMAL_PROCESSING` | Standard Claims Adjuster Review |
| $0.70 - 0.84$ | **HIGH** | `INVESTIGATION` | Fraud Specialist Review Queue |
| $0.85 - 1.00$ | **CRITICAL** | `REJECT` / SIU Referral | Special Investigation Unit (SIU) Referral |
