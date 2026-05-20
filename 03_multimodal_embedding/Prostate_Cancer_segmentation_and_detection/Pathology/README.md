# PCaMEx: Mixture-of-Experts Framework for Prostate Cancer Detection on H&E Whole-Slide Images

Developed by Zelin Zhang, Madabhushi Lab, Emory University.

## Overview

This repository contains the inference pipeline for a pathology-based Mixture-of-Experts (MoE) framework for automatic prostate cancer detection on whole-slide histopathology images (WSIs).

The framework integrates multiple pretrained image foundation/backbone models to capture complementary histomorphologic representations from prostate pathology images.

The current implementation supports multi-backbone feature extraction and adaptive expert fusion for WSI-level prostate cancer analysis.

---

## Related Work

This work was presented at AUA 2026:

Zhang Z, et al.  
**PCaMEx: A Dynamic Mixture-of-Experts Framework for Prostate Cancer Detection on Whole-Slide Images**

AUA 2026 Abstract Link:  
https://www.auajournals.org/doi/10.1097/01.JU.0001191740.08299.b6.25

---

## Main Pipeline

Main inference script:

```text
run_pipeline.py
```

---

## Key Arguments

| Argument | Default | Description |
|---|---:|---|
| `--data_root` | `./VA2024/WSI` | Root directory containing input whole-slide images |
| `--level_10x` | `1` | OpenSlide level corresponding to 10× magnification |
| `--tile_size_10x` | `512` | Patch size at 10× magnification |
| `--max_threads` | `16` | Number of CPU threads used for WSI processing |
| `--device` | `cuda:0` | CUDA device used for inference |

---

## Example Usage

```bash
python run_pipeline.py \
  --data_root ./VA2024/WSI \
  --level_10x 1 \
  --tile_size_10x 512 \
  --max_threads 16 \
  --device cuda:0
```

---

## Dependencies

Main dependencies include:

```text
Python
PyTorch
OpenSlide
OpenCV
Pillow
NumPy
Pandas
tqdm
```

---

## Model Weights

Due to the large size of the trained checkpoint files, pretrained model weights are not directly distributed through this repository.

Researchers interested in running the complete inference pipeline may contact the developer for internal collaborative research access.

Contact:

```text
Zelin Zhang 
zzha962@emory.edu
```

---

## Docker Deployment

A packaged Docker version of the full pipeline will be released in the future to support streamlined deployment, reproducibility, and cross-platform inference.

---

## Notes

This repository is currently intended for internal collaborative research use.

Please contact the developer before external redistribution, deployment, or integration into external collaborative studies.

---

## Acknowledgement

Developed in the Madabhushi Lab at Emory University.