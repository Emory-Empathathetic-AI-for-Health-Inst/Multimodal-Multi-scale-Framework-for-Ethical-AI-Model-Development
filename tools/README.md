# Tools Directory

This section contains reusable tooling that supports multimodal data readiness and downstream model development for MEFINDER use-cases.

## Scope
- Data quality and preprocessing for clinical imaging inputs
- Data harmonization utilities across heterogeneous acquisition contexts
- Reporting and relabeling support for clinical text/imaging workflows

## Representative tool families
- **Data quality/preprocessing:** Niffler, HITI-Preproc
- **Reporting support:** RadPrompter
- **Harmonization assets:** Radiology/pathology-oriented normalization and QC resources

## How this section is used
- Normalize and prepare modality-specific inputs before feature/model stages
- Standardize outputs needed by `feature_representation/`, `models/`, and `fusion/`
- Provide reusable utilities that can be versioned independently of model code

## Documentation expectations
- Keep this README focused on category-level purpose and usage boundaries.
- Keep project-specific implementation details in each tool's own local documentation.