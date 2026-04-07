---
tool_name: MOSCARD (Computational Debiasing)
lab: "Mayo"
poc: "TBD"
repo_path: "03_multimodal_embedding/deep_joint_embedding/moscard/"
short_description: "CXR + ECG causal fusion model with structural causal models for debiased cardiology outcome prediction; debiasing logic embedded in model (not yet standalone)."
category: "multimodal-embedding"
tags:
    - clinical: [cardiology]
    - data: [imaging, tabular]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Chest X-ray images + ECG signals + tabular clinical features |
| File format | PNG (CXR), ECG signal format (TODO: specify), CSV (tabular features) |
| Required fields / tags | TODO: specify required CXR view (PA/AP/lateral), ECG lead configuration, and CSV column schema |
| Preprocessing required upstream | ECG conversion (see `ecg_convert_example.ipynb`); CXR de-identification |

CXR images must be de-identified. ECG recordings may contain embedded patient metadata — verify de-identification before use.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the image encoder (e.g., DenseNet, ResNet) for CXR, the ECG encoder, and how SCM-based deconfounding is integrated — e.g., whether a confusion loss, adversarial training, or do-calculus intervention is used. Reference the structural causal model graph if documented.

| Field | Value |
|---|---|
| Dataset(s) | TODO — MIMIC-CXR and MIMIC-IV-ECG (PhysioNet) suspected; confirm with POC |
| Dataset size | TODO |
| Data source type | Public (PhysioNet) / institutional |
| Data use agreement | PhysioNet Data Use Agreement required for MIMIC data |

> **TODO (POC: TBD):** Confirm datasets and DUAs. Note whether MIMIC PhysioNet DUA is required to reproduce results. Add install command and link to requirements file. Reference `ecg_convert_example.ipynb` for ECG preprocessing setup. Show minimal commands for single-modality and multi-modality inference. Reference the `train_CXR.py`, `train_ECG.py`, and `train.py` scripts.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Outcome prediction (binary label or risk score) |
| Output format | TODO |
| Output location | TODO |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report AUROC for single-modality and multimodal configurations. Report debiasing effectiveness (e.g., reduction in performance disparity across demographic groups).

> **TODO (POC: TBD):** MOSCARD's causal debiasing design makes disaggregated performance reporting especially important. Report performance disaggregated by sex, age group, race/ethnicity, and any confounders explicitly modeled in the SCM. If not yet computed, state so explicitly and provide a timeline.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document the partial status of the tool — specifically what is incomplete. Note any known limitations of the SCM debiasing approach (e.g., requires pre-specification of the causal graph, sensitive to unobserved confounders).

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** MOSCARD was designed specifically to address bias. Describe what biases it targets, the mechanism (SCM-based), and empirical evidence of bias reduction. Note any biases that remain unaddressed.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Describe the causal graph assumed by the SCM, the confounders explicitly modeled, and the risk of unmodeled confounders. The SCM approach requires correct causal graph specification — note the consequences of misspecification.
- **Data Governance**:
  > **TODO (POC: TBD):** Confirm whether MIMIC data (PhysioNet DUA) was used. Note any institutional data included and associated governance. Debiasing effectiveness has not been validated prospectively; clinical translation requires rigorous external validation across diverse institutions.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX. Acknowledge any upstream model checkpoints (MoCo-CXR, etc.).

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Mayo
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
