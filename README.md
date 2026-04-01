# MEFINDER Multimodal Tooling Repository

This repository is the working software and analysis hub for the **Multimodal Fusion Initiative for Novel Disease Phenotype Discovery and Population-Specific Risk Prediction (MEFINDER)**.

It organizes reusable tooling and model assets for multimodal cancer AI research, with emphasis on integrating radiology, pathology, clinical text, longitudinal EHR-derived signals, and related population-level context (for example social determinants and genomics-linked features where available).

## Project context
MEFINDER focuses on open, reproducible multimodal methods for clinically meaningful prediction tasks, including:
- Patient breast cancer early recurrence risk and suitability for neoadjuvant chemotherapy (NAC)
- Patient prostate cancer biochemical recurrence risk after definitive therapy

The repository supports tool development, model experimentation, and cross-modality fusion research needed to move from raw heterogeneous data to actionable phenotype/risk modeling.

## Repository structure
- `tools/` — reusable tooling for data quality, harmonization, and reporting support
- `models/` — task/model implementations across mammography, multimodal prediction, NLP, and prostate domains
- `fusion/` — multimodal fusion pipelines (deep and handcrafted)
- `feature_representation/` — modality-specific feature representation assets
- `reconciliation/gap_analysis/` — implementation coverage and backlog tracking against project tooling goals
- `reconciliation/` — provenance and consolidation records retained for auditability (`logs/`) plus analysis status (`gap_analysis/`)

See section-level documentation in:
- `tools/README.md`
- `models/README.md`
- `fusion/README.md`
- `feature_representation/README.md`
- `reconciliation/gap_analysis/README.md`
- `reconciliation/README.md`
- `reconciliation/logs/README.md`

## Representative assets currently present
- **Data quality and preprocessing:** Niffler, HITI-Preproc
- **Reporting support:** RadPrompter
- **Multimodal models:** MOSCARD, MM-STGNN, mammography VLM workflows
- **Clinical NLP toolkits:** Treatment/outcome/recurrence extraction pipelines
- **Specialized detection tasks:** Mammography implant identification, prostate lesion workflows

## Documentation conventions
- Keep top-level section READMEs aligned with repository state and intended use-cases.
- Keep audit/provenance updates in `reconciliation/` when structural moves or consolidations occur.
- Keep `reconciliation/gap_analysis/` synchronized with observable implementation evidence.