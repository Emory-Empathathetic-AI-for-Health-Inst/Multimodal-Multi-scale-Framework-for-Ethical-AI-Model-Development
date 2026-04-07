---
tool_id: mserg
tool_name: MSERg
card_type: placeholder
status: Missing
lab: [Empathi]
poc: "TBD"
repo_path: ""
target_path: "01_data_harmonization/radiology/"
short_description: "Radiology-pathology co-registration pipeline; upstream dependency for multimodal fusion models."
input_modality: []
output_type: []
clinical_domain: [multi-domain]
last_updated: "2026-04-07"
---

# Model Card: MSERg

> **Status:** Missing | **Type:** placeholder | **Lab:** Empathi | **POC:** TBD
>
> **Target path:** `01_data_harmonization/radiology/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Radiology-pathology co-registration pipeline that spatially aligns MRI imaging data with histopathology slides. This is an upstream dependency for multimodal fusion models that require spatially coherent cross-modality features.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — radiology-pathology co-registration preprocessing.

### 9.2 Upstream Dependencies

Not yet applicable — tool not implemented.

### 9.3 Downstream Consumers

Expected to be required upstream of [SMuRF](../../../03_multimodal_embedding/deep_joint_embedding/SMuRF_MultiModal_OPSCC/MODEL_CARD.md) and other radiology-pathology fusion tools.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
