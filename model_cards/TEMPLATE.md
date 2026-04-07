# MEFINDER Model Card Template

> Copy this file into your tool's directory as `MODEL_CARD.md` and fill in all fields.
> See [`DOCUMENTATION_REQUIREMENTS.md`](../DOCUMENTATION_REQUIREMENTS.md) for field definitions, required vs. optional rules, and allowed values.

---

```yaml
---
tool_id: ""
tool_name: ""
card_type: ""           # data-utility | dl-model | nlp-pipeline | placeholder
status: ""              # Implemented | Partial | Missing
lab: []                 # HITI | Mayo | Empathi
poc: ""                 # name from PROJECT_CONTACTS.md, or "TBD"
repo_path: ""           # path relative to repo root, e.g. 01_data_harmonization/radiology/Niffler/
target_path: ""         # same as repo_path for implemented tools; planned path for placeholder tools
short_description: ""   # one sentence for INDEX.md table
input_modality: []      # DICOM | NIfTI | PNG | XLSX | CSV | JSON | ECG | EHR | free-text | multiple
output_type: []         # DICOM | NIfTI | PNG | CSV | JSON | embeddings | segmentation-mask | labels | metrics | multiple
clinical_domain: []     # breast-cancer | prostate-cancer | general-radiology | cardiology | multi-domain
last_updated: ""        # YYYY-MM-DD
weights_availability: "" # public | restricted | not-applicable | pending  [required for dl-model and nlp-pipeline]
external_validation: ""  # yes | no | in-progress | not-applicable         [required for dl-model and nlp-pipeline]
publication: ""          # DOI or arXiv URL, or ""
pypi_package: ""         # PyPI package name, or ""
depends_on: []           # list of tool_id values this tool requires upstream
used_by: []              # list of tool_id values that consume this tool's output
---
```

---

# Model Card: {tool_name}

> **Status:** {status} | **Type:** {card_type} | **Lab:** {lab} | **POC:** {poc}
>
> **Repo path:** `{repo_path}`

---

## 1. Purpose and Scope

> **TODO:** Describe in 2–4 sentences what the tool does, what problem it solves, and which stage of the MEFINDER pipeline it belongs to (01_data_harmonization through 07_infrastructure).

## 2. Intended Use

> **TODO:** State who the intended users are (e.g., ML researchers, data engineers, clinical informaticists) and the intended research context.
>
> **Required for all tools that process patient data:** Include one of the following verbatim statements:
> - `RESEARCH USE ONLY — Not validated for clinical decision support.`
> - `RESEARCH USE ONLY — Clinical validation in progress.`
> - `Clinical validation pending regulatory review.`
>
> If this is a framework (e.g., RadPrompter) rather than a model, note that clinical validity depends on each specific deployment configuration, not the framework itself.
>
> *Not applicable for `data-utility` and `placeholder` cards — replace with:* `Not applicable — this is a data processing utility / placeholder tool.`

## 3. Data Modalities and Inputs

> **TODO:** Fill in the table below and address PHI requirements in 3.2.
>
> *Not applicable for `placeholder` cards.*

### 3.1 Input Format

| Field | Value |
|---|---|
| Modality | |
| File format | |
| Required fields / tags | |
| Preprocessing required upstream | |

### 3.2 Anonymization and PHI Requirements

> **TODO:** State whether input data must be de-identified before this tool is used, and whether this tool performs anonymization itself or assumes it has been done upstream. Reference Niffler if DICOM anonymization is applicable.

## 4. Technical Specifications

> **TODO:** Fill in subsections below.
>
> *Section 4.2 (Training Data) is not applicable for `data-utility` cards — note that explicitly.*
> *This entire section is not applicable for `placeholder` cards.*

### 4.1 Architecture / Algorithm

> **TODO:** Describe the model architecture or processing algorithm in 1–3 sentences.

### 4.2 Training Data

| Field | Value |
|---|---|
| Dataset(s) | |
| Dataset size | |
| Data source type | public / institutional / mixed |
| Data use agreement | |

### 4.3 Installation and Dependencies

> **TODO:** Provide the install command or environment setup instructions. Link to the `requirements.txt` or `environment.yml` if one exists.

### 4.4 Inference / Usage

> **TODO:** Provide the minimal working example or the key command to run inference. Keep brief — link to `README.md` for full detail. For pip-installable tools, show the import and minimal usage pattern.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | |
| Output format | |
| Output location | |

> **TODO:** Fill in the table. If the output schema (e.g., CSV column names) is important, document it here or link to where it is defined.

## 6. Performance

> **TODO:** Fill in metrics for all `dl-model` and `nlp-pipeline` cards.
>
> *Not applicable for `data-utility` and `placeholder` cards — replace with:* `Not applicable — this tool does not produce predictions.`

### 6.1 Primary Metrics

| Metric | Value | Dataset | Notes |
|---|---|---|---|
| | | | |

### 6.2 Disaggregated Performance

> **REQUIRED** (do not leave blank): Report performance broken down by sex/gender, age group, race/ethnicity, and institution or scanner type where available.
>
> If disaggregated metrics have not been computed, state explicitly:
> *"Disaggregated performance analysis has not been conducted. [State whether planned and what is blocking it.]"*

## 7. Known Limitations and Failure Modes

> **TODO:** Document patient populations or imaging conditions where the tool underperforms, preprocessing conditions that degrade performance, and clinical scenarios where output should not be trusted. State explicitly if the tool has not been tested on a diverse population.
>
> *Optional for `data-utility`; not applicable for `placeholder`.*

## 8. Ethical Considerations

> **TODO:** Address all applicable subsections. Required for `dl-model` and `nlp-pipeline`; recommended for `data-utility`; not applicable for `placeholder`.

### 8.1 Bias and Fairness

> **TODO:** Describe demographic data available during training, whether the training cohort reflects intended deployment populations, known or suspected sources of bias, and any fairness-aware training techniques used.

### 8.2 Confounding and Causal Risks

> **TODO:** For models trained on observational data, note known confounders, whether causal or de-confounding methods were used, and risk of spurious correlations.

### 8.3 Clinical Deployment Safeguards

> **TODO:** State conditions under which this tool should NOT be used clinically and what monitoring or human oversight is required before clinical use.

### 8.4 Data Governance

> **TODO:** Note whether training data is publicly released or institutional/private, any data use agreements, and the patient consent model (retrospective IRB, prospective consent, public data).

## 9. MEFINDER Pipeline Integration

### 9.1 Position in Pipeline

> **TODO:** State which pipeline stage this tool belongs to:
> `01_data_harmonization` | `02_feature_extraction` | `03_multimodal_embedding` | `04_phenotype_discovery` | `05_use_cases` | `06_evaluation` | `07_infrastructure`

### 9.2 Upstream Dependencies

> **TODO:** List MEFINDER tools that must run before this tool, if any. Use relative links:
> `- [Tool Name](../path/to/MODEL_CARD.md): brief explanation of dependency`
>
> If none: `None — this tool operates on raw data.`

### 9.3 Downstream Consumers

> **TODO:** List MEFINDER tools that consume this tool's output, if known. Use relative links.
>
> If none or unknown, state that.

## 10. Citation and Attribution

> **TODO:** If a publication exists, paste the BibTeX entry here. If the tool builds on upstream code or pretrained checkpoints (e.g., nnU-Net, ALBEF, MedCLIP, MoCo-CXR), acknowledge them here.
>
> If no publication: `No publication associated with this tool.`

## 11. Maintenance and Contact

| Field | Value |
|---|---|
| POC | |
| Lab | |
| Contact | |
| Status | |
| Card last reviewed | |

> **TODO:** Fill in from PROJECT_CONTACTS.md. For contact, use email if known or link to GitHub issues.

---

*This model card follows the MEFINDER Model Card System v1.0. See [DOCUMENTATION_REQUIREMENTS.md](../DOCUMENTATION_REQUIREMENTS.md) for the full specification.*
