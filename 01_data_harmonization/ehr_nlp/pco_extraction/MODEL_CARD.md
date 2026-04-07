---
tool_name: PCO Extraction (Patient-Centered Outcomes)
lab: "Mayo"
poc: "TBD"
repo_path: "01_data_harmonization/ehr_nlp/pco_extraction/"
short_description: "Fine-tuned GPT-2/BioGPT pipeline for extracting patient-reported adverse effects (fatigue, depression, anxiety, nausea, lymphedema) from clinical text; AI-LAD boundary not yet established."
category: "data-harmonization"
tags:
    - clinical: [breast-cancer]
    - data: [free-text]
last_updated: "2026-04-07"
publication: ""
package_url: ""
---

# Model Card: PCO Extraction (Patient-Centered Outcomes)

> **Status:** Partial | **Type:** nlp-pipeline | **Lab:** Mayo | **POC:** TBD
>
> **Repo path:** `01_data_harmonization/ehr_nlp/pco_extraction/`

---

## 1. Purpose and Scope

> **TODO (POC: TBD):** Expand with 2–4 sentences describing the fine-tuning approach (GPT-2 or BioGPT), what "patient-centered outcomes" means in this context (adverse effects self-reported or documented in notes), and the current status — specifically what the "AI-LAD boundary" issue is and what is still needed to complete this tool.

This tool extracts mentions of patient-reported adverse effects from clinical text using fine-tuned GPT-2/BioGPT models. It targets five outcome categories: fatigue, depression, anxiety, nausea, and lymphedema. The explicit boundary between this tool and the broader AI-LAD system has not yet been established — see PROJECT_CONTACTS.md for status.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: Clinical informatics researchers studying patient-reported outcomes in breast cancer treatment. **Note:** The scope boundary between this tool and the broader AI-LAD framework is not yet defined; consult the POC before integrating this tool into any pipeline.

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Free-text clinical notes or patient-reported text |
| File format | `.csv` |
| Required fields / tags | `Text_snippet` column (and possibly a patient ID column) |
| Preprocessing required upstream | Notes must be de-identified |

Input text must be de-identified before use. This tool does not perform PHI removal.

## 4. Technical Specifications

> **TODO (POC: TBD):** Describe the GPT-2 / BioGPT fine-tuning setup — whether this is a classification head or generation-based extraction, how the five outcome categories are operationalized, and any ensemble or post-processing logic.

| Field | Value |
|---|---|
| Dataset(s) | TODO — institutional Mayo Clinic patient notes / PRO surveys |
| Dataset size | TODO |
| Data source type | Institutional |
| Data use agreement | TODO — IRB protocol number |

> **TODO (POC: TBD):** Fill in dataset details. Note if training labels were derived from patient surveys, structured EHR fields, or manual annotation. Add install command and link to requirements file. Show the minimal command to run PCO extraction on an input CSV.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | Per-snippet adverse effect labels |
| Output format | `.csv` |
| Output location | TODO |

Output has 5 columns corresponding to: fatigue, depression, anxiety, nausea, lymphedema.

> **TODO (POC: TBD):** Confirm exact column names and label encoding (binary 0/1, probability score, or multi-class label).

## 6. Performance

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| TODO | TODO | TODO | |

> **TODO (POC: TBD):** Report per-label F1 scores for all five outcome categories.

Disaggregated performance analysis has not been conducted. This is a known limitation. Analysis requires demographic metadata for the evaluation cohort. Contact the POC for current status.

## 7. Known Limitations and Failure Modes

> **TODO (POC: TBD):** Document known limitations: incomplete AI-LAD integration, performance on informal or abbreviated text, known class imbalance in adverse effect labels, and any known confusion between similar outcome categories (e.g., depression vs. anxiety).

## 8. Ethical Considerations

- **Bias and Fairness**:
  > **TODO (POC: TBD):** Adverse effect reporting rates vary by patient demographics (age, race, health literacy, language). Describe whether the training cohort reflects this variation and whether any known disparities exist in extraction performance.
- **Confounding and Causal Risks**:
  > **TODO (POC: TBD):** Note that patient-reported outcomes may be confounded by documentation practice differences across clinicians. Describe any de-confounding steps taken.
- **Data Governance**:
  Training data consists of institutional Mayo Clinic patient notes. Not publicly released. Local IRB required for new data. Current partial status means the tool boundary is not fully defined; do not use for clinical monitoring or patient communication without expert review.

## 9. Citation and Attribution

> **TODO (POC: TBD):** Add associated publication BibTeX. Acknowledge GPT-2 / BioGPT base checkpoints.

## 10. Maintenance and Contact

**Name**: TBD — see PROJECT_CONTACTS.md
**Affiliation**: Mayo
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
