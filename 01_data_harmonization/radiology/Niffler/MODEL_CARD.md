---
tool_name: Niffler
lab: "HITI"
poc: "Beatrice Brown-Mulry"
repo_path: "01_data_harmonization/radiology/Niffler/"
short_description: "DICOM retrieval, metadata extraction, and anonymization framework for PACS/RIS systems."
category: "data-harmonization"
tags:
    - clinical: [radiology]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | DICOM (any modality supported by the connected PACS) |
| File format | `.dcm`; CSV query files for cold retrieval |
| Required fields / tags | PACS connection credentials; DICOM tags specified in retrieval config (e.g., AccessionNumber, PatientID) |
| Preprocessing required upstream | None — Niffler is typically the first step in the pipeline |

> **TODO (POC: Beatrice Brown-Mulry):** Describe Niffler's real-time PHI stripping behavior (e.g., which DICOM tags are removed), whether exported images are fully de-identified or require an additional anonymization step, and when downstream tools such as HITI-Preproc should be run afterward.

## 4. Technical Specifications

> **TODO (POC: Beatrice Brown-Mulry):** Briefly describe Niffler's modules (e.g., ColdDataRetriever, MetadataExtractor, DicomAnonymizer) and the underlying DICOM protocol used for PACS communication.

Not applicable — this is a data processing utility without a learned prediction component. No trained weights.

> **TODO (POC: Beatrice Brown-Mulry):** Add the install command and any PACS-side configuration prerequisites. Reference the requirements file if one exists in the Niffler directory. Provide the key command for a cold retrieval run and point to the README for full configuration details.

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

- **Bias and Fairness**:
  Not applicable — this tool retrieves and anonymizes data; it does not make predictions.
- **Confounding and Causal Risks**:
  Not applicable.
- **Data Governance**:
  > **TODO (POC: Beatrice Brown-Mulry):** Describe the consent and data governance model assumed for data retrieved via Niffler (e.g., retrospective IRB, de-identification standard used). Clarify what downstream data use restrictions apply to retrieved data. State any operational requirements for connecting Niffler to a production PACS (e.g., IRB approval, IT/security sign-off, network access controls).

## 9. Citation and Attribution

> **TODO (POC: Beatrice Brown-Mulry):** Add the Niffler publication BibTeX if one exists, and acknowledge any upstream DICOM libraries used.

## 10. Maintenance and Contact

**Name**: Beatrice Brown-Mulry
**Affiliation**: HITI
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
