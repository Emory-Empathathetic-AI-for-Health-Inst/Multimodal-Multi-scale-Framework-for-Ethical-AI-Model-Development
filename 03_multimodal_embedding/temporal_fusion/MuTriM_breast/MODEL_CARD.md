---
tool_id: mutrim
tool_name: MuTriM
card_type: dl-model
status: Implemented
lab: [Empathi]
poc: "TBD"
repo_path: "03_multimodal_embedding/temporal_fusion/MuTriM_breast/"
target_path: "03_multimodal_embedding/temporal_fusion/MuTriM_breast/"
short_description: "Multiscale deep learning model integrating longitudinal radiomics and pathomics for breast cancer recurrence prediction and NAC benefit stratification; under review."
input_modality: [multiple]
output_type: [labels]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
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

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Longitudinal radiomics features (MRI) + pathomics features (histology) |
| File format | TODO: CSV feature tables, or raw image inputs? Specify |
| Required fields / tags | TODO: required feature names and temporal indexing convention |
| Preprocessing required upstream | TODO: specify radiomics extraction pipeline (e.g., PyRadiomics) and pathomics extraction pipeline required before MuTriM |

### 3.2 Anonymization and PHI Requirements

Input feature tables must not contain direct patient identifiers. Raw images used for feature extraction must be de-identified upstream.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the multiscale architecture — how features from different spatial or temporal scales are represented and fused. Describe the model head for each prediction task (recurrence and NAC benefit).

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional breast cancer cohort |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Note if external datasets (e.g., TCGA-BRCA) were used.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and list key dependencies. Link to requirements file.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show minimal commands for recurrence prediction and NAC benefit stratification.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Recurrence risk score; NAC benefit probability |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | Reference associated publication (under review) |

> **TODO (POC: TBD):** Report AUROC, C-index (survival), and comparison to unimodal baselines for both prediction tasks.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis planned pending publication review and demographic metadata availability. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: sensitivity to radiomics feature extraction protocol, missing modality handling, performance on patients with fewer than the expected number of longitudinal timepoints.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Describe the demographic composition of the training cohort and known or suspected performance variation by patient subgroup. NAC benefit stratification has direct treatment implications — demographic fairness is especially important.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Describe confounders in the longitudinal training data (e.g., treatment protocol variations over time, institution-specific imaging protocols) and how they were addressed.

### 8.3 Clinical Deployment Safeguards

NAC benefit stratification must not be used to guide treatment decisions without expert oncologist review and prospective validation. Under-representation of certain patient subgroups in training data may lead to inequitable predictions.

### 8.4 Data Governance

> **TODO (POC: TBD):** Describe data DUA and consent model. Note whether the dataset can be used for external validation.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`03_multimodal_embedding` — temporal fusion of longitudinal radiomic and pathomic features for breast cancer outcome prediction.

### 9.2 Upstream Dependencies

Requires radiomic feature extraction (planned: [Delta Radiomics](../../../model_cards/stubs/delta-radiomics-prostate.md) provides a related capability for prostate; breast equivalent TBD) and pathomic feature extraction upstream.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List MEFINDER use cases that consume MuTriM predictions.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add publication citation once published. Acknowledge upstream feature extraction libraries (PyRadiomics, etc.).

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Contact | See PROJECT_CONTACTS.md |
| Status | Implemented (publication under review) |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
