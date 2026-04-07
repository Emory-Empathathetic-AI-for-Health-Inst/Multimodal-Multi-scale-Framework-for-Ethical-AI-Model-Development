---
tool_id: hiti-preproc
tool_name: DICOM PreProcessor (HITI-Preproc)
card_type: data-utility
status: Implemented
lab: [HITI]
poc: "Beatrice Brown-Mulry"
repo_path: "01_data_harmonization/radiology/HITI-Preproc/"
target_path: "01_data_harmonization/radiology/HITI-Preproc/"
short_description: "Lightweight pip-installable DICOM preprocessing package for standardization and format conversion."
input_modality: [DICOM]
output_type: [DICOM, PNG, NIfTI]
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
weights_availability: "not-applicable"
external_validation: "not-applicable"
publication: ""
pypi_package: "hiti-preproc"
depends_on: []
used_by: []
---

# Model Card: DICOM PreProcessor (HITI-Preproc)

> **Status:** Implemented | **Type:** data-utility | **Lab:** HITI | **POC:** Beatrice Brown-Mulry
>
> **Repo path:** `01_data_harmonization/radiology/HITI-Preproc/`

---

## 1. Purpose and Scope

> **TODO (POC: Beatrice Brown-Mulry):** Expand with 2–4 sentences describing what preprocessing operations HITI-Preproc performs (e.g., windowing, normalization, format conversion, DICOM tag standardization), its current alpha status, and how it fits into the Stage 01 data harmonization pipeline.

HITI-Preproc is a lightweight DICOM preprocessing package installable via pip (`pip install hiti-preproc`). It provides standardization and format conversion utilities for DICOM images.

## 2. Intended Use

Not applicable — this is a data processing utility without a learned prediction component.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | DICOM (radiology images) |
| File format | `.dcm` |
| Required fields / tags | TODO: list required DICOM tags |
| Preprocessing required upstream | Images should be retrieved (e.g., via Niffler) and de-identified before processing |

### 3.2 Anonymization and PHI Requirements

> **TODO (POC: Beatrice Brown-Mulry):** State whether HITI-Preproc assumes inputs are already de-identified or whether it handles any PHI stripping itself.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: Beatrice Brown-Mulry):** Describe the preprocessing operations available (e.g., Hounsfield unit windowing for CT, intensity normalization for MRI, conversion to PNG/NIfTI).

### 4.2 Training Data

Not applicable — this is a data processing utility without a learned prediction component.

### 4.3 Installation and Dependencies

```bash
pip install hiti-preproc
```

> **TODO (POC: Beatrice Brown-Mulry):** Add any additional system dependencies or Python version requirements. Link to requirements file if present.

### 4.4 Inference / Usage

> **TODO (POC: Beatrice Brown-Mulry):** Show a minimal usage example. Reference `example.ipynb` for full walkthrough.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Preprocessed images |
| Output format | `.dcm`, `.png`, `.nii.gz` (configurable) |
| Output location | Configurable output directory |

## 6. Performance

Not applicable — this tool does not produce predictions.

## 7. Known Limitations and Failure Modes

> **TODO (POC: Beatrice Brown-Mulry):** Note alpha status limitations, known unsupported modalities or DICOM variants, and any known issues with specific scanner manufacturers.

## 8. Ethical Considerations

### 8.1–8.3

Not applicable — this is a data processing utility without a learned prediction component.

### 8.4 Data Governance

> **TODO (POC: Beatrice Brown-Mulry):** State what de-identification is assumed to have occurred upstream before using this tool.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — preprocessing step following DICOM retrieval.

### 9.2 Upstream Dependencies

Typically follows DICOM retrieval via [Niffler](../Niffler/MODEL_CARD.md).

### 9.3 Downstream Consumers

> **TODO (POC: Beatrice Brown-Mulry):** List which MEFINDER tools consume HITI-Preproc output. Use relative links.

## 10. Citation and Attribution

> **TODO (POC: Beatrice Brown-Mulry):** Add publication or package citation if applicable.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | Beatrice Brown-Mulry |
| Lab | HITI |
| Contact | See PROJECT_CONTACTS.md |
| Status | Implemented |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
