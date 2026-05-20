# Swin Transformer-based MultiModal and Multi-Region Data Fusion Framework to Predict BCR Outcomes
Sample bash file:
#!/bin/bash
#SBATCH --job-name=smurf_bcr_4slice
#SBATCH --account=ext_em-amadabhushi9-paid
#SBATCH --partition=gpu-rtx6000,gpu-a100,gpu-h100,gpu-h200,gpu-l40s
#SBATCH --qos=embers
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=smurf_bcr_4slice_%j.out

set -euo pipefail

CONDA_SH="/storage/home/hcoda1/1/kozyoruk3/scratch/miniconda3/etc/profile.d/conda.sh"
ENV_NAME="hipt_pip"
REPO_DIR="/storage/scratch1/1/kozyoruk3/SMuRF_MultiModal_OPSCC_4_8"
DATA_ROOT="/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere"

source "${CONDA_SH}"
conda activate "${ENV_NAME}"

cd "${REPO_DIR}"

echo "============================================"
echo "Job started on $(hostname)"
echo "SLURM job ID: ${SLURM_JOB_ID}"
echo "Start time: $(date)"
echo "============================================"

echo "Python: $(which python)"
python --version
nvidia-smi || true

python - <<'PY'
import models
print("ACTIVE MODELS FILE:", models.__file__)
from models import Model
import inspect
print(inspect.getsource(Model.__init__))
PY

python main_nocv.py \
  --dataroot "${DATA_ROOT}" \
  --checkpoints_dir "${REPO_DIR}/checkpoints_4slice3" \
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

echo "============================================"
echo "End time: $(date)"
echo "============================================"
