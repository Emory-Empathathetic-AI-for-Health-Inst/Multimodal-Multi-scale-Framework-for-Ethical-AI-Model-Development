---
tool_id: mammo-vlm-ss
tool_name: VLM for Mammogram (mammo_vlm_ss)
card_type: dl-model
status: Implemented
lab: [Mayo]
poc: "TBD"
repo_path: "03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/"
target_path: "03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/"
short_description: "ALBEF + MedCLIP vision-language model for mammography with mini-batch selective sampling for rare group equity; MICCAI 2024."
input_modality: [PNG, free-text]
output_type: [embeddings]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: [mammo-implant-detector]
used_by: []
---

# Model Card: VLM for Mammogram (mammo_vlm_ss)

> **Status:** Implemented | **Type:** dl-model | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on the ALBEF + MedCLIP architecture, how mini-batch selective sampling addresses rare subgroup underrepresentation, and what the produced embeddings are used for (retrieval, downstream classification, zero-shot tasks).

This tool adapts ALBEF and MedCLIP to mammography image-report pairs, producing cross-modal vision-language embeddings. Mini-batch selective sampling is used during training to ensure fair representation of rare demographic or clinical subgroups. Published at MICCAI 2024.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers working on mammography AI, multimodal learning, and equitable representation in medical image models. The embeddings produced are intended as inputs for downstream classification or retrieval tasks, not for direct clinical use.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Mammography images (2D) paired with radiology reports |
| File format | PNG images + free-text reports (CSV or similar) |
| Required fields / tags | Image-report pairs with shared patient/study identifier; implant-free mammograms (see upstream dependency) |
| Preprocessing required upstream | Implant detection via Mammography Implant Detector; implant-present images should be excluded or handled separately |

### 3.2 Anonymization and PHI Requirements

Input images must be de-identified. Reports must have all patient identifiers removed. DICOM-to-PNG conversion should strip header metadata; verify no burned-in PHI in images.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the ALBEF architecture (image encoder, text encoder, cross-attention), how MedCLIP pretraining weights are used, and the selective sampling strategy (how rare groups are defined and oversampled within mini-batches).

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional mammography image-report pairs |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Note whether VinDr-Mammo or other public datasets were used in addition to institutional data.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and list key dependencies (PyTorch version, transformers version, etc.). Link to requirements file.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to extract embeddings for a set of image-report pairs. Reference `extract_groups.ipynb` and `visualization.ipynb` for examples.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Vision-language embeddings |
| Output format | TODO — tensor file, numpy array, or CSV |
| Output location | Configurable output directory |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | Reference MICCAI 2024 paper for reported results |

> **TODO (POC: TBD):** Report retrieval metrics (Recall@K), linear probe classification accuracy, and any group-specific metrics demonstrating selective sampling benefit.

### 6.2 Disaggregated Performance

> **TODO (POC: TBD):** This tool was specifically designed to address rare subgroup underrepresentation via selective sampling. Report performance disaggregated by the demographic or clinical subgroups used in the sampling strategy. This is a core result of the MICCAI paper and should be documented here.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document limitations: performance on mammography views not well-represented in training (e.g., spot compression views), sensitivity to report writing style, limitations of the selective sampling approach when subgroup annotations are unavailable.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Describe the demographic composition of the training cohort, the subgroups targeted by selective sampling, and the evidence from MICCAI 2024 that selective sampling improves representation. Note any remaining gaps in subgroup coverage.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Note any site-specific imaging protocol confounders in the training data (e.g., mammography vendor effects, compression paddle type) that may affect embedding quality across institutions.

### 8.3 Clinical Deployment Safeguards

This tool produces embeddings for research retrieval and downstream tasks. It must not be used to generate clinical reports or support clinical decisions without prospective validation.

### 8.4 Data Governance

> **TODO (POC: TBD):** Describe training data ownership, DUA, and whether embeddings derived from institutional data can be shared.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`03_multimodal_embedding` — deep joint embedding of mammography images and radiology reports.

### 9.2 Upstream Dependencies

- [Mammography Implant Detector](../../../01_data_harmonization/radiology/mammo_implant_identifier/MODEL_CARD.md): implant-present mammograms should be excluded before embedding.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List MEFINDER use cases or tools that consume mammo_vlm_ss embeddings.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add MICCAI 2024 BibTeX entry. Acknowledge ALBEF and MedCLIP upstream codebases and pretrained weights.

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Mayo |
| Contact | See PROJECT_CONTACTS.md |
| Status | Implemented |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
