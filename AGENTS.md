# Repository Guidelines (Reorganized Workspace)

Use this directory as the active tooling-first workspace.

## Immediate workflow
1. Implement and maintain code in top-level roots: `tools/`, `models/`, `fusion/`, `feature_representation/`.
2. Log source and reconciliation decisions in `reconciliation/` (process/audit docs only).
3. Update gap status in `gap_analysis/` after each major consolidation or tooling change.

## Required status labels
- Tool status: `Implemented`, `Partial`, `Missing`
- Maturity status: `Unknown`, `Present`, `Runnable`, `Reproducible`

## Non-negotiable
Do not move content without updating `source_map.md` and `move_log.md` in the same change.