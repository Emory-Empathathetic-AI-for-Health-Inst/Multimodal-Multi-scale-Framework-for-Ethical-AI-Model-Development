---
tool_name: RadIQ / RadQy
lab: "HITI"
poc: "TBD"
repo_path: "01_data_harmonization/radiology/RadQy-master/"
short_description: "Automated QC metrics and interactive dashboard for MRI and CT images; FM-based OOD detection module pending."
category: "data-harmonization"
tags:
    - clinical: [radiology]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | MRI, CT |
| File format | `.dcm`, `.mha`, `.nii`, `.mat` |
| Required fields / tags | TODO: list required DICOM tags or volume metadata |
| Preprocessing required upstream | None required; images should be de-identified |

> **TODO (POC: TBD):** State whether RadQy assumes input DICOM files are de-identified and whether it handles any PHI itself.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the QC metric algorithms (classical signal processing methods) and the dashboard technology (e.g., Streamlit, Flask). Note the boundary between the implemented QC module and the planned FM-OOD module.

Not applicable — classical signal processing; no learned components in the current implementation.

> **TODO (POC: TBD):** Add the install command and link to requirements file. Note CLI entry point (e.g., `radqy` or `python -m radqy`). Show the minimal CLI command to run QC on a directory of DICOM files and launch the dashboard.

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

- **Bias and Fairness**:
  Not applicable — this is a data quality measurement utility.
- **Confounding and Causal Risks**:
  Not applicable.
- **Data Governance**:
  > **TODO (POC: TBD):** State de-identification assumptions for input data.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add MRQy/RadQy publication citation if applicable.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: HITI
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
