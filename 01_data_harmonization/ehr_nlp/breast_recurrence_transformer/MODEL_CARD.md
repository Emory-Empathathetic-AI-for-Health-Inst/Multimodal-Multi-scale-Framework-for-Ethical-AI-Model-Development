---
tool_id: breast-recurrence-transformer
tool_name: Breast Recurrence Transformer
card_type: nlp-pipeline
status: Implemented
lab: [Mayo]
poc: "TBD"
repo_path: "01_data_harmonization/ehr_nlp/breast_recurrence_transformer/"
target_path: "01_data_harmonization/ehr_nlp/breast_recurrence_transformer/"
short_description: "BERT-based NLP pipeline that identifies breast cancer recurrence occurrence and timing from clinical notes."
input_modality: [XLSX]
output_type: [CSV]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: [recurrence-site-extraction]
---

# Model Card: Breast Recurrence Transformer

> **Status:** Implemented | **Type:** nlp-pipeline | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/ehr_nlp/breast_recurrence_transformer/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences describing the BERT-based architecture, how it was fine-tuned on breast oncology notes, and what clinical question it answers (recurrence yes/no, recurrence date). Note that its output CSV is a required input for the downstream Recurrence Site Extraction tool.

This BERT-based NLP pipeline identifies whether breast cancer recurrence occurred in a patient's clinical notes and extracts the timing of recurrence. Its output is a required upstream input for the Recurrence Site Extraction tool.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: Clinical informatics researchers and data scientists building breast cancer recurrence cohorts from retrospective EHR data. This tool is intended for retrospective cohort construction, not real-time clinical surveillance.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Free-text clinical notes |
| File format | `.xlsx` |
| Required fields / tags | `ANON_ID`, `NOTE_TYPE`, `NOTE_DATE`, `NOTE` (column names must match exactly) |
| Preprocessing required upstream | Notes must be de-identified; ANON_ID must be a non-PHI patient identifier |

### 3.2 Anonymization and PHI Requirements

Input clinical notes must be de-identified before use. This tool does not perform PHI removal. The `ANON_ID` column must contain a pseudonymized identifier with no direct PHI linkage.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the BERT variant used (e.g., BioBERT, ClinicalBERT), the fine-tuning setup (classification head architecture, training objective), and any rule-based post-processing applied to the model output.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional Mayo Clinic breast oncology notes |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. State explicitly if training data cannot be released and provide a contact for reproducibility inquiries.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and link to requirements file.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to run the pipeline on an input `.xlsx` file.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Per-patient recurrence labels and dates |
| Output format | `.csv` |
| Output location | TODO |

Output CSV columns: `PATIENT_ID`, `START_DATE`, `END_DATE`, `text`, `Prediction`

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report F1 score, precision, recall, and AUROC on the held-out test set. Include performance on recurrence date extraction if evaluated separately.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis requires demographic metadata (age, race, stage) for the evaluation cohort. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations such as note types where performance degrades (e.g., short nursing notes vs. detailed oncology notes), temporal scope assumptions, handling of ambiguous recurrence language, and performance on notes from institutions other than Mayo.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Describe the demographic composition of the training cohort and whether the model has been tested on notes from diverse patient populations. Note any known disparities in performance by age, race, or cancer subtype.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Note any known confounders in the training data (e.g., institutional documentation practices, note templates that may include boilerplate recurrence language) that could affect generalizability.

### 8.3 Clinical Deployment Safeguards

This tool should NOT be used for real-time clinical surveillance or to make clinical decisions without human expert review. Intended for retrospective research cohort construction only.

### 8.4 Data Governance

Training data consists of institutional Mayo Clinic clinical notes. Training data is not publicly released. Any use of this tool on new institutional data requires a local IRB review.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — EHR NLP layer producing structured recurrence labels from clinical notes.

### 9.2 Upstream Dependencies

None — this tool operates on raw (de-identified) clinical notes.

### 9.3 Downstream Consumers

- [Recurrence Site Extraction](../recurrence_site_extraction/MODEL_CARD.md): requires the `Prediction` output CSV from this tool as its primary input. **Do not run Recurrence Site Extraction on raw notes directly.**

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add the associated publication BibTeX. Acknowledge the base BERT model checkpoint used for fine-tuning.

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
