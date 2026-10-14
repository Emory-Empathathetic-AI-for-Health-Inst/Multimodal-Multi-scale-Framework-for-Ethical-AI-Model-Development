# BCR Multimodal Survival Inference

This repository runs the complete biochemical recurrence (BCR) survival-inference
workflow for prostate cancer. It combines whole-slide image (WSI) pathology features,
MRI features, and a trained multimodal fusion model to produce patient-level risk
scores.

The pipeline is launched from `main.py`. Raw data remains in its existing location;
generated files are written to a separate output directory.

## Pipeline overview

```text
Whole-slide images
  -> patch extraction
  -> stain normalization
  -> UNI2-h feature embedding
  -> cancer classification and heatmaps
  -> cancer-patch filtering
  -> pathology MIL vector
                                      -> multimodal fusion -> BCR risk score
MRI patient folders
  -> MRI foundation-model features
```

## 1. Requirements

- Python 3.10-3.12
- A CUDA-capable GPU is strongly recommended
- Sufficient storage for WSI patches and embeddings
- Access to [MahmoodLab/UNI2-h](https://huggingface.co/MahmoodLab/UNI2-h), unless a
  local UNI2-h checkpoint is supplied

## 2. Install the environment

Open a terminal in the repository root—the folder containing `main.py`.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\setup.ps1
```

### Linux, macOS, WSL, or Git Bash

```bash
python -m venv .venv
source .venv/bin/activate
bash setup.sh
```

## 3. Check the required model files

```text
checkpoints/
├── pathology/
│   ├── prostate_uni2_model.joblib
│   └── best_mil_chimera_surv.pth
└── fusion/
    └── best_fusion_chimera_surv.pth

MRI_CORE_FEATURE_EXTRACTION/
├── Gland_model/
│   └── Finetuneglandmodel.pt
└── weights/
    ├── mri_foundation.pth
    └── sam_vit_b_01ec64.pth

data/
└── reference/
    └── reference-patch.png
```

If the MRI checkpoints are absent, download each file and copy it to the exact path
shown below:

| Checkpoint | Download | Copy to |
| --- | --- | --- |
| MRI foundation model | [mri_foundation.pth](https://github.com/Emory-Empathathetic-AI-for-Health-Inst/Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development/releases/download/mri-core-checkpoints-v1.0/mri_foundation.pth) | `MRI_CORE_FEATURE_EXTRACTION/weights/mri_foundation.pth` |
| SAM ViT-B model | [sam_vit_b_01ec64.pth](https://github.com/Emory-Empathathetic-AI-for-Health-Inst/Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development/releases/download/mri-core-checkpoints-v1.0/sam_vit_b_01ec64.pth) | `MRI_CORE_FEATURE_EXTRACTION/weights/sam_vit_b_01ec64.pth` |
| MRI gland-segmentation model | [Finetuneglandmodel.pt](https://github.com/Emory-Empathathetic-AI-for-Health-Inst/Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development/releases/download/mri-core-checkpoints-v1.0/Finetuneglandmodel.pt) | `MRI_CORE_FEATURE_EXTRACTION/Gland_model/Finetuneglandmodel.pt` |

Create the destination directories if they do not already exist. The gland checkpoint
must retain the exact filename `Finetuneglandmodel.pt`; the MRI extraction code looks
for it at `MRI_CORE_FEATURE_EXTRACTION/Gland_model/Finetuneglandmodel.pt` by default.

Use Git LFS or release assets when publishing large weights on GitHub.

## 4. Obtain and configure a Hugging Face token

UNI2-h is downloaded from Hugging Face on the first pathology run:

1. [Create a Hugging Face account](https://huggingface.co/join), or sign in.
2. Use a verified institutional email; personal-email requests may be denied.
3. Open [MahmoodLab/UNI2-h](https://huggingface.co/MahmoodLab/UNI2-h).
4. Agree to the conditions and request access using your full name, complete
   affiliation, and research purpose. Wait for approval.
5. Open [Hugging Face Access Tokens](https://huggingface.co/settings/tokens) and
   select **Create new token**.
6. Name it—for example, `bcr-multimodal`—and choose **Read**, or choose
   **Fine-grained** with permission to read `MahmoodLab/UNI2-h`.
7. Create and copy the token. It normally begins with `hf_`.
8. Set it in the terminal used to run the pipeline.

### Windows PowerShell

```powershell
$env:HF_TOKEN = "hf_your_actual_token_here"
```

### Linux, macOS, WSL, Git Bash, or HPC

```bash
export HF_TOKEN="hf_your_actual_token_here"
```

Set the variable again in new terminals and inside submitted job scripts. Never
commit or share the token. After the initial download, later runs reuse the cache.

## 5. Prepare the input data

```text
prostate_data/
├── 1003_1.tif
├── 1010_1.svs
├── 1003/
│   ├── 1003_0001_t2w.mha
│   ├── 1003_0001_adc.mha
│   ├── 1003_0001_hbv.mha
│   └── 1003_0001_mask.mha
└── 1010/
    └── ...
```

WSI formats: `.svs`, `.ndpi`, `.tif`, and `.tiff`. WSI files must be directly inside
the WSI directory. MRI formats: `.nii`, `.nii.gz`, `.mha`, and `.mhd`. Each MRI case
must be in a patient folder directly inside the MRI directory.

Identifiers must match across modalities. For example, pathology case `1003_1` is
matched to MRI patient `1003` during fusion.

## 6. Validate the inputs

Use `--dry-run` before a long job:

```bash
python main.py \
  --data-dir "/path/to/data" \
  --wsi-dir "/path/to/slides" \
  --mri-dir "/path/to/mri" \
  --dry-run
```

A successful check ends with:

```text
Dry run successful: inputs were discovered and no processing was started.
```

## 7. Run the complete end-to-end pipeline

This is the recommended workflow for collaborators who want to run everything—from
raw WSI and MRI inputs through survival evaluation—in one job.

### RadPath evaluation: copy-and-run command

From the repository root, activate the environment and set the token:

```bash
source .venv/bin/activate
export HF_TOKEN="hf_your_actual_token_here"
```

Then run:

```bash
python main.py \
  --data-dir "/N/project/rad-path/Histopathology_Projects/NIH-RadPath-Evaluation" \
  --wsi-dir "/N/project/rad-path/Histopathology_Projects/NIH-RadPath-Evaluation/WSI" \
  --mri-dir "/N/project/rad-path/Histopathology_Projects/NIH-RadPath-Evaluation/MRI" \
  --output-dir "/N/project/rad-path/Histopathology_Projects/NIH-RadPath-Evaluation/Output_After_Modifying" \
  --clinical-csv "/N/project/rad-path/Histopathology_Projects/NIH-RadPath-Evaluation/clinical_data_template.csv" \
  --stop-after evaluate \
  --processes 1 \
  --threads-per-process 4 \
  --batch-size 8 \
  --precision float16 \
  --hf-token "$HF_TOKEN"
```

Place the activation, token export, and command in `nih_evaluation_bcr.slurm`. A
submitted SLURM job may not inherit variables from the interactive login shell.

Do not use the literal text `"HF_TOKEN"`. Set the variable to the real token and keep
`"$HF_TOKEN"` in the command so its value is read at runtime.

### What this command does

It runs all ten stages:

```text
extract -> normalize -> embed -> classify -> heatmap -> filter
        -> mil -> mri -> fusion -> evaluate
```

- `--data-dir` identifies the overall dataset and is recorded in the manifest.
- `--wsi-dir` points to WSI files.
- `--mri-dir` points to one subfolder per MRI patient.
- `--output-dir` receives all patches, features, predictions, logs, and the manifest.
- `--clinical-csv` provides `patient_id`, `time`, and `event` for evaluation.
- `--stop-after evaluate` includes evaluation; otherwise the default ends at fusion.
- `--processes 1` and `--threads-per-process 4` configure WSI extraction.
- `--batch-size 8` embeds eight patches per batch.
- `--precision float16` reduces GPU memory usage and requires a compatible GPU.

### Monitoring and resuming

Progress is written to:

```text
Output_After_Modifying/
├── pipeline_manifest.json
└── logs/
    ├── extract.stdout.log
    ├── extract.stderr.log
    └── <stage>.stdout.log / <stage>.stderr.log
```

If interrupted, submit the identical command with the same output directory.
Completed stages with valid outputs are skipped, and execution resumes at the first
incomplete stage.

For data stored under one folder:

```bash
python main.py \
  --data-dir "/path/to/prostate_data" \
  --clinical-csv "/path/to/clinical_info.csv" \
  --stop-after evaluate
```

## 8. Partial runs

```bash
# Two-patch-per-slide smoke test
python main.py --data-dir "/path/to/data" --sample-count 2 --stop-after extract

# Continue at embedding
python main.py --data-dir "/path/to/data" --start-at embed

# Pathology only
python main.py --data-dir "/path/to/data" --stop-after mil

# Deliberately rerun selected stages
python main.py --data-dir "/path/to/data" --force
```

Use `--start-at` only when earlier outputs already exist in the selected output
directory. See all options with `python main.py --help`.

## 9. Outputs

```text
<output-dir>/
├── patches/
├── heatmaps/
├── pathology/
│   ├── patch_embeddings.h5
│   ├── patch_predictions.csv
│   ├── cancer_embeddings.h5
│   └── pathology_vectors.pt
├── mri/
├── fusion/
│   ├── fusion_predictions.csv
│   ├── fusion_z_fused.npy
│   ├── fusion_z_path.npy
│   ├── fusion_z_mri.npy
│   ├── aggregated_pathology_vectors.pt
│   └── evaluation/
├── logs/
└── pipeline_manifest.json
```

The `risk` column in `fusion_predictions.csv` is a Cox proportional-hazards log-risk
score. Higher values mean higher predicted BCR risk. It ranks patients and is not a
probability.

## 10. Clinical CSV

```text
patient_id,time,event
1003,3.2,1
1010,5.8,0
```

- `patient_id`: identifier matched to predictions
- `time`: follow-up time, typically in years
- `event`: `1` for recurrence or `0` for censoring

Evaluation writes the C-index, log-rank result, merged table, and Kaplan-Meier plot
under `<output-dir>/fusion/evaluation/`.

## Testing

```bash
python -m unittest discover -s tests -v
```

## Notes and troubleshooting

- The patch workflow assumes 20x WSIs. Other magnifications may require resampling.
- Do not reuse an output directory with different input data.
- On failure, inspect `<output-dir>/logs/<stage>.stderr.log`, correct the problem, and
  rerun the same command.
- Duplicate WSI stems are rejected because they produce ambiguous patch identifiers.
- Clinical labels are optional for inference but required for evaluation.
