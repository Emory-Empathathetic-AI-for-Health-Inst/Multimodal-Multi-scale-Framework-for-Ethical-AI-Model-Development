# MEFINDER Model Card Index

This index tracks every tool in the MEFINDER framework — implemented, partial, and planned. Each row links to the tool's authoritative model card (co-located with code for existing tools, or a stub in `model_cards/stubs/` for planned tools).

**Maintaining this index:** When adding a new tool card, add a row here. When a planned tool's code is contributed, update the link from `stubs/` to the co-located card and change Status to `Implemented` or `Partial`. See [`DOCUMENTATION_REQUIREMENTS.md`](../DOCUMENTATION_REQUIREMENTS.md) for the full maintenance workflow.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| Implemented | Substantive, runnable code present |
| Partial | Code present but incomplete relative to roadmap |
| Missing | No code in repository yet |

---

## 01 — Data Harmonization / Radiology

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| Niffler | data-utility | Implemented | HITI | Beatrice Brown-Mulry | general-radiology | [MODEL_CARD.md](../01_data_harmonization/radiology/Niffler/MODEL_CARD.md) |
| DICOM PreProcessor (HITI-Preproc) | data-utility | Implemented | HITI | Beatrice Brown-Mulry | general-radiology | [MODEL_CARD.md](../01_data_harmonization/radiology/HITI-Preproc/MODEL_CARD.md) |
| RadIQ / RadQy | data-utility | Partial | HITI | TBD | general-radiology | [MODEL_CARD.md](../01_data_harmonization/radiology/RadQy-master/MODEL_CARD.md) |
| MRQy (experiments) | data-utility | Partial | Empathi | TBD | general-radiology | [MODEL_CARD.md](../01_data_harmonization/radiology/PIQUALvsMRQy_codes/MODEL_CARD.md) |
| Mammography Implant Detector | dl-model | Implemented | HITI | Beatrice Brown-Mulry | breast-cancer | [MODEL_CARD.md](../01_data_harmonization/radiology/mammo_implant_identifier/MODEL_CARD.md) |
| RadIQ (FM-OOD module) | placeholder | Missing | HITI | TBD | general-radiology | [stub](stubs/radiq-fm-ood.md) |
| Anomaly Detection | placeholder | Missing | Mayo | TBD | general-radiology | [stub](stubs/anomaly-detection.md) |
| RadLLM | placeholder | Missing | HITI | TBD | general-radiology | [stub](stubs/radllm.md) |
| ROI-Lift | placeholder | Missing | HITI | Beatrice Brown-Mulry | general-radiology | [stub](stubs/roi-lift.md) |
| Atlas | placeholder | Missing | HITI | Jahanzaib Malik | general-radiology | [stub](stubs/atlas.md) |
| MSERg | placeholder | Missing | Empathi | TBD | multi-domain | [stub](stubs/mserg.md) |

## 01 — Data Harmonization / EHR & NLP

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| Breast Recurrence Transformer | nlp-pipeline | Implemented | Mayo | TBD | breast-cancer | [MODEL_CARD.md](../01_data_harmonization/ehr_nlp/breast_recurrence_transformer/MODEL_CARD.md) |
| Recurrence Site Extraction | nlp-pipeline | Implemented | Mayo | TBD | breast-cancer | [MODEL_CARD.md](../01_data_harmonization/ehr_nlp/recurrence_site_extraction/MODEL_CARD.md) |
| Breast Treatment Extraction | nlp-pipeline | Implemented | Mayo | TBD | breast-cancer | [MODEL_CARD.md](../01_data_harmonization/ehr_nlp/breast_treatment_extraction/MODEL_CARD.md) |
| PCO Extraction (AI-LAD adjacent) | nlp-pipeline | Partial | Mayo | TBD | breast-cancer | [MODEL_CARD.md](../01_data_harmonization/ehr_nlp/pco_extraction/MODEL_CARD.md) |

## 01 — Data Harmonization / Pathology

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| HistoQC | placeholder | Missing | Empathi | TBD | multi-domain | [stub](stubs/histoqc.md) |

## 02 — Feature Extraction

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| Invisible Prostate Cancer Detection | dl-model | Implemented | Empathi | TBD | prostate-cancer | [MODEL_CARD.md](../02_feature_extraction/deep_features/prostate_lesion_detection/MODEL_CARD.md) |
| Foundation Model Embedding Extractor | placeholder | Missing | HITI | TBD | multi-domain | [stub](stubs/fm-embedding-extractor.md) |
| Histotyping | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/histotyping.md) |
| Delta Radiomics Prostate | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/delta-radiomics-prostate.md) |
| Prostate Shape Distension | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/prostate-shape-distension.md) |
| pZVR Biomarker | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/pzvr-biomarker.md) |
| Cribriform Area Index (CAI) | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/cai.md) |

## 03 — Multimodal Embedding

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| VLM for Mammogram (mammo_vlm_ss) | dl-model | Implemented | Mayo | TBD | breast-cancer | [MODEL_CARD.md](../03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/MODEL_CARD.md) |
| SMuRF | dl-model | Implemented | Empathi | TBD | general-radiology | [MODEL_CARD.md](../03_multimodal_embedding/deep_joint_embedding/SMuRF_MultiModal_OPSCC/MODEL_CARD.md) |
| MOSCARD (Computational Debiasing) | dl-model | Partial | Mayo | TBD | cardiology | [MODEL_CARD.md](../03_multimodal_embedding/deep_joint_embedding/moscard/MODEL_CARD.md) |
| Graph-based Multimodal Modeling (MM-STGNN) | dl-model | Implemented | Mayo | TBD | general-radiology | [MODEL_CARD.md](../03_multimodal_embedding/temporal_fusion/readmit_stgnn/MODEL_CARD.md) |
| MuTriM | dl-model | Implemented | Empathi | TBD | breast-cancer | [MODEL_CARD.md](../03_multimodal_embedding/temporal_fusion/MuTriM_breast/MODEL_CARD.md) |
| Rad-Path Prostate Recurrence Classifier | dl-model | Partial | Empathi | TBD | prostate-cancer | [MODEL_CARD.md](../03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/MODEL_CARD.md) |
| Computational Debiasing Toolkit (standalone) | placeholder | Missing | Mayo | TBD | multi-domain | [stub](stubs/computational-debiasing-toolkit.md) |

## 04 — Phenotype Discovery

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| RadPrompter | nlp-pipeline | Implemented | HITI | Bardia Khosravi | multi-domain | [MODEL_CARD.md](../04_phenotype_discovery/in_context_learning/radprompter/MODEL_CARD.md) |

## 05 — Use Cases

| Tool | Type | Status | Lab | POC | Clinical Domain | Card |
|------|------|--------|-----|-----|-----------------|------|
| ClaD | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/clad.md) |
| RadClip | placeholder | Missing | Empathi | TBD | prostate-cancer | [stub](stubs/radclip.md) |
| Prostate Cancer ChatBot | placeholder | Missing | Mayo | TBD | prostate-cancer | [stub](stubs/prostate-cancer-chatbot.md) |

---

*Last updated: 2026-04-07. Update this file when adding, contributing, or retiring tools.*
