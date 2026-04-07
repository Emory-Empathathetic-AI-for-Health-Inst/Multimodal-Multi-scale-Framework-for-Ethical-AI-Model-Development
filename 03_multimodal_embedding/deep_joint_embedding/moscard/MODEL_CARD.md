---
tool_id: moscard
tool_name: MOSCARD (Computational Debiasing)
card_type: dl-model
status: Partial
lab: [Mayo]
poc: "TBD"
repo_path: "03_multimodal_embedding/deep_joint_embedding/moscard/"
target_path: "03_multimodal_embedding/deep_joint_embedding/moscard/"
short_description: "CXR + ECG causal fusion model with structural causal models for debiased cardiology outcome prediction; debiasing logic embedded in model (not yet standalone)."
input_modality: [PNG, ECG, CSV]
output_type: [labels]
clinical_domain: [cardiology]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
---

# Model Card: MOSCARD (Computational Debiasing)

> **Status:** Partial | **Type:** dl-model | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `03_multimodal_embedding/deep_joint_embedding/moscard/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences on what clinical outcome MOSCARD predicts (e.g., mortality, cardiac event), how structural causal models are integrated into the fusion architecture for debiasing, and what "debiasing" means in this clinical context (e.g., correcting for confounders such as BMI, age, or site-specific acquisition differences).

MOSCARD fuses chest X-ray (CXR) images with ECG signals for cardiology outcome prediction. It integrates structural causal models (SCMs) to actively debias predictions against known confounders. **The causal/deconfounding logic is currently embedded in the model architecture and has not been extracted as a standalone reusable toolkit.** See `model_cards/stubs/computational-debiasing-toolkit.md` for the planned extraction.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers working on multimodal cardiology AI and causal debiasing methods. This tool is currently in partial status; consult the POC before integrating into any research pipeline.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Chest X-ray images + ECG signals + tabular clinical features |
| File format | PNG (CXR), ECG signal format (TODO: specify), CSV (tabular features) |
| Required fields / tags | TODO: specify required CXR view (PA/AP/lateral), ECG lead configuration, and CSV column schema |
| Preprocessing required upstream | ECG conversion (see `ecg_convert_example.ipynb`); CXR de-identification |

### 3.2 Anonymization and PHI Requirements

CXR images must be de-identified. ECG recordings may contain embedded patient metadata — verify de-identification before use.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the image encoder (e.g., DenseNet, ResNet) for CXR, the ECG encoder, and how SCM-based deconfounding is integrated — e.g., whether a confusion loss, adversarial training, or do-calculus intervention is used. Reference the structural causal model graph if documented.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — MIMIC-CXR and MIMIC-IV-ECG (PhysioNet) suspected; confirm with POC |
| Dataset size | TODO |
| Data source type | Public (PhysioNet) / institutional |
| Data use agreement | PhysioNet Data Use Agreement required for MIMIC data |

> **TODO (POC: TBD):** Confirm datasets and DUAs. Note whether MIMIC PhysioNet DUA is required to reproduce results.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and link to requirements file. Reference `ecg_convert_example.ipynb` for ECG preprocessing setup.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show minimal commands for single-modality (CXR only, ECG only) and multi-modality inference. Reference the `train_CXR.py`, `train_ECG.py`, and `train.py` scripts.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Outcome prediction (binary label or risk score) |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report AUROC for single-modality and multimodal configurations. Report debiasing effectiveness (e.g., reduction in performance disparity across demographic groups).

### 6.2 Disaggregated Performance

> **TODO (POC: TBD):** MOSCARD's causal debiasing design makes disaggregated performance reporting especially important. Report performance disaggregated by sex, age group, race/ethnicity, and any confounders explicitly modeled in the SCM. If not yet computed, state so explicitly and provide a timeline.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document the partial status of the tool — specifically what is incomplete. Note any known limitations of the SCM debiasing approach (e.g., requires pre-specification of the causal graph, sensitive to unobserved confounders).

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** MOSCARD was designed specifically to address bias. Describe what biases it targets, the mechanism (SCM-based), and empirical evidence of bias reduction. Note any biases that remain unaddressed.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Describe the causal graph assumed by the SCM, the confounders explicitly modeled, and the risk of unmodeled confounders. The SCM approach requires correct causal graph specification — note the consequences of misspecification.

### 8.3 Clinical Deployment Safeguards

This tool must not be used for clinical cardiology decision-making. Debiasing effectiveness has not been validated prospectively. Clinical translation requires rigorous external validation across diverse institutions.

### 8.4 Data Governance

> **TODO (POC: TBD):** Confirm whether MIMIC data (PhysioNet DUA) was used. Note any institutional data included and associated governance.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`03_multimodal_embedding` — causal multimodal fusion for cardiology outcome prediction.

### 9.2 Upstream Dependencies

None at the MEFINDER level — takes CXR images and ECG recordings directly.

### 9.3 Downstream Consumers

The causal debiasing logic embedded in this model is intended to be extracted into a standalone toolkit: [Computational Debiasing Toolkit](../../../model_cards/stubs/computational-debiasing-toolkit.md) (planned — not yet implemented).

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX. Acknowledge any upstream model checkpoints (MoCo-CXR, etc.).

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | TBD — see PROJECT_CONTACTS.md |
| Lab | Mayo |
| Contact | See PROJECT_CONTACTS.md |
| Status | Partial — standalone debiasing toolkit not yet extracted |
| Card last reviewed | 2026-04-07 |

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../../../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
