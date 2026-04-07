---
tool_id: niffler
tool_name: Niffler
card_type: data-utility
status: Implemented
lab: [HITI]
poc: "Beatrice Brown-Mulry"
repo_path: "01_data_harmonization/radiology/Niffler/"
target_path: "01_data_harmonization/radiology/Niffler/"
short_description: "DICOM retrieval, metadata extraction, and anonymization framework for PACS/RIS systems."
input_modality: [DICOM]
output_type: [DICOM, PNG, NIfTI, CSV]
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
weights_availability: "not-applicable"
external_validation: "not-applicable"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
---

# Model Card: Niffler

> **Status:** Implemented | **Type:** data-utility | **Lab:** HITI | **POC:** Beatrice Brown-Mulry
>
> **Repo path:** `01_data_harmonization/radiology/Niffler/`

---

## 1. Purpose and Scope

> **TODO (POC: Beatrice Brown-Mulry):** Expand this section with 2–4 sentences describing Niffler's role in PACS/RIS retrieval, its real-time streaming and on-demand cold retrieval modes, and its position as the primary DICOM ingestion layer in the MEFINDER pipeline (Stage 01 — data harmonization).

Niffler is a DICOM framework for retrieving images from PACS/RIS systems, extracting metadata, and anonymizing patient information. It supports real-time streaming and on-demand cold retrieval.

## 2. Intended Use

Not applicable — this is a data processing utility without a learned prediction component.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | DICOM (any modality supported by the connected PACS) |
| File format | `.dcm`; CSV query files for cold retrieval |
| Required fields / tags | PACS connection credentials; DICOM tags specified in retrieval config (e.g., AccessionNumber, PatientID) |
| Preprocessing required upstream | None — Niffler is typically the first step in the pipeline |

### 3.2 Anonymization and PHI Requirements

> **TODO (POC: Beatrice Brown-Mulry):** Describe Niffler's real-time PHI stripping behavior (e.g., which DICOM tags are removed), whether exported images are fully de-identified or require an additional anonymization step, and when downstream tools such as HITI-Preproc should be run afterward.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: Beatrice Brown-Mulry):** Briefly describe Niffler's modules (e.g., ColdDataRetriever, MetadataExtractor, DicomAnonymizer) and the underlying DICOM protocol used for PACS communication.

### 4.2 Training Data

Not applicable — this is a data processing utility without a learned prediction component.

### 4.3 Installation and Dependencies

> **TODO (POC: Beatrice Brown-Mulry):** Add the install command and any PACS-side configuration prerequisites. Reference the requirements file if one exists in the Niffler directory.

### 4.4 Inference / Usage

> **TODO (POC: Beatrice Brown-Mulry):** Provide the key command for a cold retrieval run and point to the README for full configuration details.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | DICOM images, PNG/NIfTI exports, CSV metadata |
| Output format | `.dcm`, `.png`, `.nii.gz`, `.csv` |
| Output location | Configurable output directory |

## 6. Performance

Not applicable — this tool does not produce predictions.

## 7. Known Limitations and Failure Modes

> **TODO (POC: Beatrice Brown-Mulry):** Document known limitations such as PACS vendor compatibility constraints, behavior when DICOM tags are missing or malformed, and any known issues with specific modalities or scanner manufacturers.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

Not applicable — this tool retrieves and anonymizes data; it does not make predictions.

### 8.2 Confounding and Causal Risks

Not applicable.

### 8.3 Clinical Deployment Safeguards

> **TODO (POC: Beatrice Brown-Mulry):** State any operational requirements for connecting Niffler to a production PACS (e.g., IRB approval, IT/security sign-off, network access controls).

### 8.4 Data Governance

> **TODO (POC: Beatrice Brown-Mulry):** Describe the consent and data governance model assumed for data retrieved via Niffler (e.g., retrospective IRB, de-identification standard used). Clarify what downstream data use restrictions apply to retrieved data.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — primary DICOM ingestion entry point.

### 9.2 Upstream Dependencies

None — Niffler operates directly against a PACS/RIS system.

### 9.3 Downstream Consumers

> **TODO (POC: Beatrice Brown-Mulry):** List the MEFINDER tools that typically consume Niffler's output (e.g., HITI-Preproc, RadQy, mammo_vlm_ss). Use relative links once those MODEL_CARD.md files exist.

## 10. Citation and Attribution

> **TODO (POC: Beatrice Brown-Mulry):** Add the Niffler publication BibTeX if one exists, and acknowledge any upstream DICOM libraries used.

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
