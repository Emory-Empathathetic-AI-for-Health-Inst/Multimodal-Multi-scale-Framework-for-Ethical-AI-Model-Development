---
tool_id: rad-path-prostate-classifier
tool_name: Rad-Path Prostate Recurrence Classifier
card_type: dl-model
status: Partial
lab: [Empathi]
poc: "TBD"
repo_path: "03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/"
target_path: "03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/"
short_description: "Classical ML classifier combining radiological and pathological features for biochemical recurrence prediction after radical prostatectomy."
input_modality: [multiple]
output_type: [labels]
clinical_domain: [prostate-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: [prostate-lesion-detection]
used_by: []
---

# Model Card: Rad-Path Prostate Recurrence Classifier

> **Status:** Partial | **Type:** dl-model | **Lab:** Empathi | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on what features are combined (radiological: MRI-derived, pathological: Gleason grade, margin status, etc.), the classical ML approach used (e.g., logistic regression, SVM, random forest), and the clinical context — biochemical recurrence (BCR) after radical prostatectomy as a key outcome for treatment escalation decisions.

This classifier combines engineered radiological features from prostate MRI with pathological features from surgical pathology to predict biochemical recurrence after radical prostatectomy. It uses classical ML (non-deep-learning) feature fusion. This tool is related to the ClaD and RadClip roadmap items.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: Prostate cancer researchers and computational oncologists working on post-prostatectomy BCR risk stratification.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Radiological features (MRI-derived) + pathological features (surgical pathology report) |
| File format | TODO: CSV feature tables |
| Required fields / tags | TODO: specify required feature columns for radiology and pathology inputs |
| Preprocessing required upstream | Prostate MRI lesion segmentation via Invisible Prostate Cancer Detection; radiomics feature extraction; pathology feature extraction |

### 3.2 Anonymization and PHI Requirements

Feature tables must not contain direct patient identifiers. Source images and pathology reports used for feature extraction must be de-identified upstream.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the ML algorithm(s) used (e.g., logistic regression, gradient boosting), the feature selection approach, and how radiology and pathology features are combined (early fusion, late fusion, or stacking).

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional prostate cancer cohort |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and list dependencies. Note scikit-learn / other ML library versions.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to run inference on new feature tables.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | BCR risk score or binary BCR prediction |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report AUROC and C-index for BCR prediction. Report comparison to pathology-only and imaging-only baselines.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document the partial status — what is incomplete relative to the roadmap. Note sensitivity to feature extraction quality and known limitations of classical ML versus the planned DL-based ClaD/RadClip tools.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Prostate cancer incidence, treatment patterns, and pathology differ by race (notably higher incidence and mortality in Black men). Describe training cohort demographics and performance variation by race and age.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** BCR is confounded by PSA threshold definitions and follow-up duration. Describe how these were standardized in the training cohort.

### 8.3 Clinical Deployment Safeguards

BCR risk stratification must not inform treatment decisions (e.g., adjuvant radiation) without expert urologist and radiation oncologist review.

### 8.4 Data Governance

> **TODO (POC: TBD):** Describe data DUA and consent model.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`03_multimodal_embedding` — engineered feature fusion for prostate cancer outcome prediction.

### 9.2 Upstream Dependencies

- [Invisible Prostate Cancer Detection](../../../02_feature_extraction/deep_features/prostate_lesion_detection/MODEL_CARD.md): segmentation masks used for radiological feature extraction.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List MEFINDER use cases that consume BCR predictions. Note the planned ClaD and RadClip tools as successors to this approach.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX if one exists.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Contact | See PROJECT_CONTACTS.md |
| Status | Partial |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
