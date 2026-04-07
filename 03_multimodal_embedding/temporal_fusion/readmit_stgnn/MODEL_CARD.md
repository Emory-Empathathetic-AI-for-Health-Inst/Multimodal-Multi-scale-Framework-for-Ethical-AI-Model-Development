---
tool_name: Graph-based Multimodal Modeling (MM-STGNN)
lab: "Mayo"
poc: "TBD"
repo_path: "03_multimodal_embedding/temporal_fusion/readmit_stgnn/"
short_description: "Multimodal spatiotemporal graph neural network fusing longitudinal CXR and EHR for 30-day hospital readmission prediction; IEEE JBHI 2023."
category: "multimodal-embedding"
tags:
    - clinical: [radiology]
    - data: [imaging, tabular]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Longitudinal chest X-ray images + structured EHR features |
| File format | PNG (CXR), tabular EHR features (CSV) |
| Required fields / tags | TODO: required EHR feature columns and temporal indexing; CXR temporal alignment with EHR timestamps |
| Preprocessing required upstream | CXR de-identification; EHR feature extraction and normalization |

CXR images must be de-identified. EHR data must be processed to remove direct identifiers. MIMIC data requires completion of PhysioNet DUA; see Section 8.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the patient graph construction (node and edge definitions), the spatiotemporal GNN architecture (e.g., DGL-based, temporal attention), the CXR image encoder, and how image and EHR representations are fused.

| Field | Value |
|---|---|
| Dataset(s) | MIMIC-IV (EHR) + MIMIC-CXR-JPG (chest X-rays) |
| Dataset size | TODO: number of patients/admissions used |
| Data source type | Public (PhysioNet) |
| Data use agreement | PhysioNet Data Use Agreement — completion required before accessing MIMIC data |

> **TODO (POC: TBD):** Confirm exact MIMIC version and cohort selection criteria. Add data split sizes (train/val/test). Add install command. Note DGL (Deep Graph Library) version requirement and GPU memory requirements. Show the minimal command to run inference and reference `train.py`, `gnn_explainer.py` for training and explanation.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | 30-day readmission risk score |
| Output format | TODO — scalar probability or binary label |
| Output location | TODO |

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| AUROC | TODO | MIMIC test set | Reference JBHI 2023 paper |
| F1 | TODO | MIMIC test set | |

> **TODO (POC: TBD):** Report AUROC, AUPRC, F1, and comparison to unimodal (CXR-only, EHR-only) baselines. Reference IEEE JBHI 2023 paper for full results.

> **TODO (POC: TBD):** MIMIC-IV includes demographic variables (sex, age, race/ethnicity, insurance type as a proxy for socioeconomic status). Report 30-day readmission prediction performance disaggregated by these variables. If not yet computed, state explicitly with a plan and timeline.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: reliance on temporal completeness of CXR and EHR records, performance degradation for patients with few longitudinal visits, sensitivity to EHR feature availability across institutions, and known performance gaps for specific demographic subgroups.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** MIMIC-IV over-represents certain patient populations (e.g., patients at a single academic medical center in Boston). Describe demographic distribution of the training cohort, known performance disparities, and any fairness-aware training techniques applied.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Readmission is strongly confounded by socioeconomic factors, discharge planning quality, and home support — all factors not captured in imaging or standard EHR features. Describe how these confounders were addressed or acknowledged.
- **Data Governance**:
  Training data: MIMIC-IV and MIMIC-CXR-JPG, both available via PhysioNet under the PhysioNet Data Use Agreement. Researchers must individually complete the PhysioNet DUA and complete the CITI "Data or Specimens Only Research" training before accessing MIMIC data. Readmission prediction models must not gate resource allocation or discharge decisions without human clinical review.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add IEEE JBHI 2023 BibTeX. Acknowledge MIMIC-IV and MIMIC-CXR-JPG datasets. Acknowledge DGL framework.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Mayo
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
