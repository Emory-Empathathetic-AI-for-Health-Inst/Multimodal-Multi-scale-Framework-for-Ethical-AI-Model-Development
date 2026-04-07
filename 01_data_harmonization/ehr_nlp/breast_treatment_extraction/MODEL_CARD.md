---
tool_id: breast-treatment-extraction
tool_name: Breast Treatment Extraction
card_type: nlp-pipeline
status: Implemented
lab: [Mayo]
poc: "TBD"
repo_path: "01_data_harmonization/ehr_nlp/breast_treatment_extraction/"
target_path: "01_data_harmonization/ehr_nlp/breast_treatment_extraction/"
short_description: "Two-phase (rule-based + BioGPT) pipeline for structured reconstruction of breast cancer treatment timelines from clinical notes."
input_modality: [XLSX]
output_type: [CSV]
clinical_domain: [breast-cancer]
last_updated: "2026-04-07"
weights_availability: "restricted"
external_validation: "no"
publication: ""
pypi_package: ""
depends_on: []
used_by: []
---

# Model Card: Breast Treatment Extraction

> **Status:** Implemented | **Type:** nlp-pipeline | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/ehr_nlp/breast_treatment_extraction/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences describing the two-phase approach — what the rule-based first phase extracts, what BioGPT handles in the second phase, and what the final structured timeline looks like (e.g., treatment type, start/end dates, dose).

This pipeline uses a two-phase approach combining rule-based extraction and BioGPT to reconstruct structured breast cancer treatment timelines from clinical notes. It operates on the same input format as the Breast Recurrence Transformer but is an independent pipeline.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: Clinical informatics researchers building structured breast cancer treatment datasets from retrospective EHR data.

## 3. Data Modalities and Inputs

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | Free-text clinical notes |
| File format | `.xlsx` |
| Required fields / tags | `ANON_ID`, `NOTE_TYPE`, `NOTE_DATE`, `NOTE` |
| Preprocessing required upstream | Notes must be de-identified |

### 3.2 Anonymization and PHI Requirements

Input clinical notes must be de-identified before use. This tool does not perform PHI removal.

## 4. Technical Specifications

### 4.1 Architecture / Algorithm

> **TODO (POC: TBD):** Describe Phase 1 (rule-based: regex or pattern matching for treatment keywords, dates, dosing) and Phase 2 (BioGPT: what it handles that rules miss, how outputs are merged). Describe any post-processing normalization.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional Mayo Clinic breast oncology notes |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Note that BioGPT was likely fine-tuned on a labeled subset; document the annotation process.

### 4.3 Installation and Dependencies

> **TODO (POC: TBD):** Add install command and link to requirements file. Note BioGPT model checkpoint source.

### 4.4 Inference / Usage

> **TODO (POC: TBD):** Show the minimal command to run on an input `.xlsx` file.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Structured treatment timeline per patient |
| Output format | `.csv` |
| Output location | TODO |

> **TODO (POC: TBD):** Document output column schema (treatment type, start date, end date, dose, route, etc.).

## 6. Performance

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report F1, precision, and recall for treatment type extraction and date extraction separately.

### 6.2 Disaggregated Performance

Disaggregated performance analysis has not been conducted. This is a known limitation. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known failure modes — e.g., treatments mentioned only implicitly, ambiguous date references, BioGPT hallucination risk for structured extraction, performance on note types not well-represented in training.

## 8. Ethical Considerations

### 8.1 Bias and Fairness

> **TODO (POC: TBD):** Describe training cohort demographics and whether extraction performance varies by patient subgroup or documentation practice.

### 8.2 Confounding and Causal Risks

> **TODO (POC: TBD):** Note institutional documentation biases (e.g., if treatment templates vary by physician or department) that may limit generalizability.

### 8.3 Clinical Deployment Safeguards

Not intended for clinical decision support. Retrospective research use only. All extracted timelines should be validated by domain experts before use in any clinical study.

### 8.4 Data Governance

Training data consists of institutional Mayo Clinic clinical notes and is not publicly released. Local IRB review required for use on new data.

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

`01_data_harmonization` — EHR NLP layer producing structured treatment data from clinical notes.

### 9.2 Upstream Dependencies

None — this tool operates on raw (de-identified) clinical notes.

### 9.3 Downstream Consumers

> **TODO (POC: TBD):** List MEFINDER tools that consume treatment timeline data produced by this tool.

## 10. Citation and Attribution

> **TODO (POC: TBD):** Add publication BibTeX. Acknowledge BioGPT base checkpoint.

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
