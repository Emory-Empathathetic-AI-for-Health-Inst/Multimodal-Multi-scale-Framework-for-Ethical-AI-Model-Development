---
tool_id: cai
tool_name: Cribriform Area Index (CAI)
card_type: placeholder
status: Missing
lab: [Empathi]
poc: "TBD"
repo_path: ""
target_path: "02_feature_extraction/pathomics/"
short_description: "Pathology biomarker quantifying cribriform growth pattern area from prostate H&E slides for adverse outcome prediction."
input_modality: []
output_type: []
clinical_domain: [prostate-cancer]
last_updated: "2026-04-07"
---

# Model Card: Cribriform Area Index (CAI)

> **Status:** Missing | **Type:** placeholder | **Lab:** Empathi | **POC:** TBD
>
> **Target path:** `02_feature_extraction/pathomics/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Computes the Cribriform Area Index from prostate H&E histology slides. The cribriform growth pattern is associated with adverse prostate cancer outcomes; CAI quantifies its extent for use in downstream risk stratification models.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`02_feature_extraction` — pathomics biomarker extraction.

### 9.2 Upstream Dependencies

Will depend on [HistoQC](histoqc.md) for slide quality control upstream.

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
