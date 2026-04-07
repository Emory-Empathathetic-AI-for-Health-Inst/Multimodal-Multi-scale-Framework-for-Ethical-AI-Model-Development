---
tool_id: prostate-lesion-detection
tool_name: Invisible Prostate Cancer Detection
card_type: dl-model
status: Implemented
lab: [Empathi]
poc: "TBD"
repo_path: "02_feature_extraction/deep_features/prostate_lesion_detection/"
target_path: "02_feature_extraction/deep_features/prostate_lesion_detection/"
short_description: "nnU-Net lesion detection and segmentation on prostate MRI; trained on PI-CAI and Prostate-158 datasets."
input_modality: [NIfTI]
output_type: [segmentation-mask]
clinical_domain: [prostate-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: [prostate-shape-distension, rad-path-prostate-classifier]
---

# Model Card: Invisible Prostate Cancer Detection

> **Status:** Implemented | **Type:** dl-model | **Lab:** Empathi | **POC:** TBD
>
> **Repo path:** `02_feature_extraction/deep_features/prostate_lesion_detection/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on the "invisible" lesion detection challenge (clinically significant lesions not visible to radiologists on standard sequences), the nnU-Net configuration used, and how the segmentation output feeds into downstream prostate analysis tools.

This tool applies nnU-Net for automated detection and segmentation of prostate cancer lesions on multiparametric MRI, with a focus on lesions that may be missed by radiologists. It was trained on the publicly available PI-CAI and Prostate-158 datasets.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers and computational pathology researchers working on prostate cancer risk stratification. Segmentation masks produced by this tool are intended as inputs to downstream MEFINDER tools (shape biomarkers, radiomics).

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Multiparametric prostate MRI (T2W, DWI, DCE) |
| File format | NIfTI (`.nii.gz`) |
| Required fields / tags | TODO: required MRI sequences and spatial resolution expectations |
| Preprocessing required upstream | TODO: state required preprocessing (e.g., resampling, N4 bias correction, normalization) |

### 3.2 Anonymization and PHI Requirements

Input NIfTI files must be de-identified. NIfTI files typically do not contain embedded PHI, but any associated metadata files should be verified before use.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

nnU-Net framework for self-configuring medical image segmentation. Architecture parameters (patch size, pooling, encoder depth) are automatically configured by nnU-Net based on dataset properties.

> **TODO (POC: TBD):** Specify the nnU-Net configuration used (2D, 3D full-res, 3D low-res, ensemble), the input modality combination, and any custom modifications made to the nnU-Net pipeline.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | PI-CAI (Prostate Imaging: Cancer AI), Prostate-158 |
| Dataset size | PI-CAI: 1,500 cases; Prostate-158: 158 cases |
| Data source type | Public |
| Data use agreement | PI-CAI challenge data use agreement; Prostate-158 CC-BY license |

> **TODO (POC: TBD):** Confirm exact dataset splits (training/validation/test), whether additional institutional data was included, and where model weights are hosted.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add nnU-Net install command and version. Specify GPU memory requirements.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the nnU-Net inference command for running segmentation on a new case. Point to any wrapper scripts in this directory.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Binary or multi-class lesion segmentation mask |
| Output format | NIfTI (`.nii.gz`) |
| Output location | nnU-Net default output directory (configurable) |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| Dice score | TODO | PI-CAI test set | |
| AUROC (lesion detection) | TODO | PI-CAI test set | |

> **TODO (POC: TBD):** Report Dice score, sensitivity, specificity, and AUROC on the official PI-CAI challenge test set. Reference challenge leaderboard if results were submitted.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted within MEFINDER. The PI-CAI dataset includes cases from multiple European institutions; scanner/site-level performance may vary. Contact the POC for current status of demographic disaggregation analysis.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: lesion size thresholds below which detection fails, sensitivity to MRI acquisition protocol (e.g., field strength, slice thickness), performance on non-European patient populations, and known failure modes for specific Gleason grades.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** PI-CAI and Prostate-158 are predominantly European institutional datasets. Describe whether the model has been tested on more diverse populations, and what is known about performance variation by patient demographics.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** MRI acquisition protocols differ across institutions and scanner manufacturers. Describe any known protocol-dependent performance variation and whether domain adaptation was applied.

### 8.3 Clinical Deployment Safeguards

This tool should NOT be used to guide clinical biopsy decisions without radiologist review. Segmentation masks are inputs for downstream research tools, not clinical reports. Any clinical translation requires prospective validation under IRB oversight.

### 8.4 Data Governance

Training data is publicly available under PI-CAI challenge terms and Prostate-158 CC-BY license. Model weights availability: see POC. If weights are derived from challenge-restricted data, redistribution may require challenge organizer approval.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`02_feature_extraction` — produces lesion segmentation masks used as inputs for downstream prostate analysis tools.

### 9.2 Upstream Dependencies

None at the MEFINDER level — takes MRI volumes directly. Preprocessing (resampling, normalization) may be required; see Section 3.1.

### 9.3 Downstream Consumers

- [Prostate Shape Distension](../../../model_cards/stubs/prostate-shape-distension.md): consumes segmentation masks to derive 3D shape biomarkers (planned).
- [Rad-Path Prostate Recurrence Classifier](../../../03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/MODEL_CARD.md): uses imaging features derived from prostate lesion regions.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add nnU-Net citation and PI-CAI / Prostate-158 dataset citations. Add any MEFINDER-associated publication.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Empathi |
| Contact | See PROJECT_CONTACTS.md |
| Status | Implemented |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
