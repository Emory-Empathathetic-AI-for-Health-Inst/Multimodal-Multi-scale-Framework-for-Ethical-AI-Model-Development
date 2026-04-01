# TOOLING_OVERVIEW Status

Status is based on evidence currently present in top-level `reorganized/` code roots after Phase 2-4 copy-only consolidation.

| Tool (from TOOLING_OVERVIEW.md) | Lab | Status (Implemented/Partial/Missing) | Evidence path in `reorganized/` | Notes |
|---|---|---|---|---|
| RadIQ | HITI | Partial | `tools/harmonization/radiology/RadQy-master/` | Related QC tool present; explicit FM-based OOD implementation not identified. |
| Niffler | HITI | Implemented | `tools/data_quality/niffler/`; `tools/harmonization/radiology/Niffler_2/` | Canonical and variant copies exist. |
| DICOM PreProcessor | HITI | Implemented | `tools/data_quality/hiti_preproc/`; `tools/harmonization/radiology/HITI-Preproc/` | Canonical and harmonization copy present. |
| MRQy | Empathi | Partial | `tools/harmonization/radiology/PIQUALvsMRQy_codes/`; `tools/harmonization/radiology/RadQy-master/` | MRQy-related experiments/tooling present; not a clearly packaged standalone MRQy repo. |
| HistoQC | Empathi | Partial | `tools/harmonization/pathology/HistoQC-master.zip` | Archive artifact present; runnable extracted project not yet validated. |
| MSERg | Empathi | Missing | - | No explicit co-registration tool with this name found in current tree. |
| Mammography Patch Classifier | HITI | Missing | - | No dedicated patch-classifier project found. |
| Mammography Cancer Classifier | HITI | Missing | - | No dedicated whole-image mammography classifier project found. |
| Mammography Patch Describer | HITI | Missing | - | No patch-description model/tool found. |
| Mammography Implant Detector | HITI | Implemented | `models/mammography/implant_identifier/` | Notebook + trained weights present. |
| Mammography Special View Detector | HITI | Missing | - | No explicit special-view detector project found. |
| Breast Segmenter | HITI | Missing | - | No dedicated breast segmentation tool identified. |
| VLM for Mammogram | Mayo | Implemented | `models/mammography/vlm_ss/` | ALBEF + MedCLIP selective-sampling project present. |
| RadLLM | HITI | Missing | - | No explicit RadLLM project found. |
| RadPrompter | HITI | Implemented | `tools/reporting/radprompter/` | Packaged project with tutorials present. |
| Foundation Model Embedding Extractor | HITI | Partial | `models/mammography/vlm_ss/MedCLIP/` | Embedding-capable MedCLIP code exists; no standalone extractor tool/package. |
| Graph-based Multimodal Modeling | Mayo | Implemented | `models/multimodal/readmit_stgnn/` | Graph-based multimodal model code present. |
| AI-LAD | Mayo | Partial | `models/nlp/pco_extraction/` | Similar effect-extraction pipeline present; explicit AI-LAD naming/tool boundary unclear. |
| Multimodal Temporal Modeling | Mayo | Partial | `models/nlp/breast_recurrence_transformer/` | Temporal NLP recurrence modeling present; broad multimodal temporal platform not explicit. |
| SMuRF | Empathi | Implemented | `fusion/deep/SMuRF_MultiModal_OPSCC/` | Named SMuRF project present. |
| MuTriM | Empathi | Implemented | `fusion/deep/MuTriM_breast/` | Named MuTriM project present. |
| Computational Debiasing | Mayo | Partial | `models/multimodal/moscard/` | Causal/confounding mechanisms present; no standalone debiasing toolkit boundary. |
| Anomaly Detection | Mayo | Missing | - | No dedicated anomaly-detection project identified. |
| Prostate Cancer ChatBot | Mayo | Missing | - | No chatbot project found. |
| Rad-Path Prostate Recurrence Tool | Empathi | Partial | `fusion/handcrafted/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/` | Related integrated rad-path classifier exists; explicit named tool not present. |
| ClaD | Empathi | Missing | - | No explicit ClaD project found. |
| RadClip | Empathi | Missing | - | No explicit RadClip project found. |
| Histotyping | Empathi | Missing | - | No explicit histotyping project found. |
| Delta Radiomics Prostate | Empathi | Missing | - | No explicit delta-radiomics prostate project found. |
| Prostate Shape Distension | Empathi | Missing | - | No explicit shape-distension project found. |
| pZVR Biomarker | Empathi | Missing | - | No explicit pZVR project found. |
| Cribriform Area Index (CAI) | Empathi | Missing | - | No explicit CAI project found. |
| Invisible Prostate Cancer Detection | Empathi | Implemented | `models/prostate/lesion_detection/` | Lesion detection project present and mapped to this capability. |