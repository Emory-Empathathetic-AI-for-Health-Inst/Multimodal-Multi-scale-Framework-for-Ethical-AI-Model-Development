---
tool_id: radiq-fm-ood
tool_name: RadIQ (FM-OOD module)
card_type: placeholder
status: Missing
lab: [HITI]
poc: "TBD"
repo_path: ""
target_path: "01_data_harmonization/radiology/"
short_description: "Foundation model-based out-of-distribution detection extending the existing RadQy QC infrastructure."
input_modality: []
output_type: []
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
---

# Model Card: RadIQ (FM-OOD module)

> **Status:** Missing | **Type:** placeholder | **Lab:** HITI | **POC:** TBD
>
> **Target path:** `01_data_harmonization/radiology/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Foundation model-based out-of-distribution (OOD) detection module that extends the existing [RadQy](../../../01_data_harmonization/radiology/RadQy-master/MODEL_CARD.md) QC infrastructure. Uses foundation model embeddings to detect images that fall outside the training distribution of downstream models. Also see: [Anomaly Detection](anomaly-detection.md) (planned by Mayo, related scope).

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — quality gate using FM-based OOD detection.

### 9.2 Upstream Dependencies

Extends [RadQy](../../../01_data_harmonization/radiology/RadQy-master/MODEL_CARD.md).

### 9.3 Downstream Consumers

Expected to gate input to downstream feature extraction and multimodal embedding tools.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | HITI |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
