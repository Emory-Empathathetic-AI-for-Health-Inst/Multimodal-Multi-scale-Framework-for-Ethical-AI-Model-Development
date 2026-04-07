---
tool_id: prostate-shape-distension
tool_name: Prostate Shape Distension
card_type: placeholder
status: Missing
lab: [Empathi]
poc: "TBD"
repo_path: ""
target_path: "02_feature_extraction/deep_features/"
short_description: "3D shape biomarker derived from prostate lesion segmentation masks."
input_modality: []
output_type: []
clinical_domain: [prostate-cancer]
last_updated: "2026-04-07"
---

# Model Card: Prostate Shape Distension

> **Status:** Missing | **Type:** placeholder | **Lab:** Empathi | **POC:** TBD
>
> **Target path:** `02_feature_extraction/deep_features/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Derives 3D shape distension biomarkers from prostate lesion segmentation masks produced by the Invisible Prostate Cancer Detection tool. Shape features capture lesion morphology relevant to cancer aggressiveness.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`02_feature_extraction` — shape biomarker derivation from segmentation output.

### 9.2 Upstream Dependencies

Will depend on [Invisible Prostate Cancer Detection](../../../02_feature_extraction/deep_features/prostate_lesion_detection/MODEL_CARD.md) for segmentation masks.

### 9.3 Downstream Consumers

Not yet applicable — tool not implemented.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
