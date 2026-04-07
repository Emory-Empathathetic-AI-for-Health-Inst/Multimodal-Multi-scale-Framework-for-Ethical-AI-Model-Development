# MEFINDER Documentation Requirements

This document defines the model card system for the MEFINDER repository. Every tool — whether currently implemented, partially implemented, or planned — must have a model card.

---

## What Is a Model Card?

A model card is a structured document that describes a tool's purpose, expected inputs and outputs, underlying approach, performance characteristics, limitations, and ethical considerations. In MEFINDER, model cards are the primary mechanism for ensuring that all tools meet the project's ethical AI mandate: that their assumptions, failure modes, data provenance, and potential biases are explicitly documented rather than implicit.

---

## File Placement

Each tool has **one authoritative model card** co-located with its code:

```
<tool-directory>/MODEL_CARD.md
```

Tools that are planned but not yet contributed to the repository have a **stub card** in the central registry:

```
model_cards/stubs/<tool-slug>.md
```

When a planned tool is contributed, its stub becomes the starting point for the co-located card. Move the stub content into the new tool directory and expand it.

The **master registry index** at `model_cards/INDEX.md` maintains a one-row summary of every tool (implemented and planned) and links to its card.

The **blank template** at `model_cards/TEMPLATE.md` is the source of truth for card structure. Copy it when creating a new card.

---

## Card Types

Declare the card type in the YAML front matter as `card_type`. The type determines which sections are required.

| Type | Description | Examples |
|------|-------------|---------|
| `data-utility` | Data processing or transformation tools without a learned prediction component | Niffler, HITI-Preproc, RadQy |
| `dl-model` | Deep learning models with trained weights that produce predictions | mammo-implant-detector, prostate-lesion-detection, SMuRF, MM-STGNN |
| `nlp-pipeline` | NLP or LLM pipelines that process clinical text to produce labels or structure | breast-recurrence-transformer, pco-extraction, RadPrompter |
| `placeholder` | Planned tools not yet implemented | All Part 2 tools in PROJECT_CONTACTS.md |

---

## Required Fields by Card Type

### YAML Front Matter

| Field | `data-utility` | `dl-model` | `nlp-pipeline` | `placeholder` |
|-------|:-:|:-:|:-:|:-:|
| `tool_id` | Required | Required | Required | Required |
| `tool_name` | Required | Required | Required | Required |
| `card_type` | Required | Required | Required | Required |
| `status` | Required | Required | Required | Required |
| `lab` | Required | Required | Required | Required |
| `poc` | Required | Required | Required | Required |
| `repo_path` | Required | Required | Required | — |
| `target_path` | — | — | — | Required |
| `short_description` | Required | Required | Required | Required |
| `input_modality` | Required | Required | Required | Optional |
| `output_type` | Required | Required | Required | Optional |
| `clinical_domain` | Required | Required | Required | Optional |
| `last_updated` | Required | Required | Required | Required |
| `weights_availability` | — | Required | Required | — |
| `external_validation` | — | Required | Required | — |
| `publication` | Optional | Optional | Optional | — |
| `pypi_package` | Optional | Optional | Optional | — |
| `depends_on` | Optional | Optional | Optional | — |
| `used_by` | Optional | Optional | Optional | — |

**Allowed values for enumerated fields:**

- `card_type`: `data-utility` | `dl-model` | `nlp-pipeline` | `placeholder`
- `status`: `Implemented` | `Partial` | `Missing`
- `input_modality`: `DICOM` | `NIfTI` | `PNG` | `XLSX` | `CSV` | `JSON` | `ECG` | `EHR` | `free-text` | `multiple`
- `output_type`: `DICOM` | `NIfTI` | `PNG` | `CSV` | `JSON` | `embeddings` | `segmentation-mask` | `labels` | `metrics` | `multiple`
- `clinical_domain`: `breast-cancer` | `prostate-cancer` | `general-radiology` | `cardiology` | `multi-domain`
- `weights_availability`: `public` | `restricted` | `not-applicable` | `pending`
- `external_validation`: `yes` | `no` | `in-progress` | `not-applicable`

### Prose Sections

| Section | `data-utility` | `dl-model` | `nlp-pipeline` | `placeholder` |
|---------|:-:|:-:|:-:|:-:|
| 1. Purpose and Scope | Required | Required | Required | Required (1–2 sentences) |
| 2. Intended Use | Optional | Required | Required | Skip |
| 3. Data Modalities and Inputs | Required | Required | Required | Skip |
| 4. Technical Specifications | Optional | Required | Required | Skip |
| 5. Outputs | Required | Required | Required | Skip |
| 6. Performance | Not applicable | Required | Required | Skip |
| 7. Known Limitations | Optional | Required | Required | Skip |
| 8. Ethical Considerations | Recommended | Required | Required | Skip |
| 9. Pipeline Integration | Required | Required | Required | Required |
| 10. Citation and Attribution | Optional | Optional | Optional | Skip |
| 11. Maintenance and Contact | Required | Required | Required | Required |

For sections marked **Not applicable** or **Skip**, replace the section body with:

```
Not applicable — [one-line reason].
```

Do not delete the section header; keep it so the structure is consistent across all cards.

---

## Key Requirements

### Research Use Statement (Section 2)

Every `dl-model` and `nlp-pipeline` card that processes patient data **must** include one of the following statements verbatim in Section 2:

> RESEARCH USE ONLY — Not validated for clinical decision support.

> RESEARCH USE ONLY — Clinical validation in progress.

> Clinical validation pending regulatory review.

### Disaggregated Performance (Section 6.2)

Section 6.2 is **required** for all `dl-model` and `nlp-pipeline` cards. If disaggregated performance has not been computed, state this explicitly:

> Disaggregated performance analysis has not been conducted. This is a known limitation. [State whether it is planned and, if so, when or what is blocking it.]

Do not leave Section 6.2 blank.

### PHI and Anonymization (Section 3.2)

Every card for a tool that consumes patient data must address whether inputs must be de-identified before use and whether the tool performs anonymization itself or assumes upstream de-identification.

### Cross-Card Links

Links between cards (in Section 9) must use **relative paths** from the card's own location:

```markdown
- [Breast Recurrence Transformer](../../breast_recurrence_transformer/MODEL_CARD.md)
```

This ensures links resolve correctly in GitHub's file browser and in any downstream documentation system.

---

## Maintenance Workflow

**When a new tool is contributed:**

1. Copy `model_cards/TEMPLATE.md` into the tool's directory as `MODEL_CARD.md`.
2. Fill in all required YAML front matter fields.
3. Fill in or mark TODO each prose section.
4. Add the tool to `model_cards/INDEX.md`.
5. If a stub exists in `model_cards/stubs/`, delete it and update the INDEX link.
6. Update `depends_on` / `used_by` fields in any related cards.

**When a tool's code or results change materially:**

- Update the relevant sections of its `MODEL_CARD.md`.
- Update `last_updated` in the YAML front matter.
- Update the `INDEX.md` entry if status changes.

**Who is responsible:**

The named POC for each tool (see `PROJECT_CONTACTS.md`) is responsible for keeping their tool's model card accurate. The POC must review their card before any major release or external demo.

---

## File Naming and Slugs

Co-located cards: always named `MODEL_CARD.md` (all caps, matches README.md convention).

Stub files: named `<tool-slug>.md` where the slug is lowercase, hyphen-separated, and matches the `tool_id` field in the YAML front matter.

---

## Reference

- Master template: [`model_cards/TEMPLATE.md`](model_cards/TEMPLATE.md)
- Registry index: [`model_cards/INDEX.md`](model_cards/INDEX.md)
- Planned tool stubs: [`model_cards/stubs/`](model_cards/stubs/)
- POC assignments: [`PROJECT_CONTACTS.md`](PROJECT_CONTACTS.md)
