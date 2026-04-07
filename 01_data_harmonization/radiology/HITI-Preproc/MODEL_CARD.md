---
tool_name: DICOM PreProcessor (HITI-Preproc)
lab: "HITI"
poc: "Beatrice Brown-Mulry"
repo_path: "01_data_harmonization/radiology/HITI-Preproc/"
short_description: "Lightweight pip-installable DICOM preprocessing package for standardization and format conversion."
category: "data-harmonization"
tags:
    - clinical: [radiology]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: "hiti-preproc"
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | DICOM (radiology images) |
| File format | `.dcm` |
| Required fields / tags | TODO: list required DICOM tags |
| Preprocessing required upstream | Images should be retrieved (e.g., via Niffler) and de-identified before processing |

> **TODO (POC: Beatrice Brown-Mulry):** State whether HITI-Preproc assumes inputs are already de-identified or whether it handles any PHI stripping itself.

## 4. Technical Specifications

> **TODO (POC: Beatrice Brown-Mulry):** Describe the preprocessing operations available (e.g., Hounsfield unit windowing for CT, intensity normalization for MRI, conversion to PNG/NIfTI).

Not applicable — this is a data processing utility without a learned prediction component. No trained weights.

```bash
pip install hiti-preproc
```

> **TODO (POC: Beatrice Brown-Mulry):** Add any additional system dependencies or Python version requirements. Link to requirements file if present. Show a minimal usage example. Reference `example.ipynb` for full walkthrough.

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

- **Bias and Fairness**:
  Not applicable — this is a data processing utility without a learned prediction component.
- **Confounding and Causal Risks**:
  Not applicable.
- **Data Governance**:
  > **TODO (POC: Beatrice Brown-Mulry):** State what de-identification is assumed to have occurred upstream before using this tool.

## 9. Citation and Attribution

> **TODO (POC: Beatrice Brown-Mulry):** Add publication or package citation if applicable.

## 10. Maintenance and Contact

**Name**: Beatrice Brown-Mulry
**Affiliation**: HITI
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
