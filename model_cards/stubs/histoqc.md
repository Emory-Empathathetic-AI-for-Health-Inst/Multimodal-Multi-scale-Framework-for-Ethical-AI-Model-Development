---
tool_id: histoqc
tool_name: HistoQC
card_type: placeholder
status: Missing
lab: [Empathi]
poc: "TBD"
repo_path: ""
target_path: "01_data_harmonization/pathology/"
short_description: "H&E slide quality control; archive present but not yet extracted or validated as runnable."
input_modality: []
output_type: []
clinical_domain: [multi-domain]
last_updated: "2026-04-07"
---

# Model Card: HistoQC

> **Status:** Missing | **Type:** placeholder | **Lab:** Empathi | **POC:** TBD
>
> **Target path:** `01_data_harmonization/pathology/`

This tool is planned but not yet implemented. An archive is present in the repository but has not been extracted or validated as runnable. See `PROJECT_CONTACTS.md` for the assigned POC.

**Description:** Quality control tool for H&E whole-slide images. Produces quality metrics and flags slides with artifacts, focus issues, or staining irregularities before downstream pathomics analysis.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — pathology data quality gate.

### 9.2 Upstream Dependencies

Not yet applicable — tool not implemented.

### 9.3 Downstream Consumers

Expected to gate input to [Histotyping](histotyping.md), [CAI](cai.md), and other pathomics tools.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Status | Missing (archive present but not extracted) |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
