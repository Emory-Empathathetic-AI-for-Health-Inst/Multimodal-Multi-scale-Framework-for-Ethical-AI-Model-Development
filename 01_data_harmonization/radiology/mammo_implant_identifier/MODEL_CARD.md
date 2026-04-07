---
tool_id: mammo-implant-detector
tool_name: Mammography Implant Detector
card_type: dl-model
status: Implemented
lab: [HITI]
poc: "Beatrice Brown-Mulry"
repo_path: "01_data_harmonization/radiology/mammo_implant_identifier/"
target_path: "01_data_harmonization/radiology/mammo_implant_identifier/"
short_description: "ResNet-18 binary classifier that identifies breast implant presence in mammograms; preprocessing gate for the mammography pipeline."
input_modality: [PNG]
output_type: [labels]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: [mammo-vlm-ss]
---

# Model Card: Mammography Implant Detector

> **Status:** Implemented | **Type:** dl-model | **Lab:** HITI | **POC:** Beatrice Brown-Mulry
>
> **Repo path:** `01_data_harmonization/radiology/mammo_implant_identifier/`

---

## 1. Purpose and Scope

> **TODO (POC: Beatrice Brown-Mulry):** Expand with 2–4 sentences describing how the ResNet-18 classifier was adapted for implant detection, the clinical motivation (implants significantly affect image processing pipelines and must be flagged before downstream VLM or radiomics analysis), and its role as a preprocessing gate in the MEFINDER mammography pipeline.

This tool classifies mammograms as implant-present or implant-absent using a pre-trained ResNet-18 model. It serves as a preprocessing gate before downstream mammography tools (e.g., mammo_vlm_ss) to prevent implant artifacts from corrupting model inputs.

**Note:** This directory contains no README. This MODEL_CARD.md serves as the primary documentation for this tool. See `inference.ipynb` for usage.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers and data engineers preparing mammography datasets for downstream MEFINDER tools. This classifier is intended to flag mammograms with implants so they can be excluded or handled separately by downstream models.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Mammography (2D) |
| File format | PNG images |
| Required fields / tags | Standard 2D mammogram image; implant regions must be visible in the image field |
| Preprocessing required upstream | DICOM-to-PNG conversion (e.g., via Niffler or HITI-Preproc); de-identification |

### 3.2 Anonymization and PHI Requirements

Input images must be de-identified before use. DICOM-to-PNG conversion typically strips most DICOM header metadata; verify that no PHI is embedded in image pixels (e.g., burned-in annotations) before running this tool.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

ResNet-18 binary classifier fine-tuned for breast implant presence detection in mammograms. Pre-trained weights are stored in `optimized_resnet18_implant_class.pth`.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — training dataset not documented in this repository |
| Dataset size | TODO |
| Data source type | TODO — institutional / public / mixed |
| Data use agreement | TODO |

> **TODO (POC: Beatrice Brown-Mulry):** Document the training dataset. If training details are not available in this repository, state that explicitly and provide a contact for inquiries.

### 4.3 Installation and Dependencies

> **TODO (POC: Beatrice Brown-Mulry):** List Python dependencies (PyTorch version, torchvision, etc.) and how to set up the environment. Reference `inference.ipynb` for a self-contained example.

### 4.4 Inference / Usage

See `inference.ipynb` for a complete inference walkthrough.

> **TODO (POC: Beatrice Brown-Mulry):** Add a minimal code snippet showing how to load the `.pth` weights and run inference on a single PNG image.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Binary label (implant present / absent) |
| Output format | TODO — scalar prediction, probability score, or class label |
| Output location | TODO |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: Beatrice Brown-Mulry):** Report classification performance (accuracy, AUROC, sensitivity, specificity) on the test set used during development.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis is planned but requires demographic metadata for the training/test cohort. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: Beatrice Brown-Mulry):** Document known failure modes such as performance on specific mammography views (CC vs. MLO), unusual implant types, or images with burned-in text. Note that training data provenance is not documented in this repository.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: Beatrice Brown-Mulry):** Describe what demographic data was available during training, whether the training cohort reflects diverse patient populations, and any known or suspected sources of bias in implant detection performance across demographic groups.

### 8.2 Confounding and Causal Risks

> **TODO (POC: Beatrice Brown-Mulry):** Note any known confounders in the training data (e.g., site-specific acquisition protocols, mammography vendor effects) and how they may affect generalizability.

### 8.3 Clinical Deployment Safeguards

This tool should NOT be used alone for clinical decision-making. It is a preprocessing classifier whose output gates downstream tools. Human review should confirm implant status before excluding patients from any clinical analysis.

### 8.4 Data Governance

> **TODO (POC: Beatrice Brown-Mulry):** Describe the data use agreement and consent model for the training data. State whether the pre-trained weights can be redistributed.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — preprocessing gate applied before downstream mammography models.

### 9.2 Upstream Dependencies

Requires mammograms converted to PNG format, typically produced by [Niffler](../Niffler/MODEL_CARD.md) or [HITI-Preproc](../HITI-Preproc/MODEL_CARD.md).

### 9.3 Downstream Consumers

- [VLM for Mammogram (mammo_vlm_ss)](../../../03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/MODEL_CARD.md): implant detection output used to gate which mammograms enter the VLM pipeline.

## 10. Citation and Attribution

> **TODO (POC: Beatrice Brown-Mulry):** Add associated publication citation if one exists. Acknowledge the ResNet-18 pretrained backbone (ImageNet).

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | Beatrice Brown-Mulry |
| Lab | HITI |
| Contact | See PROJECT_CONTACTS.md |
| Status | Implemented |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
