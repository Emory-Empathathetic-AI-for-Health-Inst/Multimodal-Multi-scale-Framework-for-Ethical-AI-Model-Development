# MEFINDER Model Card Template

> Copy this file into your tool's directory as `MODEL_CARD.md` and fill in all fields.
> See [`DOCUMENTATION_REQUIREMENTS.md`](../DOCUMENTATION_REQUIREMENTS.md) for field definitions, required vs. optional rules, and allowed values.

---

```yaml
---
tool_name: "" # e.g. HITI-Preproc
lab: "" # lab name
poc: "" # point-of-contact name
repo_path: "" # e.g. 01_data_harmonization/radiology/HITI-Preproc
short_description: "" # one sentence for INDEX.md table
category: "" # e.g. data-harmonization
tags:
    - clinical: [] # breast-cancer, prostate-cancer, radiology, pathology
    - data: [] # imaging, free-text, tabular
last_updated: "" # YYYY-MM-DD
publication: "" # Publication/preprint URL, or ""
package_url: "" # PyPI package name, or ""
---
```

---

# Model Card: {tool_name}

> **Status:** {status} | **Type:** {card_type} | **Lab:** {lab} | **POC:** {poc}
>
> **Repo path:** `{repo_path}`

---

## 1. Purpose and Scope

_Describe in 2–4 sentences what the tool does, what problem it solves, and which stage of the MEFINDER pipeline it belongs to (01_data_harmonization through 07_infrastructure)._

## 2. Intended Use

_State who the intended users are (e.g., ML engineers, data scientists, clinicians) and the intended research context._

## 3. Input Data Modalities

_Please describe each input data modality this tool takes as an input. Please ensure you include any required preprocessing and assumptions about the usage context._

## 4. Technical Specifications

Please describe any technical specifications for the tool here. If it includes a trained model, please describe its architecture and training cohort (including the source dataset(s), key inclusion/exclusion criteria, and demographics).

## 5. Outputs

_Please describe the expected tool outputs, including their modality/format and how they should be interpreted._

## 6. Performance

_Please describe any available tool performance metrics. Where possible, please ensure you include disaggregated metrics across demographic and clinical subgroups._

## 7. Known Limitations and Failure Modes

_Document populations or conditions where the tool underperforms, preprocessing conditions that degrade performance, and clinical scenarios where output should not be trusted. State explicitly if the tool has not been tested on a diverse population._

## 8. Ethical Considerations

- **Bias and Fairness**:
  _Describe demographic data available during training, whether the training cohort reflects intended deployment populations, known or suspected sources of bias, and any fairness-aware training techniques used._
- **Confounding and Causal Risks**:
  _For models trained on observational data, note known confounders, whether causal or de-confounding methods were used, and risk of spurious correlations._
- **Data Governance**:
  _Note whether training data is publicly released or institutional/private, any data use agreements, and the patient consent model (retrospective IRB, prospective consent, public data)._

## 9. Citation and Attribution

_If a publication exists, paste the BibTeX entry here. If the tool builds on upstream code or pretrained checkpoints, acknowledge them here._

_If no publication: `No publication associated with this tool.`_

## 10. Maintenance and Contact

**Name**: _maintainer name_
**Affiliation**: _maintainer affiliation_
**Contact**: _contact details_
**Last Reviewed**: _YYYY-MM-DD_

---
