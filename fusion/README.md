# Fusion Directory

This section contains multimodal fusion pipelines that integrate features and predictions across modalities.

## Scope
Fusion assets support combining radiology, pathology, and clinical/EHR-derived representations for clinically meaningful prediction tasks.

Current organization includes:
- `deep/` for deep-learning-based multimodal fusion approaches
- `handcrafted/` for feature-engineered and interpretable integration pipelines
- `other/` for additional supporting fusion assets

## Relation to project use-cases
Fusion workflows in this repository support research directions tied to:
- Breast cancer recurrence-oriented multimodal modeling
- Prostate recurrence risk and related phenotype discovery tasks

## Integration points
- Inputs from `feature_representation/` and `models/`
- Upstream data preparation and harmonization from `tools/`

## Documentation expectations
- Keep this README focused on fusion strategy categories and integration boundaries.
- Keep algorithm-specific details in local project documentation under each fusion pipeline.