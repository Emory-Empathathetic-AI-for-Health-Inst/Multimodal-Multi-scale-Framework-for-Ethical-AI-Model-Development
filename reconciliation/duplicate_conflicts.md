# Duplicate / Conflict Log

Track all duplicate-concept or conflicting-content decisions.

| Concept | Conflicting source paths | Resolution chosen | Remaining risk / open question | Owner |
|---|---|---|---|---|
| Niffler / HITI-Preproc / RadPrompter (main vs side) | `main:*` vs `side:*` for each tool directory | Keep single canonical copy from main branch after equivalence check | Re-check only if submodule commits diverge later | assistant |

| Shared model families (MOSCARD, VLM_SS, readmit-stgnn, breast NLP, implant identifier) | corresponding `main:*` and `side:*` directories | Keep canonical copy from main branch after equivalence check | Re-check only if branch code diverges in future | assistant |
| Prostate lesion detection top-level location | `main: Prostate Cancer Lesion Detection/` vs `side: (missing as top-level)` | Keep main branch directory as canonical source for model migration | Cross-reference with side fusion/prostate artifacts in later phase | assistant |
| Side harmonization contains tool variants overlapping main concepts | `side:Harmonization/Radiology/{Niffler_2,HITI-Preproc,PIQUALvsMRQy_codes}` vs canonical main-derived tool/model copies | Preserve side harmonization variants under `unified/tools/harmonization/radiology/` without overwriting canonical tool locations | Future dedup pass needed to decide merge/archive policy | assistant |
| PIQUAL/MRQy codes appears in both branch structures | `main: PIQUALvsMRQy_codes/` vs `side:Harmonization/Radiology/PIQUALvsMRQy_codes/` | Canonicalize to `unified/tools/harmonization/radiology/PIQUALvsMRQy_codes/` (side-copied) and map main as equivalent source | Future optional cleanup: remove one upstream copy after branch policy decision | assistant |
| PIQUALvsMRQy top-level placeholder | `main: PIQUALvsMRQy` vs `side: PIQUALvsMRQy` | Treat as empty placeholder artifact; no unified destination required | Revisit only if populated with executable/contentful files later | assistant |