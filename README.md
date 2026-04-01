# Reorganized Workspace

This directory is the canonical destination for same-day branch unification.

## Purpose
- Consolidate code from:
  - `multimodal-grant-main-branch/`
  - `multimodal-grant-side-branch/`
- Record all move/reconciliation decisions
- Produce post-cutover gap analysis against `TOOLING_OVERVIEW.md`

## Key subdirectories
- `unified/` — consolidated code/assets
- `reconciliation/` — source mapping + duplicate/conflict decisions + move log
- `gap_analysis/` — implemented/partial/missing tool status and priority gaps

## Operating rule
For every move into `unified/`, update:
1. `reconciliation/source_map.md`
2. `reconciliation/move_log.md`
3. `reconciliation/duplicate_conflicts.md` (only when conflicts exist)
