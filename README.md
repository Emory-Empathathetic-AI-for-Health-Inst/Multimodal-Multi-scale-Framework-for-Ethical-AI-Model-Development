# MEFINDER - Multimodal Tooling Repository

## Overview

MEFINDER (*Multimodal Fusion Initiative for Novel Disease Phenotype Discovery and Population-Specific Risk Prediction*) is an NCI U01-funded collaboration led by Dr. Judy Gichoya at Emory University.

This repository contains the open-source implementation of the MEFINDER framework: a modular, multi-institutional pipeline for integrating radiology imaging, digital pathology, and clinical/EHR data to discover biologically relevant patient phenotypes and enable phenotype-specific cancer risk prediction.

The framework is validated on two clinical use cases:
- Hormone receptor-positive (HR+) breast cancer — recurrence risk stratification and prediction of adjuvant therapy benefit.
- High-risk recurrent prostate cancer — biochemical recurrence prediction and identification of patients likely to benefit from chemotherapy.

## Motivation

Patients with similar clinical diagnoses frequently experience markedly different outcomes. Current molecular assays—such as Decipher (prostate, ~$3,400) and Oncotype DX (breast)—provide valuable prognostic information but are expensive and inaccessible in many settings. MEFINDER aims to develop open, computationally derived counterparts that combine the complementary information in radiology images, pathology slides, and clinical records to improve risk stratification across diverse patient populations.

## Collaborating Institutions

| Institution         | Role             | Key Dataset(s)                                                     |
| ------------------- | ---------------- | ------------------------------------------------------------------ |
| Emory University    | Lead Institution | EMBED v2 (260,815 patients, ~1M exams); EPIP (~7,500 patients)     |
| Mayo Clinic         | Co-investigator  | Mayo Clinic Biobank (75,000+ patients, 10-15 yr follow-up)         |
| Stanford University | Co-investigator  | Stanford Prostate Cohort                                           |
| Indiana University  | Co-investigator  | Breast & Prostate Imaging Cohorts                                  |
| VA Medical Center   | Collaborator     | VA Biparametric MRI (387 patients, pathology digitization ongoing) |
| TCIA / RTOG / EDRN  | Public Datasets  | PICCAI, RTOG Clinical Trial Data, TCIA Collections                 |
