---
tool_name: Invisible Prostate Cancer Detection
lab: "Empathi"
poc: "TBD"
repo_path: "02_feature_extraction/deep_features/prostate_lesion_detection/"
short_description: "nnU-Net lesion detection and segmentation on prostate MRI; trained on PI-CAI and Prostate-158 datasets."
category: "feature-extraction"
tags:
    - clinical: [prostate-cancer]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Multiparametric prostate MRI (T2W, DWI, DCE) |
| File format | NIfTI (`.nii.gz`) |
| Required fields / tags | TODO: required MRI sequences and spatial resolution expectations |
| Preprocessing required upstream | TODO: state required preprocessing (e.g., resampling, N4 bias correction, normalization) |

Input NIfTI files must be de-identified. NIfTI files typically do not contain embedded PHI, but any associated metadata files should be verified before use.

## 4. Technical Specifications

nnU-Net framework for self-configuring medical image segmentation. Architecture parameters (patch size, pooling, encoder depth) are automatically configured by nnU-Net based on dataset properties.

> **TODO (POC: TBD):** Specify the nnU-Net configuration used (2D, 3D full-res, 3D low-res, ensemble), the input modality combination, and any custom modifications made to the nnU-Net pipeline.

| Field | Value |
|---|---|
| Dataset(s) | PI-CAI (Prostate Imaging: Cancer AI), Prostate-158 |
| Dataset size | PI-CAI: 1,500 cases; Prostate-158: 158 cases |
| Data source type | Public |
| Data use agreement | PI-CAI challenge data use agreement; Prostate-158 CC-BY license |

> **TODO (POC: TBD):** Confirm exact dataset splits (training/validation/test), whether additional institutional data was included, and where model weights are hosted. Add nnU-Net install command and version. Specify GPU memory requirements. Show the nnU-Net inference command for running segmentation on a new case.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Binary or multi-class lesion segmentation mask |
| Output format | NIfTI (`.nii.gz`) |
| Output location | nnU-Net default output directory (configurable) |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| Dice score | TODO | PI-CAI test set | |
| AUROC (lesion detection) | TODO | PI-CAI test set | |

> **TODO (POC: TBD):** Report Dice score, sensitivity, specificity, and AUROC on the official PI-CAI challenge test set. Reference challenge leaderboard if results were submitted.

Disaggregated performance analysis has not been conducted within MEFINDER. The PI-CAI dataset includes cases from multiple European institutions; scanner/site-level performance may vary. Contact the POC for current status of demographic disaggregation analysis.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: lesion size thresholds below which detection fails, sensitivity to MRI acquisition protocol (e.g., field strength, slice thickness), performance on non-European patient populations, and known failure modes for specific Gleason grades.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** PI-CAI and Prostate-158 are predominantly European institutional datasets. Describe whether the model has been tested on more diverse populations, and what is known about performance variation by patient demographics.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** MRI acquisition protocols differ across institutions and scanner manufacturers. Describe any known protocol-dependent performance variation and whether domain adaptation was applied.
- **Data Governance**:
  Training data is publicly available under PI-CAI challenge terms and Prostate-158 CC-BY license. Model weights availability: see POC. If weights are derived from challenge-restricted data, redistribution may require challenge organizer approval. This tool should NOT be used to guide clinical biopsy decisions without radiologist review; any clinical translation requires prospective validation under IRB oversight.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add nnU-Net citation and PI-CAI / Prostate-158 dataset citations. Add any MEFINDER-associated publication.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Empathi
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
