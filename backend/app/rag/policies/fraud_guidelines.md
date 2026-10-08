# ClaimGraph AI — Anti-Fraud Detection & Prevention Guidelines (FG-2026-v1)

## 1. Operational Fraud Classification
Fraudulent activity within the warranty and insurance processing pipeline is categorized into:
- **Opportunistic Claim Inflation**: Exaggerating the extent of genuine damage or submitting outdated replacement estimates.
- **Premeditated Fabrication**: Filing claims for pre-damaged units, fictitious devices, or staged staged loss/theft occurrences.
- **Organized Fraud Rings**: Coordinated rings exploiting multi-identity syndicates, shared physical devices across accounts, and complicit repair facilities.

## 2. Primary Red Flag Indicators (RFIs)
- **RFI-1 (Rapid Claim Genesis)**: Claims initiated within seven (7) days of policy inception or coverage limit upgrade.
- **RFI-2 (Device Sharing Collision)**: Any hardware serial number or IMEI appearing across more than one customer profile or associated with previous paid total-loss settlements.
- **RFI-3 (Metadata Inconsistency)**: Image EXIF timestamps that contradict the claimed incident date, or digital forensic indications of photo alteration, cropping, or stock photo reuse.
- **RFI-4 (High Claim Velocity)**: Three (3) or more claims filed by the same policyholder or originating from the same physical address within a 90-day rolling window.
- **RFI-5 (Suspicious Repair Shop Pattern)**: Repeated claims routed through an unverified repair vendor with recurring uniform quotes, excessive labor markups (>40%), or identical invoice boilerplate.
- **RFI-6 (Disproportionate Damage Narrative)**: Description claiming minor drops resulting in catastrophic internal logic board or structural destruction inconsistent with observed exterior shell impact.

## 3. Mandatory Fraud Response Matrix
- When any single critical RFI is triggered, automated adjudication must be immediately suspended.
- Claims triggering two or more RFIs must be assigned risk score >= 0.70 and routed to the Special Investigation Unit (SIU) for comprehensive agentic inquiry.
