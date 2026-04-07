---
tool_name: MuTriM
lab: "Empathi"
poc: "TBD"
repo_path: "03_multimodal_embedding/temporal_fusion/MuTriM_breast/"
short_description: "Multiscale deep learning model integrating longitudinal radiomics and pathomics for breast cancer recurrence prediction and NAC benefit stratification; under review."
category: "multimodal-embedding"
tags:
    - clinical: [breast-cancer]
    - data: [imaging, tabular]
last_updated: "2026-04-07"
publication: ""
package_url: ""
---

# Model Card: MuTriM

> **Status:** Implemented | **Type:** dl-model | **Lab:** Empathi | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/temporal_fusion/MuTriM_breast/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on what "multiscale" means in this context (e.g., spatial scales in imaging, temporal scales across treatment timepoints), what radiomic and pathomic features are fused, and the two prediction tasks (recurrence prediction and NAC — neoadjuvant chemotherapy — benefit stratification).

MuTriM integrates longitudinal radiomics and pathomics features across treatment timepoints using a multiscale deep learning approach to predict breast cancer recurrence and stratify patients by benefit from neoadjuvant chemotherapy (NAC). An associated publication is currently under review.

## 2. Intended Use

RESEARCH USE ONLY — Clinical validation in progress.

Intended users: ML researchers and oncology researchers working on longitudinal multimodal breast cancer outcome prediction. NAC benefit stratification output is intended for research cohort analysis only.

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Longitudinal radiomics features (MRI) + pathomics features (histology) |
| File format | TODO: CSV feature tables, or raw image inputs? Specify |
| Required fields / tags | TODO: required feature names and temporal indexing convention |
| Preprocessing required upstream | TODO: specify radiomics extraction pipeline (e.g., PyRadiomics) and pathomics extraction pipeline required before MuTriM |

Input feature tables must not contain direct patient identifiers. Raw images used for feature extraction must be de-identified upstream.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the multiscale architecture — how features from different spatial or temporal scales are represented and fused. Describe the model head for each prediction task (recurrence and NAC benefit).

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional breast cancer cohort |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Note if external datasets (e.g., TCGA-BRCA) were used. Add install command and list key dependencies. Show minimal commands for recurrence prediction and NAC benefit stratification.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Recurrence risk score; NAC benefit probability |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | Reference associated publication (under review) |

> **TODO (POC: TBD):** Report AUROC, C-index (survival), and comparison to unimodal baselines for both prediction tasks.

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis planned pending publication review and demographic metadata availability. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: sensitivity to radiomics feature extraction protocol, missing modality handling, performance on patients with fewer than the expected number of longitudinal timepoints.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** Describe the demographic composition of the training cohort and known or suspected performance variation by patient subgroup. NAC benefit stratification has direct treatment implications — demographic fairness is especially important.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Describe confounders in the longitudinal training data (e.g., treatment protocol variations over time, institution-specific imaging protocols) and how they were addressed.
- **Data Governance**:
  > **TODO (POC: TBD):** Describe data DUA and consent model. Note whether the dataset can be used for external validation. NAC benefit stratification must not be used to guide treatment decisions without expert oncologist review and prospective validation.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add publication citation once published. Acknowledge upstream feature extraction libraries (PyRadiomics, etc.).

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Empathi
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
