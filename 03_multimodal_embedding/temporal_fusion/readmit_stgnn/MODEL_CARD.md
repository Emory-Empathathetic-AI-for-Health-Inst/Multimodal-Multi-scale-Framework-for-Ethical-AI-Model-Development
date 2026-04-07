---
tool_id: readmit-stgnn
tool_name: Graph-based Multimodal Modeling (MM-STGNN)
card_type: dl-model
status: Implemented
lab: [Mayo]
poc: "TBD"
repo_path: "03_multimodal_embedding/temporal_fusion/readmit_stgnn/"
target_path: "03_multimodal_embedding/temporal_fusion/readmit_stgnn/"
short_description: "Multimodal spatiotemporal graph neural network fusing longitudinal CXR and EHR for 30-day hospital readmission prediction; IEEE JBHI 2023."
input_modality: [PNG, EHR]
output_type: [labels]
clinical_domain: [general-radiology]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
---

# Model Card: Graph-based Multimodal Modeling (MM-STGNN)

> **Status:** Implemented | **Type:** dl-model | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/temporal_fusion/readmit_stgnn/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on the spatiotemporal graph construction (how patients and visits are represented as graph nodes/edges), the multimodal fusion of longitudinal CXR and EHR data, and the clinical significance of 30-day readmission prediction as a quality-of-care metric.

MM-STGNN fuses longitudinal chest X-ray images and structured EHR data via a multimodal spatiotemporal graph neural network to predict 30-day hospital readmission. Published in IEEE Journal of Biomedical and Health Informatics (JBHI) 2023.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers working on temporal multimodal clinical prediction and graph-based learning for EHR data. The readmission prediction output is intended for research evaluation, not real-time clinical triage.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Longitudinal chest X-ray images + structured EHR features |
| File format | PNG (CXR), tabular EHR features (CSV) |
| Required fields / tags | TODO: required EHR feature columns and temporal indexing; CXR temporal alignment with EHR timestamps |
| Preprocessing required upstream | CXR de-identification; EHR feature extraction and normalization |

### 3.2 Anonymization and PHI Requirements

CXR images must be de-identified. EHR data must be processed to remove direct identifiers. MIMIC data requires completion of PhysioNet DUA; see Section 8.4.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the patient graph construction (node and edge definitions), the spatiotemporal GNN architecture (e.g., DGL-based, temporal attention), the CXR image encoder, and how image and EHR representations are fused.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | MIMIC-IV (EHR) + MIMIC-CXR-JPG (chest X-rays) |
| Dataset size | TODO: number of patients/admissions used |
| Data source type | Public (PhysioNet) |
| Data use agreement | PhysioNet Data Use Agreement — completion required before accessing MIMIC data |

> **TODO (POC: TBD):** Confirm exact MIMIC version and cohort selection criteria. Add data split sizes (train/val/test).

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command. Note DGL (Deep Graph Library) version requirement and GPU memory requirements.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to run inference and reference `train.py`, `gnn_explainer.py` for training and explanation.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | 30-day readmission risk score |
| Output format | TODO — scalar probability or binary label |
| Output location | TODO |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| AUROC | TODO | MIMIC test set | Reference JBHI 2023 paper |
| F1 | TODO | MIMIC test set | |

> **TODO (POC: TBD):** Report AUROC, AUPRC, F1, and comparison to unimodal (CXR-only, EHR-only) baselines. Reference IEEE JBHI 2023 paper for full results.

### 6.2 Disaggregated Performance

> **TODO (POC: TBD):** MIMIC-IV includes demographic variables (sex, age, race/ethnicity, insurance type as a proxy for socioeconomic status). Report 30-day readmission prediction performance disaggregated by these variables. If not yet computed, state explicitly with a plan and timeline.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: reliance on temporal completeness of CXR and EHR records, performance degradation for patients with few longitudinal visits, sensitivity to EHR feature availability across institutions, and known performance gaps for specific demographic subgroups.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** MIMIC-IV over-represents certain patient populations (e.g., patients at a single academic medical center in Boston). Describe demographic distribution of the training cohort, known performance disparities, and any fairness-aware training techniques applied.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Readmission is strongly confounded by socioeconomic factors, discharge planning quality, and home support — all factors not captured in imaging or standard EHR features. Describe how these confounders were addressed or acknowledged.

### 8.3 Clinical Deployment Safeguards

Readmission prediction models must not gate resource allocation or discharge decisions without human clinical review. Deployment in clinical settings requires prospective validation and adherence to local regulatory requirements.

### 8.4 Data Governance

Training data: MIMIC-IV and MIMIC-CXR-JPG, both available via PhysioNet under the PhysioNet Data Use Agreement. Researchers must individually complete the PhysioNet DUA and complete the CITI "Data or Specimens Only Research" training before accessing MIMIC data.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`03_multimodal_embedding` — temporal fusion of longitudinal imaging and EHR for clinical outcome prediction.

### 9.2 Upstream Dependencies

None at the MEFINDER level — takes MIMIC-derived CXR and EHR data directly.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List any MEFINDER use cases or evaluation tools that consume MM-STGNN predictions.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add IEEE JBHI 2023 BibTeX. Acknowledge MIMIC-IV and MIMIC-CXR-JPG datasets. Acknowledge DGL framework.

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
