# Missing Tools Priority Backlog

Prioritized from current `tooling_overview_status.md` after unification.

| Missing tool | Category | Priority (High/Medium/Low) | Why it matters now | Suggested seed code/path | Owner |
|---|---|---|---|---|---|
| RadLLM | Reporting | High | Needed to convert free-text radiology reports into structured labels for monitoring/training loops. | `unified/tools/reporting/radprompter/` | TBD |
| Mammography Cancer Classifier | Mammography AI | High | Core screening triage use case remains absent. | `unified/models/mammography/vlm_ss/`, `unified/models/mammography/implant_identifier/` | TBD |
| Mammography Patch Classifier | Mammography AI | High | Required building block for lesion-localized workflows and explainability chains. | `unified/models/mammography/vlm_ss/` | TBD |
| Mammography Patch Describer | Mammography AI | High | Missing explainable descriptor output (mass/calcification/etc.) needed for clinical interpretability. | `unified/models/mammography/vlm_ss/` | TBD |
| Mammography Special View Detector | Mammography AI | High | Prevents view-mix contamination and improves downstream model consistency. | `unified/models/mammography/implant_identifier/` | TBD |
| Breast Segmenter | Mammography AI | High | Segmentation is foundational for robust feature extraction and artifact control. | `unified/models/mammography/vlm_ss/` | TBD |
| Anomaly Detection | Debiasing & Generalization | High | OOD detection is critical for safe deployment/generalization across institutions. | `unified/tools/harmonization/radiology/RadQy-master/`, `unified/models/multimodal/moscard/` | TBD |
| Prostate Cancer ChatBot | Prostate AI | Medium | Clinical communication/summarization workflow absent despite roadmap requirement. | `unified/tools/reporting/radprompter/` | TBD |
| ClaD | Prostate AI | Medium | Diagnosis nomogram missing; gap in clinically significant prostate cancer stratification tooling. | `unified/fusion/handcrafted/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/` | TBD |
| RadClip | Prostate AI | Medium | Prognosis nomogram absent; recurrence trajectory support currently incomplete. | `unified/fusion/handcrafted/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/` | TBD |
| Histotyping | Prostate AI | Medium | Pathomic subtype-aware recurrence tooling not present. | `unified/tools/harmonization/pathology/HistoQC-master.zip` | TBD |
| Delta Radiomics Prostate | Prostate AI | Medium | Longitudinal radiomics component missing for progression monitoring. | `unified/tools/harmonization/radiology/PIQUALvsMRQy_codes/` | TBD |
| Prostate Shape Distension | Prostate AI | Medium | 3D shape biomarker workflow absent from current unified assets. | `unified/models/prostate/lesion_detection/` | TBD |
| pZVR Biomarker | Prostate AI | Medium | MRI zonal-volume biomarker implementation is not present. | `unified/models/prostate/lesion_detection/` | TBD |
| Cribriform Area Index (CAI) | Prostate AI | Medium | Pathology biomarker extraction for adverse outcomes not implemented. | `unified/tools/harmonization/pathology/HistoQC-master.zip` | TBD |
| MSERg | Data Quality & Preprocessing | Medium | Explicit radiology-pathology co-registration pipeline missing despite fusion roadmap dependency. | `unified/fusion/deep/SMuRF_MultiModal_OPSCC/`, `unified/fusion/deep/MuTriM_breast/` | TBD |
| RadIQ (full FM-OOD implementation) | Data Quality & Preprocessing | Medium | Only related QC tooling exists; roadmap requires dedicated FM-based OOD module. | `unified/tools/harmonization/radiology/RadQy-master/` | TBD |
| Foundation Model Embedding Extractor (standalone) | Reporting & Documentation Support | Medium | Embedding capability exists but not as a reusable standalone tool. | `unified/models/mammography/vlm_ss/MedCLIP/` | TBD |
| Computational Debiasing (standalone toolkit) | Debiasing & Generalization | Medium | Debiasing logic is embedded in model code; no reusable framework boundary exists. | `unified/models/multimodal/moscard/` | TBD |
