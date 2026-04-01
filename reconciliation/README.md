# Reconciliation Directory

This section preserves process, provenance, and consolidation records for repository structural changes.

## Purpose
- Maintain auditable source-to-destination mapping history
- Record move/consolidation operations and conflict-resolution decisions
- Preserve phase completion records for traceability
- Keep implementation-gap status collocated with reconciliation outputs

## Subdirectories
- `logs/`
  - `source_map.md`
  - `move_log.md`
  - `duplicate_conflicts.md`
  - `phase_completion.md`
- `gap_analysis/`
  - `tooling_overview_status.md`
  - `missing_tools_priority.md`

## Notes
Historical source-origin details are intentionally retained in `logs/` for auditability. These records document how assets were consolidated into the current standalone repository structure.