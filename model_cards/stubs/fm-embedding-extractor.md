---
tool_id: fm-embedding-extractor
tool_name: Foundation Model Embedding Extractor (standalone)
card_type: placeholder
status: Missing
lab: [HITI]
poc: "TBD"
repo_path: ""
target_path: "02_feature_extraction/deep_features/"
short_description: "Reusable standalone tool for extracting foundation model embeddings from medical images; currently embedded inside mammo_vlm_ss."
input_modality: []
output_type: []
clinical_domain: [multi-domain]
last_updated: "2026-04-07"
---

# Model Card: Foundation Model Embedding Extractor (standalone)

> **Status:** Missing | **Type:** placeholder | **Lab:** HITI | **POC:** TBD
>
> **Target path:** `02_feature_extraction/deep_features/`

This tool is planned but not yet implemented as a standalone package. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** A reusable standalone tool for extracting embeddings from medical images using foundation models. The embedding capability currently exists inside [mammo_vlm_ss](../../../03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/MODEL_CARD.md) but has not been packaged as a modality-agnostic reusable tool. This extraction is needed to support the [Atlas](atlas.md) tool and other downstream consumers.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`02_feature_extraction` — reusable foundation model embedding extraction.

### 9.2 Upstream Dependencies

Not yet applicable — will wrap existing FM capabilities from mammo_vlm_ss and potentially other FMs.

### 9.3 Downstream Consumers

Expected to provide embeddings for [Atlas](atlas.md) and other embedding-based tools.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | HITI |
| Status | Missing — capability exists inside mammo_vlm_ss but not packaged standalone |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
