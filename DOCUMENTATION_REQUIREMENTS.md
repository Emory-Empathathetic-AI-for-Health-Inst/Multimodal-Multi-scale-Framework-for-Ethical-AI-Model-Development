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

Card type is indicated in the card header (`**Type:**`) as a human-readable annotation. It determines which prose sections are required.

| Type | Description | Examples |
|------|-------------|---------|
| `data-utility` | Data processing or transformation tools without a learned prediction component | Niffler, HITI-Preproc, RadQy |
| `dl-model` | Deep learning models with trained weights that produce predictions | mammo-implant-detector, prostate-lesion-detection, SMuRF, MM-STGNN |
| `nlp-pipeline` | NLP or LLM pipelines that process clinical text to produce labels or structure | breast-recurrence-transformer, pco-extraction, RadPrompter |
| `placeholder` | Planned tools not yet implemented | All Part 2 tools in PROJECT_CONTACTS.md |

---

## Required Fields

### YAML Front Matter

All cards use the same YAML front matter fields regardless of card type.

| Field | Required | Description |
|-------|:--------:|-------------|
| `tool_name` | Required | Full display name of the tool |
| `lab` | Required | Lab name (string) |
| `poc` | Required | Point-of-contact name |
| `repo_path` | Required | Path to tool directory from repo root; `""` for stubs |
| `short_description` | Required | One sentence for the INDEX.md table |
| `category` | Required | Pipeline stage (see allowed values below) |
| `tags` | Required | Clinical and data modality tags (see allowed values below) |
| `last_updated` | Required | `YYYY-MM-DD` |
| `publication` | Optional | Publication or preprint URL, or `""` |
| `package_url` | Optional | PyPI package name, or `""` |

**Allowed values for `category`:**

- `data-harmonization`
- `feature-extraction`
- `multimodal-embedding`
- `phenotype-discovery`
- `use-cases`
- `infrastructure`

**Allowed values for `tags.clinical`:**

- `breast-cancer`
- `prostate-cancer`
- `radiology`
- `pathology`
- `cardiology`

**Allowed values for `tags.data`:**

- `imaging`
- `free-text`
- `tabular`

---

### Prose Sections

| Section | `data-utility` | `dl-model` | `nlp-pipeline` | `placeholder` |
|---------|:-:|:-:|:-:|:-:|
| 1. Purpose and Scope | Required | Required | Required | Required (1–2 sentences) |
| 2. Intended Use | Optional | Required | Required | Skip |
| 3. Input Data Modalities | Required | Required | Required | Skip |
| 4. Technical Specifications | Optional | Required | Required | Skip |
| 5. Outputs | Required | Required | Required | Skip |
| 6. Performance | Not applicable | Required | Required | Skip |
| 7. Known Limitations and Failure Modes | Optional | Required | Required | Skip |
| 8. Ethical Considerations | Recommended | Required | Required | Skip |
| 9. Citation and Attribution | Optional | Optional | Optional | Skip |
| 10. Maintenance and Contact | Required | Required | Required | Required |

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

---

## Maintenance Workflow

**When a new tool is contributed:**

1. Copy `model_cards/TEMPLATE.md` into the tool's directory as `MODEL_CARD.md`.
2. Fill in all YAML front matter fields.
3. Fill in or mark TODO each prose section.
4. Add the tool to `model_cards/INDEX.md`.
5. If a stub exists in `model_cards/stubs/`, delete it and update the INDEX link.

**When a tool's code or results change materially:**

- Update the relevant sections of its `MODEL_CARD.md`.
- Update `last_updated` in the YAML front matter.
- Update the `INDEX.md` entry if status changes.

**Who is responsible:**

The named POC for each tool (see `PROJECT_CONTACTS.md`) is responsible for keeping their tool's model card accurate. The POC must review their card before any major release or external demo.

---

## File Naming and Slugs

Co-located cards: always named `MODEL_CARD.md` (all caps, matches README.md convention).

Stub files: named `<tool-slug>.md` where the slug is lowercase and hyphen-separated.

---

## Reference

- Master template: [`model_cards/TEMPLATE.md`](model_cards/TEMPLATE.md)
- Registry index: [`model_cards/INDEX.md`](model_cards/INDEX.md)
- Planned tool stubs: [`model_cards/stubs/`](model_cards/stubs/)
- POC assignments: [`PROJECT_CONTACTS.md`](PROJECT_CONTACTS.md)
