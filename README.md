# Multimodal Tooling Repository

This repository organizes multimodal tooling assets for data quality, harmonization, reporting, model development, and multimodal fusion workflows.

## Repository scope
- Provide a single codebase for multimodal tooling and model assets.
- Keep tooling and model code in stable top-level roots for direct development and reuse.
- Retain audit/process history in `reconciliation/`.
- Track implementation coverage and priority gaps in `gap_analysis/`.

## Directory layout
- `tools/` — tooling projects for data quality, harmonization, and reporting workflows.
- `models/` — model projects across mammography, multimodal, NLP, and prostate domains.
- `fusion/` — multimodal fusion implementations (deep and handcrafted pipelines).
- `feature_representation/` — feature representation assets by modality/domain.
- `gap_analysis/` — current implemented/partial/missing tooling status and prioritized backlog.
- `reconciliation/` — process records (`source_map.md`, `move_log.md`, `duplicate_conflicts.md`, `phase_completion.md`).

## Working conventions
- Make structural updates directly in the top-level code roots.
- Keep `gap_analysis/` aligned with observable repository state.
- When code is moved or consolidated, update reconciliation records in the same change to preserve traceability.