---
tool_name: RadPrompter
lab: "HITI"
poc: "Bardia Khosravi"
repo_path: "04_phenotype_discovery/in_context_learning/radprompter/"
short_description: "TOML-driven LLM prompting framework for biomedical in-context learning; pip-installable with 6 tutorials."
category: "phenotype-discovery"
tags:
    - clinical: [radiology, pathology]
    - data: [free-text]
last_updated: "2026-04-07"
publication: ""
package_url: "radprompter"
---

# Model Card: RadPrompter

> **Status:** Implemented | **Type:** nlp-pipeline | **Lab:** HITI | **POC:** Bardia Khosravi
>
> **Repo path:** `04_phenotype_discovery/in_context_learning/radprompter/`

---

## 1. Purpose and Scope

> **TODO (POC: Bardia Khosravi):** Expand with 2–4 sentences describing RadPrompter's core design — TOML-driven prompt templating, the supported LLM backends, and the biomedical in-context learning tasks it is intended for (e.g., phenotyping from radiology reports, structured extraction). Note the 6 tutorial notebooks and pip installability.

RadPrompter is a TOML-driven LLM prompting framework for biomedical in-context learning. It enables structured, reproducible prompting of LLMs (local and API-based) for clinical text tasks such as phenotyping from radiology reports.

**Important:** RadPrompter is a framework, not a model. Clinical validity of any RadPrompter deployment depends entirely on the prompt configuration and LLM used, not on the framework itself. Each distinct RadPrompter application (prompt + LLM + data) should be documented separately.

## 2. Intended Use

RESEARCH USE ONLY — Not validated for clinical decision support.

Intended users: ML researchers, clinical informatics researchers, and data scientists who need a structured, reproducible way to apply LLMs to biomedical text. RadPrompter itself makes no accuracy claims — each deployment with a specific prompt configuration and LLM constitutes a distinct application that requires its own performance evaluation.

## 3. Input Data Modalities

| Field | Value |
|---|---|
| Modality | Free-text biomedical/clinical text |
| File format | TOML prompt config + data file (CSV or similar) |
| Required fields / tags | TOML config specifying prompt template, LLM backend, and output schema; data CSV with a text column |
| Preprocessing required upstream | Text de-identification must be performed upstream for any patient data |

RadPrompter does not perform de-identification. Any clinical text passed to a cloud-based LLM API must be de-identified first. For local LLM deployments, institutional data governance policies govern PHI handling.

## 4. Technical Specifications

RadPrompter is an orchestration framework, not a model. It manages: TOML-based prompt template rendering, LLM client dispatch (OpenAI, HuggingFace, local), output parsing and schema validation, and batch processing.

> **TODO (POC: Bardia Khosravi):** Describe any schema validation or output parsing logic, and how multi-turn prompting and JSON prefill are handled.

Not applicable — RadPrompter is a prompting framework without learned parameters.

```bash
pip install radprompter
```

> **TODO (POC: Bardia Khosravi):** Add any additional dependencies (e.g., for specific LLM backends). Link to requirements file.

See tutorial notebooks:
- `00_basic_usage.ipynb` — basic prompting
- `01_template_prompting.ipynb` — template syntax
- `02_multi_turn_prompting.ipynb` — multi-turn conversations
- `03_schemas.ipynb` — output schema validation
- `04_json_prefill.ipynb` — JSON prefill for structured output
- `05_huggingface_client.ipynb` — local HuggingFace models

> **TODO (POC: Bardia Khosravi):** Add a minimal Python usage example showing how to initialize RadPrompter with a TOML config and run it on a CSV.

## 5. Outputs

| Field | Value |
|---|---|
| Output type | LLM predictions / extracted structured data |
| Output format | `.csv` |
| Output location | Configurable in TOML config |

## 6. Performance

Not applicable — RadPrompter is an orchestration framework; performance depends entirely on the LLM and prompt configuration used. Each specific deployment must be evaluated independently.

## 7. Known Limitations and Failure Modes

> **TODO (POC: Bardia Khosravi):** Document known framework limitations: LLM backend compatibility, rate limiting for API-based LLMs, handling of LLM output parsing failures, and the risk of LLM hallucination in structured extraction tasks. Note that prompt configuration quality directly determines output quality.

## 8. Ethical Considerations

- **Bias and Fairness**:
  RadPrompter itself introduces no demographic bias — bias arises from the LLM used and the prompt design. Any RadPrompter-based application used on patient data should evaluate demographic bias in LLM outputs.
- **Confounding and Causal Risks**:
  LLMs used via RadPrompter may produce plausible-sounding but incorrect extractions (hallucinations). Schema validation helps but does not eliminate this risk.
- **Data Governance**:
  RadPrompter is agnostic to data governance — the deploying researcher is responsible for ensuring input data complies with applicable data use agreements and de-identification requirements. Cloud-based LLMs should not receive identifiable patient data.

## 9. Citation and Attribution

> **TODO (POC: Bardia Khosravi):** Add publication BibTeX if available. Acknowledge LLM frameworks and APIs supported.

## 10. Maintenance and Contact

**Name**: Bardia Khosravi
**Affiliation**: HITI
**Contact**: See PROJECT_CONTACTS.md
**Last Reviewed**: 2026-04-07
