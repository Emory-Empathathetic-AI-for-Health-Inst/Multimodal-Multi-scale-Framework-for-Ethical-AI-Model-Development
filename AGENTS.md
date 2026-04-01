# Repository Guidelines (Reorganized Workspace)

Use this directory as the active cutover workspace.

## Immediate workflow
1. Move/merge code from main + side branches into `unified/`.
2. Log source and decisions in `reconciliation/`.
3. Update gap status in `gap_analysis/` after each major consolidation step.

## Required status labels
- Tool status: `Implemented`, `Partial`, `Missing`
- Maturity status: `Unknown`, `Present`, `Runnable`, `Reproducible`

## Non-negotiable
Do not move content without updating `source_map.md` and `move_log.md` in the same change.
