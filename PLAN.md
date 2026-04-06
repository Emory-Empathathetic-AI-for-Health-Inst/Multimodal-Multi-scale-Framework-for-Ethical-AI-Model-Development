# Code Migration Plan: Reorganize into 01–05 Structure

## Objective
Migrate **code assets only** (no project meta-information reorganization required) into:

- `01_data_harmonization/` (Radiology, pathology, EHR, federated learning)
- `02_feature_extraction/` (Radiomics, pathomics, deep & causal features)
- `03_multimodal_embedding/` (Engineered fusion, deep joint embedding, temporal)
- `04_phenotype_discovery/` (Clustering, in-context learning)
- `05_use_cases/` (Breast cancer & prostate cancer with parallel structure)

## Scope Rules
- In scope: executable code and runtime code-adjacent assets used by code (`*.py`, `*.ipynb`, `*.sh`, required local config/json/yaml consumed by code).
- Out of scope: portfolio-level docs/meta reorganization (`README` hierarchy, reconciliation notes, governance docs).
- Full cutover: no compatibility shims, no dual locations, no re-export aliases.

## Discovery Summary (Current State)
- Main code sources: `tools/`, `models/`, `fusion/`.
- Important duplication:
  - `tools/harmonization/radiology/Niffler_2/modules_2` ≈ `tools/data_quality/niffler/modules` (nearly identical).
  - `tools/harmonization/radiology/HITI-Preproc` ≈ `tools/data_quality/hiti_preproc`.
- Disease-specific code already exists and should move under use-cases:
  - Breast: `fusion/deep/MuTriM_breast`, `models/mammography/*`, `models/nlp/breast_*`, `models/nlp/recurrence_site_extraction`.
  - Prostate: `models/prostate/lesion_detection`, `fusion/handcrafted/...Prostatectomy`, parts of `PIQUALvsMRQy_codes`.
- No explicit federated-learning implementation found in current code.
- High-risk path fragility exists (absolute local machine paths + `PYTHONPATH=.:$PYTHONPATH` shell assumptions).

---

## Target Mapping (Canonical)

### `01_data_harmonization/`
- `radiology/`
  - `tools/harmonization/radiology/Niffler_2` (canonical)
  - `tools/harmonization/radiology/HITI-Preproc` (canonical)
  - `tools/harmonization/radiology/RadQy-master`
  - `tools/data_quality/{niffler,hiti_preproc}` removed after dedupe (code no longer duplicated)
- `pathology/`
  - (currently no distinct pathology harmonization package; create container for future code)
- `ehr/`
  - shared EHR harmonization/preprocessing utilities that are standalone (if extracted safely)
- `federated_learning/`
  - empty scaffold for now (no current code to migrate)

### `02_feature_extraction/`
- `radiomics/`
  - prostate/breast extraction modules that are not end-to-end use-case bundles
- `pathomics/`
  - standalone pathology embedding/preprocessing utilities where separable
- `deep_causal_features/`
  - generic deep feature extractors / causal feature modules not bound to a single use-case

### `03_multimodal_embedding/`
- `engineered_fusion/`
  - reusable non-disease-specific engineered fusion code
- `deep_joint_embedding/`
  - `fusion/deep/SMuRF_MultiModal_OPSCC`
  - `models/multimodal/moscard`
- `temporal/`
  - `models/multimodal/readmit_stgnn`

### `04_phenotype_discovery/`
- `clustering/`
  - generic clustering/phenotyping assets (including unsupervised clustering notebooks/scripts not tied to a disease bundle)
- `in_context_learning/`
  - `tools/reporting/radprompter`

### `05_use_cases/` (parallel internal structure)

#### `05_use_cases/breast_cancer/`
- `01_data_harmonization/` (breast-specific prep scripts)
- `02_feature_extraction/`
  - `models/mammography/vlm_ss`
  - `models/mammography/implant_identifier`
  - `models/nlp/breast_recurrence_transformer`
  - `models/nlp/breast_treatment_extraction`
  - `models/nlp/recurrence_site_extraction`
- `03_multimodal_embedding/`
  - `fusion/deep/MuTriM_breast`
- `04_phenotype_discovery/`
  - breast-specific recurrence phenotype discovery scripts (if present)

#### `05_use_cases/prostate_cancer/`
- `01_data_harmonization/`
  - prostate-specific prep/harmonization pieces from PIQUAL workflows where applicable
- `02_feature_extraction/`
  - `models/prostate/lesion_detection`
  - PIQUAL segmentation/registration feature scripts
- `03_multimodal_embedding/`
  - `fusion/handcrafted/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy`
- `04_phenotype_discovery/`
  - PIQUAL clustering assets (e.g., `Unsupervised_Clustering.ipynb`)

---

## Execution Plan (Phased)

### Phase 1 — Migration Manifest and Guardrails (sequential)
1. Generate a migration manifest (`old_path -> new_path`) for all code-bearing files/directories.
2. Mark each entry as: `move`, `dedupe-delete`, or `defer`.
3. Lock canonical copy for duplicated code:
   - Keep harmonization copies (`Niffler_2`, `HITI-Preproc`), remove data_quality duplicates after verification.
4. Define explicit non-goals (no README/meta reshuffle).

### Phase 2 — Create New Skeleton (sequential)
1. Create `01..05` top-level directories and required subtrees.
2. Create `05_use_cases/{breast_cancer,prostate_cancer}/{01..04}` in parallel structure.
3. Prepare empty `01_data_harmonization/federated_learning/` scaffold.

### Phase 3 — Parallel Code Moves (parallel workstreams)
Run in parallel because file sets are independent:
- **Stream A**: `01_data_harmonization` migration + dedupe of Niffler/HITI.
- **Stream B**: `03_multimodal_embedding` migration (`moscard`, `readmit_stgnn`, `SMuRF`).
- **Stream C**: `04_phenotype_discovery` migration (`radprompter`, clustering assets).
- **Stream D**: `05_use_cases/breast_cancer` migration.
- **Stream E**: `05_use_cases/prostate_cancer` migration.

### Phase 4 — Path/Import Refactor and Cutover (parallel by stream, then unify)
1. Update import/module paths broken by move.
2. Replace brittle launch assumptions:
   - remove hardcoded `PYTHONPATH=.:$PYTHONPATH` dependency where possible.
   - parameterize absolute machine paths (`/home/...`, `C:\Users\...`, `/media/...`).
3. Update script/config references that assume old root layout.
4. Delete old code locations once replacement is complete (no forwarding wrappers).

### Phase 5 — Verification (must pass before handoff)
1. **Structural checks**
   - No code files remain in legacy locations (`tools/`, `models/`, `fusion/`) except intentional meta/docs.
   - Manifest diff is 1:1 satisfied.
2. **Runtime/import checks**
   - Project-local smoke runs for moved entry points (`--help`/dry-run) in each migrated subsystem.
   - Unit tests where already present (notably Niffler suites) against new paths.
3. **Use-case proof points**
   - One breast pipeline entry point starts from new location.
   - One prostate pipeline entry point starts from new location.

---

## Risk Register and Mitigations
- **Duplicate code drift** (Niffler/HITI mirrors)
  - Mitigation: canonicalize one copy, delete mirror copy after verification.
- **Hidden path coupling** (absolute local paths)
  - Mitigation: parameterize with CLI/config; fail fast when missing paths.
- **Relative-import fragility after move**
  - Mitigation: move project directories atomically where possible; only split file-level when dependency-safe.
- **Mixed-quality scripts/notebook-style Python**
  - Mitigation: verify via targeted runtime checks per entrypoint, not blanket py_compile across known notebook-style scripts.

---

## External Guidance Used
- Cookiecutter Data Science (phase-oriented project organization and modular code extraction):
  - https://cookiecutter-data-science.drivendata.org/using-the-template/
- Flower architecture (clear separation of orchestration vs app logic for federated-learning placement):
  - https://flower.ai/docs/framework/explanation-flower-architecture.html
- MONAI Deploy workloads (clinical workload decomposition into computational layers):
  - https://github.com/Project-MONAI/monai-deploy/blob/main/guidelines/monai-workloads.md

These reinforce: (1) stage-based directory boundaries, (2) strict separation of orchestration and domain logic, and (3) workload-aware grouping for high-reliability clinical AI code.

---

## Deliverables at Completion
- New `01..05` code layout populated.
- `05_use_cases` with breast/prostate parallel substructure.
- Legacy duplicated code removed.
- Updated imports/scripts/config paths.
- Verification report tied to manifest and smoke tests.
