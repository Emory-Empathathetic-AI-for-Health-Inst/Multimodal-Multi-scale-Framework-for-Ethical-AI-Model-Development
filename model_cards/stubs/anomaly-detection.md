---
tool_id: anomaly-detection
tool_name: Anomaly Detection
card_type: placeholder
status: Missing
lab: [Mayo]
poc: "TBD"
repo_path: ""
target_path: "01_data_harmonization/radiology/"
short_description: "OOD detection for safe cross-institution deployment; also completes the RadIQ FM-OOD component."
input_modality: []
output_type: []
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
---

# Model Card: Anomaly Detection

> **Status:** Missing | **Type:** placeholder | **Lab:** Mayo | **POC:** TBD
>
> **Target path:** `01_data_harmonization/radiology/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Out-of-distribution anomaly detection for safe cross-institution model deployment. Also intended to complete the FM-OOD component of [RadIQ](radiq-fm-ood.md). Detects images or data that fall outside the training distribution, enabling safe gating before downstream models are applied.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — cross-institution deployment safety layer.

### 9.2 Upstream Dependencies

Not yet applicable — tool not implemented. Will likely complement [RadQy](../../../01_data_harmonization/radiology/RadQy-master/MODEL_CARD.md) and [RadIQ FM-OOD](radiq-fm-ood.md).

### 9.3 Downstream Consumers

Expected to gate input to all downstream MEFINDER models when deployed at new institutions.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Mayo |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
