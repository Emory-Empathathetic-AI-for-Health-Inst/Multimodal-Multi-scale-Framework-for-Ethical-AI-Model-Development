# Move Log

Chronological log of moves into `reorganized/` destination roots.

| Date | From path | To path | Operation (copy/move/merge) | By | Verification note |
|---|---|---|---|---|---|
| 2026-04-01 | `multimodal-grant-main-branch/Niffler/` | `reorganized/tools/data_quality/niffler/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/HITI-Preproc/` | `reorganized/tools/data_quality/hiti_preproc/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/RadPrompter/` | `reorganized/tools/reporting/radprompter/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |

| 2026-04-01 | `multimodal-grant-main-branch/MAYO_MOSCARD/` | `reorganized/models/multimodal/moscard/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/readmit-stgnn-main/` | `reorganized/models/multimodal/readmit_stgnn/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/VLM_SS-main/` | `reorganized/models/mammography/vlm_ss/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/mammo-implant-identifier/` | `reorganized/models/mammography/implant_identifier/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/BreastRecurrence_Transformer-main/` | `reorganized/models/nlp/breast_recurrence_transformer/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/Breast_Cancer_Treatment_Extraction-main/` | `reorganized/models/nlp/breast_treatment_extraction/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/pco_extraction_man-main/` | `reorganized/models/nlp/pco_extraction/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/recurrence_site_extraction_BioLinkBERT-main/` | `reorganized/models/nlp/recurrence_site_extraction/` | copy | assistant | Source equivalent across branches (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/Prostate Cancer Lesion Detection/` | `reorganized/models/prostate/lesion_detection/` | copy | assistant | Branch-only source (side top-level directory missing) |
| 2026-04-01 | `multimodal-grant-side-branch/feature_fusion/deep_fusion/` | `reorganized/fusion/deep/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/feature_fusion/handcrafted_feature fusion/` | `reorganized/fusion/handcrafted/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/feature_fusion/Other/` | `reorganized/fusion/other/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/2_feature_representation/radiology/` | `reorganized/feature_representation/radiology/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/2_feature_representation/pathology/` | `reorganized/feature_representation/pathology/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/2_feature_representation/EHR + Genomics/` | `reorganized/feature_representation/ehr_genomics/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/Harmonization/Radiology/` | `reorganized/tools/harmonization/radiology/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/Harmonization/Pathology/` | `reorganized/tools/harmonization/pathology/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-side-branch/Harmonization/Other/` | `reorganized/tools/harmonization/other/` | copy | assistant | `diff -qr` source vs destination status 0 |
| 2026-04-01 | `multimodal-grant-main-branch/PIQUALvsMRQy_codes/` | `reorganized/tools/harmonization/radiology/PIQUALvsMRQy_codes/` | merge | assistant | No additional copy required; already present from side and equivalent (`diff -qr --exclude=.git` status 0) |
| 2026-04-01 | `multimodal-grant-main-branch/PIQUALvsMRQy` + `multimodal-grant-side-branch/PIQUALvsMRQy` | (no destination) | merge | assistant | Empty placeholder file in both branches (`diff -q` status 0); intentionally not migrated as executable asset |