---
tool_name: Breast Recurrence Transformer
lab: "Mayo"
poc: "TBD"
repo_path: "01_data_harmonization/ehr_nlp/breast_recurrence_transformer/"
short_description: "BERT-based NLP pipeline that identifies breast cancer recurrence occurrence and timing from clinical notes."
category: "data-harmonization"
tags:
    - clinical: [breast-cancer]
    - data: [free-text]
last_updated: "2026-04-07"
publication: ""
package_url: ""
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

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Free-text clinical notes |
| File format | `.xlsx` |
| Required fields / tags | `ANON_ID`, `NOTE_TYPE`, `NOTE_DATE`, `NOTE` (column names must match exactly) |
| Preprocessing required upstream | Notes must be de-identified; ANON_ID must be a non-PHI patient identifier |

Input clinical notes must be de-identified before use. This tool does not perform PHI removal. The `ANON_ID` column must contain a pseudonymized identifier with no direct PHI linkage.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the BERT variant used (e.g., BioBERT, ClinicalBERT), the fine-tuning setup (classification head architecture, training objective), and any rule-based post-processing applied to the model output.

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional Mayo Clinic breast oncology notes |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. State explicitly if training data cannot be released and provide a contact for reproducibility inquiries. Add install command and link to requirements file. Show the minimal command to run the pipeline on an input `.xlsx` file.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Per-patient recurrence labels and dates |
| Output format | `.csv` |
| Output location | TODO |

Output CSV columns: `PATIENT_ID`, `START_DATE`, `END_DATE`, `text`, `Prediction`

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report F1 score, precision, recall, and AUROC on the held-out test set. Include performance on recurrence date extraction if evaluated separately.

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis requires demographic metadata (age, race, stage) for the evaluation cohort. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations such as note types where performance degrades (e.g., short nursing notes vs. detailed oncology notes), temporal scope assumptions, handling of ambiguous recurrence language, and performance on notes from institutions other than Mayo.

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** Describe the demographic composition of the training cohort and whether the model has been tested on notes from diverse patient populations. Note any known disparities in performance by age, race, or cancer subtype.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Note any known confounders in the training data (e.g., institutional documentation practices, note templates that may include boilerplate recurrence language) that could affect generalizability.
- **Data Governance**:
  Training data consists of institutional Mayo Clinic clinical notes. Training data is not publicly released. Any use of this tool on new institutional data requires a local IRB review. This tool should NOT be used for real-time clinical surveillance or to make clinical decisions without human expert review.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add the associated publication BibTeX. Acknowledge the base BERT model checkpoint used for fine-tuning.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Mayo
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
