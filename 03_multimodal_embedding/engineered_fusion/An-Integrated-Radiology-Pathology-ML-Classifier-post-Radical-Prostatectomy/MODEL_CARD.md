---
tool_name: Rad-Path Prostate Recurrence Classifier
lab: "Empathi"
poc: "TBD"
repo_path: "03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/"
short_description: "Classical ML classifier combining radiological and pathological features for biochemical recurrence prediction after radical prostatectomy."
category: "multimodal-embedding"
tags:
    - clinical: [prostate-cancer]
    - data: [imaging, tabular]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Radiological features (MRI-derived) + pathological features (surgical pathology report) |
| File format | TODO: CSV feature tables |
| Required fields / tags | TODO: specify required feature columns for radiology and pathology inputs |
| Preprocessing required upstream | Prostate MRI lesion segmentation via Invisible Prostate Cancer Detection; radiomics feature extraction; pathology feature extraction |

Feature tables must not contain direct patient identifiers. Source images and pathology reports used for feature extraction must be de-identified upstream.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the ML algorithm(s) used (e.g., logistic regression, gradient boosting), the feature selection approach, and how radiology and pathology features are combined (early fusion, late fusion, or stacking).

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional prostate cancer cohort |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Add install command and list dependencies. Note scikit-learn / other ML library versions. Show the minimal command to run inference on new feature tables.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | BCR risk score or binary BCR prediction |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report AUROC and C-index for BCR prediction. Report comparison to pathology-only and imaging-only baselines.

Disaggregated performance analysis has not been conducted. This is a known limitation. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document the partial status — what is incomplete relative to the roadmap. Note sensitivity to feature extraction quality and known limitations of classical ML versus the planned DL-based ClaD/RadClip tools.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** Prostate cancer incidence, treatment patterns, and pathology differ by race (notably higher incidence and mortality in Black men). Describe training cohort demographics and performance variation by race and age.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** BCR is confounded by PSA threshold definitions and follow-up duration. Describe how these were standardized in the training cohort.
- **Data Governance**:
  > **TODO (POC: TBD):** Describe data DUA and consent model. BCR risk stratification must not inform treatment decisions (e.g., adjuvant radiation) without expert urologist and radiation oncologist review.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX if one exists.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Empathi
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
