---
tool_id: roi-lift
tool_name: ROI-Lift
card_type: placeholder
status: Missing
lab: [HITI]
poc: "Beatrice Brown-Mulry"
repo_path: ""
target_path: "01_data_harmonization/radiology/"
short_description: "Converts 2D ROIs into 3D ROIs on spatially aligned digital breast tomosynthesis (DBT) images."
input_modality: []
output_type: []
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
---

# Model Card: ROI-Lift

> **Status:** Missing | **Type:** placeholder | **Lab:** HITI | **POC:** Beatrice Brown-Mulry
>
> **Target path:** `01_data_harmonization/radiology/`

This tool is planned but not yet implemented. See `PROJECT_CONTACTS.md` for the assigned POC and target contribution path.

**Description:** Converts 2D region-of-interest (ROI) annotations into 3D ROIs on spatially aligned digital breast tomosynthesis (DBT) images. Enables 3D analysis workflows from datasets that were annotated in 2D.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — 2D-to-3D ROI lifting for DBT preprocessing.

### 9.2 Upstream Dependencies

Not yet applicable — will require spatially aligned DBT image volumes and 2D ROI annotations.

### 9.3 Downstream Consumers

Expected to provide 3D ROIs for downstream mammography feature extraction and embedding tools.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | Beatrice Brown-Mulry |
| Lab | HITI |
| Status | Missing |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
