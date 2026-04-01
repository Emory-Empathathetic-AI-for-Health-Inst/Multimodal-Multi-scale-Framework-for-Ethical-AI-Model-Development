# Source Map

Map each unified destination to original source location(s).

| Unified destination path | Source path(s) | Branch origin (Main/Side/Both) | Decision (copied/merged/canonicalized) | Notes |
|---|---|---|---|---|
| `unified/tools/data_quality/niffler/` | `multimodal-grant-main-branch/Niffler/` + `multimodal-grant-side-branch/Niffler/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/tools/data_quality/hiti_preproc/` | `multimodal-grant-main-branch/HITI-Preproc/` + `multimodal-grant-side-branch/HITI-Preproc/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/tools/reporting/radprompter/` | `multimodal-grant-main-branch/RadPrompter/` + `multimodal-grant-side-branch/RadPrompter/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |

| `unified/models/multimodal/moscard/` | `multimodal-grant-main-branch/MAYO_MOSCARD/` + `multimodal-grant-side-branch/MAYO_MOSCARD/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/multimodal/readmit_stgnn/` | `multimodal-grant-main-branch/readmit-stgnn-main/` + `multimodal-grant-side-branch/readmit-stgnn-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/mammography/vlm_ss/` | `multimodal-grant-main-branch/VLM_SS-main/` + `multimodal-grant-side-branch/VLM_SS-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/mammography/implant_identifier/` | `multimodal-grant-main-branch/mammo-implant-identifier/` + `multimodal-grant-side-branch/mammo-implant-identifier/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/nlp/breast_recurrence_transformer/` | `multimodal-grant-main-branch/BreastRecurrence_Transformer-main/` + `multimodal-grant-side-branch/BreastRecurrence_Transformer-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/nlp/breast_treatment_extraction/` | `multimodal-grant-main-branch/Breast_Cancer_Treatment_Extraction-main/` + `multimodal-grant-side-branch/Breast_Cancer_Treatment_Extraction-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/nlp/pco_extraction/` | `multimodal-grant-main-branch/pco_extraction_man-main/` + `multimodal-grant-side-branch/pco_extraction_man-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/nlp/recurrence_site_extraction/` | `multimodal-grant-main-branch/recurrence_site_extraction_BioLinkBERT-main/` + `multimodal-grant-side-branch/recurrence_site_extraction_BioLinkBERT-main/` | Both | canonicalized (copied from main after equivalence check) | `diff -qr --exclude=.git` status 0 |
| `unified/models/prostate/lesion_detection/` | `multimodal-grant-main-branch/Prostate Cancer Lesion Detection/` | Main | copied (branch-only source) | Side branch top-level directory missing |
| `unified/fusion/deep/` | `multimodal-grant-side-branch/feature_fusion/deep_fusion/` | Side | copied (branch-only source) | Preserved full deep_fusion contents |
| `unified/fusion/handcrafted/` | `multimodal-grant-side-branch/feature_fusion/handcrafted_feature fusion/` | Side | copied (branch-only source) | Directory name normalized at destination only |
| `unified/fusion/other/` | `multimodal-grant-side-branch/feature_fusion/Other/` | Side | copied (branch-only source) | Preserved as side-provided auxiliary content |
| `unified/feature_representation/radiology/` | `multimodal-grant-side-branch/2_feature_representation/radiology/` | Side | copied (branch-only source) | |
| `unified/feature_representation/pathology/` | `multimodal-grant-side-branch/2_feature_representation/pathology/` | Side | copied (branch-only source) | |
| `unified/feature_representation/ehr_genomics/` | `multimodal-grant-side-branch/2_feature_representation/EHR + Genomics/` | Side | copied (branch-only source) | Destination naming normalized for no-space path |
| `unified/tools/harmonization/radiology/` | `multimodal-grant-side-branch/Harmonization/Radiology/` | Side | copied (branch-only source) | Includes nested Niffler_2, HITI-Preproc, PIQUALvsMRQy_codes, RadQy-master |
| `unified/tools/harmonization/pathology/` | `multimodal-grant-side-branch/Harmonization/Pathology/` | Side | copied (branch-only source) | Includes HistoQC archive artifact |
| `unified/tools/harmonization/other/` | `multimodal-grant-side-branch/Harmonization/Other/` | Side | copied (branch-only source) | |