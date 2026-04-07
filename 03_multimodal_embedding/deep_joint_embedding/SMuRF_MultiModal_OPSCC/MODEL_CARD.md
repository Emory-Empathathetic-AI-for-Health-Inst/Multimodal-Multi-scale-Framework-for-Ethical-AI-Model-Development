---
tool_name: SMuRF
lab: "Empathi"
poc: "TBD"
repo_path: "03_multimodal_embedding/deep_joint_embedding/SMuRF_MultiModal_OPSCC/"
short_description: "Swin Transformer co-attention fusion of radiology and pathology images for oropharyngeal squamous cell carcinoma (OPSCC) outcome prediction; EBioMedicine."
category: "multimodal-embedding"
tags:
    - clinical: [radiology, pathology]
    - data: [imaging]
last_updated: "2026-04-07"
publication: ""
package_url: ""
---

# Model Card: SMuRF

> **Status:** Implemented | **Type:** dl-model | **Lab:** Empathi | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/deep_joint_embedding/SMuRF_MultiModal_OPSCC/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on what clinical outcome SMuRF predicts for OPSCC (e.g., survival, recurrence, treatment response), how Swin Transformer co-attention fuses radiology and pathology modalities, and the clinical significance of the OPSCC prediction task.

SMuRF uses Swin Transformer-based co-attention to fuse radiology (CT/PET) and pathology (H&E slide) image modalities for oropharyngeal squamous cell carcinoma (OPSCC) outcome prediction. Published in EBioMedicine.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers and oncology researchers working on multimodal fusion for head and neck cancer outcome prediction.

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Radiology images (CT or PET) + pathology images (H&E slides) |
| File format | DICOM for radiology; PNG/TIFF for pathology tiles |
| Required fields / tags | TODO: specific DICOM sequences required; pathology tile resolution requirements |
| Preprocessing required upstream | TODO: describe radiology preprocessing (resampling, registration); pathology tile extraction (patch size, magnification) |

Both radiology DICOM files and pathology slide images must be de-identified before use. Pathology images may contain institutional metadata in file headers — verify de-identification.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the Swin Transformer backbone for each modality, the co-attention mechanism design, and how the dual-modality representations are fused for final outcome prediction.

| Field | Value |
|---|---|
| Dataset(s) | TODO — OPSCC patient cohort (institutional) |
| Dataset size | TODO |
| Data source type | TODO — institutional / multi-institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Reference the EBioMedicine paper for dataset description. Add install command and list key dependencies. Specify GPU memory requirements for inference. Show the minimal command for running inference on a paired radiology + pathology case.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | OPSCC outcome prediction (binary label or risk score) |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | Reference EBioMedicine paper for reported results |

> **TODO (POC: TBD):** Report AUROC, C-index (if survival), and comparison to unimodal baselines.

Disaggregated performance analysis has not been conducted within MEFINDER. Contact the POC for current status of demographic disaggregation analysis.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: performance when one modality is missing or of poor quality, pathology tile extraction sensitivity, generalizability to OPSCC cohorts with different HPV status distributions.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** Describe the demographic composition of the training cohort (sex, age, HPV status, race) and whether the model has been evaluated across subgroups.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Note confounders in the OPSCC training data (e.g., treatment era, institutional protocol differences, HPV status as a strong prognostic confounder) and how they were addressed.
- **Data Governance**:
  > **TODO (POC: TBD):** Describe training data DUA and whether model weights can be redistributed. This tool must not be used for clinical treatment decision-making without prospective validation and regulatory review.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add EBioMedicine publication BibTeX. Acknowledge Swin Transformer pretrained checkpoint and any upstream pathology tile extraction libraries used.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Empathi
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
