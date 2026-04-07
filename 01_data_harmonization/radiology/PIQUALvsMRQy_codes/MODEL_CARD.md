---
tool_name: MRQy Quality Control Experiments (PI-QUAL vs MRQy)
lab: "Empathi"
poc: "TBD"
repo_path: "01_data_harmonization/radiology/PIQUALvsMRQy_codes/"
short_description: "Experimental research code comparing PI-QUAL and MRQy prostate MRI quality metrics; includes unsupervised clustering; not a packaged tool."
category: "data-harmonization"
tags:
    - clinical: [radiology, prostate-cancer]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
---

# Model Card: MRQy Quality Control Experiments (PI-QUAL vs MRQy)

> **Status:** Partial | **Type:** data-utility | **Lab:** Empathi | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/radiology/PIQUALvsMRQy_codes/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Describe in 2–4 sentences what this experiment set demonstrates — e.g., the comparison methodology between PI-QUAL and MRQy metrics on prostate MRI, the clustering experiment, and any conclusions drawn. Clarify that this is experimental research code, not a reusable pipeline component.

**Important:** This directory contains experimental comparison code, not a packaged or reusable tool. It documents research on prostate MRI quality control metric comparison (PI-QUAL vs. MRQy) including unsupervised clustering analysis. Do not use this code as a drop-in replacement for RadQy.

## 2. Intended Use

Not applicable — this is experimental research code, not a reusable pipeline component.

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Prostate MRI (DICOM) |
| File format | `.dcm` |
| Required fields / tags | TODO: list required DICOM tags or metadata |
| Preprocessing required upstream | TODO |

> **TODO (POC: TBD):** State de-identification requirements for the prostate MRI inputs used in these experiments.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the PI-QUAL scoring method, the MRQy metrics computed, and the unsupervised clustering approach used in the comparison.

Not applicable — classical signal processing; no learned components.

> **TODO (POC: TBD):** List the Python dependencies and how to set up the environment to run these scripts/notebooks. Describe how to reproduce the comparison experiment. Reference any notebooks that demonstrate the analysis.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | QC metric scores, clustering results |
| Output format | `.csv`, plots |
| Output location | TODO |

## 6. Performance

Not applicable — this is a QC metric comparison study, not a predictive model.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Note that this code is not a standalone packaged tool and may require adaptation before reuse. Document dataset-specific assumptions baked into the experiment.

## 8. Ethical Considerations

Not applicable — this is a data quality measurement research experiment.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add the PI-QUAL and MRQy paper citations. Add any associated MEFINDER publication if applicable.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Empathi
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
