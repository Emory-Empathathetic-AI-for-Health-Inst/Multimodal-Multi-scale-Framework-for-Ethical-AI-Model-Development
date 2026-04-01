# Feature Representation Directory

This section contains modality-specific feature representation assets used to bridge raw data and multimodal modeling.

## Scope
Feature representation workflows are organized by modality/domain and support downstream fusion and prediction tasks:
- `radiology/`
- `pathology/`
- `ehr_genomics/`

## Role in the repository
- Convert heterogeneous modality data into consistent, model-ready representations
- Provide reusable intermediate features for `models/` and `fusion/`
- Support cross-modality alignment required for multimodal phenotype/risk modeling

## Documentation expectations
- Keep this README focused on representation-layer responsibilities.
- Keep implementation details and modality-specific assumptions in local subproject documentation.