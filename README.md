# Reorganized Workspace

This directory is the canonical tooling workspace.

## Purpose
- Host active code and assets under top-level roots:
  - `tools/`
  - `models/`
  - `fusion/`
  - `feature_representation/`
- Preserve provenance/reconciliation records in `reconciliation/`
- Maintain post-cutover gap analysis in `gap_analysis/` against `TOOLING_OVERVIEW.md`

## Key subdirectories
- `tools/`, `models/`, `fusion/`, `feature_representation/` — active tooling and model code roots
- `reconciliation/` — process/audit documentation (source mapping, move decisions, phase completion)
- `gap_analysis/` — implemented/partial/missing tool status and priority gaps

## Operating rule
For every structural move across code roots, update:
1. `reconciliation/source_map.md`
2. `reconciliation/move_log.md`
3. `reconciliation/duplicate_conflicts.md` (only when conflicts exist)