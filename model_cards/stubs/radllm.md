---
tool_id: radllm
tool_name: RadLLM
card_type: placeholder
status: Missing
lab: [HITI]
poc: "TBD"
repo_path: ""
target_path: "01_data_harmonization/radiology/"
short_description: "Converts free-text radiology reports into structured labels for monitoring and training loops."
input_modality: []
output_type: []
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
---

# Model Card: RadLLM

> **Status:** Missing | **Type:** placeholder | **Lab:** HITI | **POC:** TBD
>
> **Target path:** `01_data_harmonization/radiology/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Uses a large language model to convert free-text radiology reports into structured labels. Intended to support model monitoring pipelines and to generate training labels from historical radiology reports without manual annotation.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — structured label generation from radiology reports.

### 9.2 Upstream Dependencies

Not yet applicable — will take radiology reports as text input; de-identification required upstream.

### 9.3 Downstream Consumers

Expected to provide structured labels for training and monitoring downstream MEFINDER models.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | HITI |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
