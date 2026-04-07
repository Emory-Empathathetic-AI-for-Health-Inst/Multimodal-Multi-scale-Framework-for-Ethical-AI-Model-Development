---
tool_id: recurrence-site-extraction
tool_name: Recurrence Site Extraction
card_type: nlp-pipeline
status: Implemented
lab: [Mayo]
poc: "TBD"
repo_path: "01_data_harmonization/ehr_nlp/recurrence_site_extraction/"
target_path: "01_data_harmonization/ehr_nlp/recurrence_site_extraction/"
short_description: "BioLinkBERT-based extraction of distant recurrence sites from recurrence-positive clinical notes; requires Breast Recurrence Transformer output."
input_modality: [CSV]
output_type: [CSV]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: [breast-recurrence-transformer]
used_by: []
---

# Model Card: Recurrence Site Extraction

> **Status:** Implemented | **Type:** nlp-pipeline | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/ehr_nlp/recurrence_site_extraction/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences describing how BioLinkBERT was adapted for named entity recognition / span extraction of recurrence site mentions (e.g., liver, lung, bone), and what the output labels represent clinically.

This tool uses BioLinkBERT to extract the anatomical sites of distant breast cancer recurrence from clinical notes that have already been classified as recurrence-positive by the Breast Recurrence Transformer. **It must not be run on raw clinical notes directly.**

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: Clinical informatics researchers building structured breast cancer metastasis datasets from retrospective EHR data. Intended for use only on notes that have been pre-filtered by the Breast Recurrence Transformer.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Free-text clinical note snippets (recurrence-positive) |
| File format | `.csv` (output from Breast Recurrence Transformer) |
| Required fields / tags | `PATIENT_ID`, `text`, `Prediction` — must be the output format of the Breast Recurrence Transformer |
| Preprocessing required upstream | Must run [Breast Recurrence Transformer](../breast_recurrence_transformer/MODEL_CARD.md) first and filter to recurrence-positive rows |

### 3.2 Anonymization and PHI Requirements

Input must be de-identified. PHI removal is assumed to have been performed upstream before the Breast Recurrence Transformer was run.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe the BioLinkBERT fine-tuning setup for site extraction (e.g., NER token classification, span extraction, or sequence-to-sequence), and what ontology or label set is used for anatomical sites.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional Mayo Clinic breast oncology notes (recurrence-positive subset) |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details and note data release restrictions.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and link to requirements file.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to run site extraction on the Breast Recurrence Transformer output CSV.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Per-patient distant recurrence site labels |
| Output format | `.csv` |
| Output location | TODO |

> **TODO (POC: TBD):** Document output column names and the label taxonomy used for anatomical sites.

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report F1, precision, and recall for site extraction on the held-out test set. If entity-level and token-level metrics differ, report both.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis requires demographic metadata for the evaluation cohort. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations, e.g., rare or atypical metastasis sites not well-represented in training data, performance degradation on short or heavily abbreviated notes, sensitivity to note type (radiology report vs. oncology note).

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Describe training cohort demographics and known or suspected disparities in extraction performance across patient subgroups.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Note any institutional documentation biases that could affect generalizability.

### 8.3 Clinical Deployment Safeguards

This tool should NOT be used for clinical decision-making without expert review. It is intended for retrospective cohort construction only.

### 8.4 Data Governance

Training data consists of institutional Mayo Clinic clinical notes and is not publicly released. Local IRB review required for use on new data.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — second stage of the breast recurrence NLP chain.

### 9.2 Upstream Dependencies

- [Breast Recurrence Transformer](../breast_recurrence_transformer/MODEL_CARD.md): **required upstream dependency**. This tool must receive the recurrence-positive output CSV from the Breast Recurrence Transformer. Do not run on raw clinical notes.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List MEFINDER tools that consume the recurrence site labels produced by this tool.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX. Acknowledge BioLinkBERT base checkpoint.

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
