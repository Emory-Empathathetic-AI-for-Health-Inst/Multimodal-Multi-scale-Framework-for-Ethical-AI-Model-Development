# Models Directory

This section contains model implementations used across MEFINDER research workflows.

## Scope
Model assets in this directory cover multiple clinical tasks and modalities, including:
- Mammography workflows
- Multimodal clinical prediction models
- NLP extraction pipelines for longitudinal clinical notes
- Prostate-focused detection/prognostic modeling assets

## Representative model contexts
- **Multimodal fusion/prediction:** MOSCARD, MM-STGNN-style workflows
- **Mammography:** vision-language and implant-identification related projects
- **Clinical NLP:** treatment, outcome, and recurrence extraction toolkits
- **Prostate:** lesion-focused modeling workflows

## How this section is used
- Train, evaluate, and adapt task-specific models
- Consume prepared inputs from `tools/` and `feature_representation/`
- Feed integrated multimodal pipelines in `fusion/`

## Documentation expectations
- Keep this README at portfolio level.
- Keep model-specific training/evaluation details within each model project's own documentation.