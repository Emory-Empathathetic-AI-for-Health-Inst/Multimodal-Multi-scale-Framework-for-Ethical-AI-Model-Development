# Swin Transformer-Based Multimodal and Multi-Region Data Fusion Framework for Predicting BCR Outcomes

This repository implements a Swin Transformer-based multimodal and multi-region data fusion framework for predicting biochemical recurrence (BCR) outcomes in prostate cancer.

## Overview

The framework is designed to integrate complementary information from multiple imaging-derived sources and anatomical or tumor-relevant regions. It combines radiology-derived and pathology-derived features using an attention-based fusion strategy to improve BCR outcome prediction.

The model supports multi-slice inputs and feature-level fusion, allowing the integration of radiomic, pathomic, or combined feature representations. In the current setup, the framework is configured for the Chimera prostate cancer BCR prediction dataset using a 4-slice input setting.

## Key Features

- Swin Transformer-based feature representation
- Multimodal data fusion
- Multi-region feature integration
- Attention-based fusion strategy
- Support for radiomic/pathomic feature inputs
- Configurable number of input slices
- Binary outcome prediction for BCR-related tasks

## Example Training Command

```bash
python main_nocv.py \
  --dataroot /path/to/Chimere \
  --checkpoints_dir /path/to/checkpoints \
  --exp_name chimere_bcr_4slice \
  --gpu_ids 0 \
  --n_epochs 100 \
  --feature_type raptomic \
  --act_type relu \
  --fusion_type fused_attention \
  --task grade \
  --batch_size 2 \
  --lr 0.0002 \
  --dropout 0.25 \
  --dim_out 2 \
  --feature_size 192 \
  --print_freq 1 \
  --num_slices 4
```

## Main Parameters

| Parameter | Description |
|---|---|
| `--dataroot` | Root directory of the dataset |
| `--checkpoints_dir` | Directory where model checkpoints and outputs are saved |
| `--exp_name` | Experiment name |
| `--gpu_ids` | GPU ID used for training |
| `--n_epochs` | Number of training epochs |
| `--feature_type` | Type of input feature representation |
| `--act_type` | Activation function used in the model |
| `--fusion_type` | Feature fusion strategy |
| `--task` | Prediction task specified in the code |
| `--batch_size` | Training batch size |
| `--lr` | Learning rate |
| `--dropout` | Dropout rate |
| `--dim_out` | Number of output classes |
| `--feature_size` | Feature embedding size |
| `--print_freq` | Frequency of printed training updates |
| `--num_slices` | Number of input slices used by the model |

## Output

Model checkpoints, training logs, and prediction outputs are saved under the specified checkpoint directory:

```bash
/path/to/checkpoints/chimere_bcr_4slice
```

## Notes

Before running the training script, make sure that:

- The required Conda environment and dependencies are installed.
- The dataset path is correctly specified.
- The input data structure matches the expected format of `main_nocv.py`.
- GPU settings are properly configured.
- The selected `--task` argument matches the task names supported by the code.

If the task is specifically BCR prediction, consider replacing `--task grade` with a BCR-specific task name only if it is supported by the code.
