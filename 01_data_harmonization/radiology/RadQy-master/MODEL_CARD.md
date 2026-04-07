---
tool_id: radqy
tool_name: RadIQ / RadQy
card_type: data-utility
status: Partial
lab: [HITI]
poc: "TBD"
repo_path: "01_data_harmonization/radiology/RadQy-master/"
target_path: "01_data_harmonization/radiology/RadQy-master/"
short_description: "Automated QC metrics and interactive dashboard for MRI and CT images; FM-based OOD detection module pending."
input_modality: [DICOM, NIfTI]
output_type: [metrics, CSV, PNG]
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
weights_availability: "not-applicable"
external_validation: "not-applicable"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
---

# Model Card: RadIQ / RadQy

> **Status:** Partial | **Type:** data-utility | **Lab:** HITI | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/radiology/RadQy-master/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Describe in 2–4 sentences what QC metrics RadQy computes (e.g., SNR, CNR, ghosting, homogeneity), which modalities it supports, and what the interactive dashboard shows. Note that the FM-based OOD module is not yet implemented (see `model_cards/stubs/radiq-fm-ood.md`).

RadQy provides automated quality control metrics for MRI and CT images along with an interactive visualization dashboard. A foundation model-based out-of-distribution detection module is planned but not yet implemented.

## 2. Intended Use

Not applicable — this is a data processing utility without a learned prediction component.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | MRI, CT |
| File format | `.dcm`, `.mha`, `.nii`, `.mat` |
| Required fields / tags | TODO: list required DICOM tags or volume metadata |
| Preprocessing required upstream | None required; images should be de-identified |

### 3.2 Anonymization and PHI Requirements

> **TODO (POC: TBD):** State whether RadQy assumes input DICOM files are de-identified and whether it handles any PHI itself.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the QC metric algorithms (classical signal processing methods) and the dashboard technology (e.g., Streamlit, Flask). Note the boundary between the implemented QC module and the planned FM-OOD module.

### 4.2 Training Data

Not applicable — classical signal processing; no learned components in the current implementation.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add the install command and link to requirements file. Note CLI entry point (e.g., `radqy` or `python -m radqy`).

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal CLI command to run QC on a directory of DICOM files and launch the dashboard.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Per-image QC metrics, summary statistics |
| Output format | `.tsv`, `.csv`, `.png` thumbnails |
| Output location | Configurable output directory |

## 6. Performance

Not applicable — this tool does not produce predictions; it computes reference QC metrics.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document supported vs. unsupported modalities, known issues with specific DICOM variants, and any known edge cases where QC metrics are unreliable (e.g., very low-resolution images, non-standard acquisition protocols).

## 8. Ethical Considerations

### 8.1–8.3

Not applicable — this is a data quality measurement utility.

### 8.4 Data Governance

> **TODO (POC: TBD):** State de-identification assumptions for input data.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — quality gate applied after DICOM retrieval and before downstream feature extraction.

### 9.2 Upstream Dependencies

Typically follows DICOM retrieval via [Niffler](../Niffler/MODEL_CARD.md) or [HITI-Preproc](../HITI-Preproc/MODEL_CARD.md).

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List which MEFINDER tools depend on passing RadQy quality gates. The planned [RadIQ FM-OOD module](../../../model_cards/stubs/radiq-fm-ood.md) extends this tool.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add MRQy/RadQy publication citation if applicable.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | HITI |
| Contact | See PROJECT_CONTACTS.md |
| Status | Partial (FM-OOD module not yet implemented) |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
