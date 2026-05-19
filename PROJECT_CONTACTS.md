# Project Contacts

**Purpose:** Use this document at the next project meeting to assign a named point of contact (POC) for every tool in the MEFINDER framework — both code already in the repository and tools still to be contributed.

**POC responsibilities:**

- For tools already here: first point of escalation for questions, code reviews, and maintenance
- For tools not yet here: accountable for contributing the code to the repository at the path listed under _Target Path_

**Status key:** `Implemented` — substantive, runnable code present | `Partial` — code present but incomplete relative to roadmap | `Missing` — no code in repository yet

---

## Part 1 — Code Already in the Repository

### 01_data_harmonization / radiology

| Tool                              | Repo Path                                                   | Lab     | Status      | POC                  | Notes                                                                                              |
| --------------------------------- | ----------------------------------------------------------- | ------- | ----------- | -------------------- | -------------------------------------------------------------------------------------------------- |
| Niffler                           | `01_data_harmonization/radiology/Niffler/`                  | HITI    | Implemented | Beatrice Brown-Mulry | DICOM PACS/RIS retrieval, metadata extraction, anonymization                                       |
| DICOM PreProcessor (HITI-Preproc) | `01_data_harmonization/radiology/HITI-Preproc/`             | HITI    | Implemented | Beatrice Brown-Mulry | Lightweight DICOM preprocessing package (`pip install hiti-preproc`)                               |
| RadQy                     | `01_data_harmonization/radiology/RadQy-master/`             | Empathi    | Partial     | Yamlak Bogale           | QC metrics and interactive dashboard present |
| MRQy (experiments)                | `01_data_harmonization/radiology/PIQUALvsMRQy_codes/`       | Empathi | Partial     | Yamlak Bogale          | PI-QUAL vs MRQy comparison code present; not yet a packaged standalone MRQy tool — see Part 2      |
| Mammography Implant Detector      | `01_data_harmonization/radiology/mammo_implant_identifier/` | HITI    | Implemented | Beatrice Brown-Mulry | Deep learning classifier with pre-trained weights; preprocessing step for mammography pipelines    |

### 01_data_harmonization / ehr_nlp

| Tool                             | Repo Path                                                      | Lab  | Status      | POC | Notes                                                                                                                                  |
| -------------------------------- | -------------------------------------------------------------- | ---- | ----------- | --- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Breast Recurrence Transformer    | `01_data_harmonization/ehr_nlp/breast_recurrence_transformer/` | Mayo | Implemented | Madhu Sikha | BERT-based NLP pipeline to identify recurrence occurrence and timing from clinical notes                                               |
| Recurrence Site Extraction       | `01_data_harmonization/ehr_nlp/recurrence_site_extraction/`    | Mayo | Implemented | Madhu Sikha | BioLinkBERT extraction of distant recurrence sites; depends on Breast Recurrence Transformer output                                    |
| Breast Treatment Extraction      | `01_data_harmonization/ehr_nlp/breast_treatment_extraction/`   | Mayo | Implemented | Madhu Sikha | Two-phase (rule-based + BioGPT) pipeline for structured treatment timeline reconstruction                                              |
| PCO Extraction (AI-LAD adjacent) | `01_data_harmonization/ehr_nlp/pco_extraction/`                | Mayo | Partial     | Madhu Sikha | Fine-tuned GPT-2/BioGPT for patient-reported adverse effect extraction; explicit AI-LAD tool boundary not yet established — see Part 2 |

### 01_data_harmonization / pathology

| Tool                             | Repo Path                                                      | Lab  | Status      | POC | Notes                                                                                                                                  |
| -------------------------------- | -------------------------------------------------------------- | ---- | ----------- | --- | -------------------------------------------------------------------------------------------------------------------------------------- |
| HistoQC | `01_data_harmonization/pathology/HistoQC/` | Empathi | Implemented | Jackson Jacobs | H&E slide quality control; archive present but not extracted or validated as runnable          |

### 02_feature_extraction / deep_features

| Tool                                | Repo Path                                                        | Lab     | Status      | POC | Notes                                                                                         |
| ----------------------------------- | ---------------------------------------------------------------- | ------- | ----------- | --- | --------------------------------------------------------------------------------------------- |
| Invisible Prostate Cancer Detection | `02_feature_extraction/deep_features/prostate_lesion_detection/` | Empathi | Implemented | ??? | nnU-Net lesion detection and segmentation on prostate MRI; trained on PI-CAI and Prostate-158 |

### 02_feature_extraction / handcrafted_features 

| Tool                                | Repo Path                                                        | Lab     | Status      | POC | Notes                                                                                         |
| ----------------------------------- | ---------------------------------------------------------------- | ------- | ----------- | --- | --------------------------------------------------------------------------------------------- |
| pZVR Biomarker | `02_feature_extraction/handcrafted_features/pZVR/` | Empathi | Implemented | Zelin Zhang | MRI peripheral-zone volume ratio biomarker                                   |

### 03_multimodal_embedding / deep_joint_embedding

| Tool                              | Repo Path                                                              | Lab     | Status      | POC | Notes                                                                                                                                                             |
| --------------------------------- | ---------------------------------------------------------------------- | ------- | ----------- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VLM for Mammogram (mammo_vlm_ss)  | `03_multimodal_embedding/deep_joint_embedding/mammo_vlm_ss/`           | Mayo    | Implemented | Gokul Ramasamy | ALBEF + MedCLIP VLM adaptation with mini-batch selective sampling; MICCAI 2024                                                                                    |
| SMuRF                             | `03_multimodal_embedding/deep_joint_embedding/SMuRF_MultiModal_OPSCC/` | Empathi | Implemented | Bolin Song | Swin Transformer co-attention fusion of radiology and pathology for OPSCC outcome prediction; EBioMedicine                                                        |
| MOSCARD (Computational Debiasing) | `03_multimodal_embedding/deep_joint_embedding/moscard/`                | Mayo    | Partial     | Jialu Pi | CXR + ECG causal fusion with structural causal models; causal/deconfounding logic embedded in model — standalone debiasing toolkit not yet separated — see Part 2 |

### 03_multimodal_embedding / temporal_fusion

| Tool                                            | Repo Path                                                | Lab     | Status      | POC | Notes                                                                                                                                      |
| ----------------------------------------------- | -------------------------------------------------------- | ------- | ----------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Graph-based Multimodal Modeling (readmit_stgnn) | `03_multimodal_embedding/temporal_fusion/readmit_stgnn/` | Mayo    | Implemented | Amara Tariq | MM-STGNN fusing longitudinal imaging and EHR data; IEEE JBHI 2023                                                   |
| MuTriM                                          | `03_multimodal_embedding/temporal_fusion/MuTriM_breast/` | Empathi | Implemented | Bolin Song | Multiscale deep learning model integrating longitudinal radiomics and pathomics for breast cancer recurrence and NAC benefit; under review |

### 03_multimodal_embedding / engineered_fusion

| Tool                                    | Repo Path                                                                                                               | Lab     | Status  | POC | Notes                                                                                                                                        |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------- | ------- | --- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Rad-Path Prostate Recurrence Classifier | `03_multimodal_embedding/engineered_fusion/An-Integrated-Radiology-Pathology-ML-Classifier-post-Radical-Prostatectomy/` | Empathi | Partial | Rakesh Shiradkar | Classical ML combining radiological and pathological features for post-prostatectomy BCR; related to ClaD/RadClip roadmap items — see Part 2 |

### 04_phenotype_discovery / in_context_learning

| Tool        | Repo Path                                                 | Lab  | Status      | POC             | Notes                                                                                                 |
| ----------- | --------------------------------------------------------- | ---- | ----------- | --------------- | ----------------------------------------------------------------------------------------------------- |
| RadPrompter | `04_phenotype_discovery/in_context_learning/radprompter/` | HITI | Implemented | Bardia Khosravi | TOML-driven LLM prompting framework for biomedical in-context learning; PyPI installable; 6 tutorials |

---

## Part 2 — Tools Not Yet in the Repository

A POC assigned here is responsible for contributing the code to the repository at the target path shown.

#### Prostate Tooling

| Tool                        | Lab     | Target Path                            | POC | Notes                                                                        |
| --------------------------- | ------- | -------------------------------------- | --- | ---------------------------------------------------------------------------- |
| Prostate Cancer ChatBot     | Mayo    | `05_use_cases/prostate_cancer/`        | Amara Tariq | Clinical communication and summarization workflow                            |

#### Data Quality & Preprocessing

| Tool                       | Lab     | Target Path                        | POC                  | Notes                                                                                          |
| -------------------------- | ------- | ---------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------- |
| Anomaly Detection          | Mayo    | `01_data_harmonization/radiology/` | Gokul Ramasamy | OOD detection for safe cross-institution deployment; also completes the RadIQ FM-OOD component |
| ROI-Lift                   | HITI    | `01_data_harmonization/radiology/` | Beatrice Brown-Mulry | Converts 2D ROIs into 3D ROIs on spatially aligned DBT images                                 |
| Atlas                      | HITI    | `01_data_harmonization/radiology/` | Jahanzaib Malik | Dataset embedding exploration tool for data curation and subgroup identification               |

#### Reporting & Reusable Infrastructure

| Tool                                              | Lab  | Target Path                            | POC | Notes                                                                                                                   |
| ------------------------------------------------- | ---- | -------------------------------------- | --- | ----------------------------------------------------------------------------------------------------------------------- |
| Computational Debiasing Toolkit (standalone)      | Mayo | `01_data_harmonization/federated/` | Jialu Pi / Vedant Joshi | Debiasing and confounding-correction logic is currently embedded in MOSCARD; needs separation into a reusable framework |

