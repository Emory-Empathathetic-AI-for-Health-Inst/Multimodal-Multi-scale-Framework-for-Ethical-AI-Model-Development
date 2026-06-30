#!/bin/bash
# run_all_symmetry_features.sh
# Run the symmetry_features_extr2.py extractor on all cohorts.
#
# Script expectations (SAME for every cohort):
#   - CSV must have a column named 'patient_id'
#   - File names must be {patient_id}.nii.gz, {patient_id}.nii,
#     {patient_id}_t2w.nii.gz, or {patient_id}_t2w.nii (script tries these 4)
#   - There is NO --id_col flag
#   - There is NO --skipped_csv flag
#
# For cohorts whose CSV uses a different ID column, this script first
# pre-creates a copy of the CSV with patient_id derived appropriately.

set -e

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

BASE="/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026"
SCRIPT="${BASE}/feature_extractor/tzpz/tzpz_sym_feat.py"  # adjust if elsewhere

# =============================================================
# Pre-step: harmonize ID column to 'patient_id' for cohorts that
# use case_id / EMPI / MRI_FILE
# =============================================================
echo "==================== Pre-step: harmonize patient_id ===================="
python - <<'PY'
import pandas as pd
import os

BASE = "/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026"

# Chimera: case_id -> patient_id
src = f"{BASE}/Chimera/Chimere_prostate_clinical_data.csv"
if os.path.exists(src):
    d = pd.read_csv(src)
    if 'case_id' in d.columns and 'patient_id' not in d.columns:
        d = d.rename(columns={'case_id': 'patient_id'})
    out = f"{BASE}/Chimera/Chimere_clinical_pid.csv"
    d.to_csv(out, index=False)
    print(f"  Chimera : {len(d)} rows -> {out}")

# VA: MRI_FILE -> patient_id (strip .nii.gz so the script matches files exactly)
src = f"{BASE}/VA/CLE_MAPP_Radiology+Pathology_v1-31-2025_Deidentified2.csv"
if os.path.exists(src):
    d = pd.read_csv(src)
    if 'MRI_FILE' in d.columns:
        d['patient_id'] = d['MRI_FILE'].astype(str).str.replace('.nii.gz', '', regex=False)
    out = f"{BASE}/VA/VA_clinical_pid.csv"
    d.to_csv(out, index=False)
    print(f"  VA      : {len(d)} rows -> {out}")

# EDRN: EMPI -> patient_id (use EMPI; switch to EMPI_Anon if your filenames are anon-derived)
edrn_paths = [
    f"{BASE}/EDRN/EDRN MRI Targeted biopsy clinical data 2025.04.csv",
    f"{BASE}/EDRN/edrn_clinical.csv",
]
for src in edrn_paths:
    if os.path.exists(src):
        d = pd.read_csv(src)
        if 'EMPI' in d.columns and 'patient_id' not in d.columns:
            d = d.rename(columns={'EMPI': 'patient_id'})
        out = f"{BASE}/EDRN/EDRN_clinical_pid.csv"
        d.to_csv(out, index=False)
        print(f"  EDRN    : {len(d)} rows -> {out}")
        break
PY

# =============================================================
# PI-CAI extended  (Benign / ciPCA / csPCA) — marksheet has patient_id
# =============================================================
echo ""
echo "==================== PI-CAI extended ===================="
for grp in Benign ciPCA csPCA; do
    echo ""
    echo "--- PICCAI_extended / ${grp} ---"
    python "${SCRIPT}" \
        --nifti_pred_path "${BASE}/PICCAI_extended/${grp}/tzpz" \
        --t2w_mri_path    "${BASE}/PICCAI_extended/${grp}/t2w" \
        --excel_path      "${BASE}/PICCAI_extended/marksheet.csv" \
        --output_csv      "${BASE}/PICCAI_extended/${grp}/symmetry_features.csv"
done

# =============================================================
# Chimera (single csPCA cohort) — uses Chimere_clinical_pid.csv (created above)
# =============================================================
echo ""
echo "==================== Chimera ===================="
python "${SCRIPT}" \
    --nifti_pred_path "${BASE}/Chimera/tzpz" \
    --t2w_mri_path    "${BASE}/Chimera/t2w" \
    --excel_path      "${BASE}/Chimera/Chimere_clinical_pid.csv" \
    --output_csv      "${BASE}/Chimera/symmetry_features.csv"

# =============================================================
# Gifu  (csPCA cohort) — clinical_table_with_valid_pzvr_pv.csv has patient_id
# =============================================================
echo ""
echo "==================== Gifu ===================="
python "${SCRIPT}" \
    --nifti_pred_path "${BASE}/GIFU/tzpz/csPCA" \
    --t2w_mri_path    "${BASE}/GIFU/t2w/csPCA" \
    --excel_path      "${BASE}/GIFU/clinical_table_with_valid_pzvr_pv.csv" \
    --output_csv      "${BASE}/GIFU/symmetry_features.csv"

# =============================================================
# VA  (Benign / ciPCA / csPCA) — uses VA_clinical_pid.csv (created above)
# patient_id = MRI_FILE.nii.gz minus '.nii.gz' so it matches exact filenames
# =============================================================
echo ""
echo "==================== VA ===================="
for grp in Benign ciPCA csPCA; do
    echo ""
    echo "--- VA / ${grp} ---"
    python "${SCRIPT}" \
        --nifti_pred_path "${BASE}/VA/${grp}/tzpz" \
        --t2w_mri_path    "${BASE}/VA/${grp}/t2w" \
        --excel_path      "${BASE}/VA/VA_clinical_pid.csv" \
        --output_csv      "${BASE}/VA/${grp}/symmetry_features.csv"
done

# =============================================================
# EDRN — uses EDRN_clinical_pid.csv (created above)
# =============================================================
echo ""
echo "==================== EDRN ===================="
python "${SCRIPT}" \
    --nifti_pred_path "${BASE}/EDRN/tzpz" \
    --t2w_mri_path    "${BASE}/EDRN/t2w" \
    --excel_path      "${BASE}/EDRN/EDRN_clinical_pid.csv" \
    --output_csv      "${BASE}/EDRN/symmetry_features.csv"

echo ""
echo "============================================================"
echo "All symmetry feature extractions complete."
echo "============================================================"
echo ""
echo "Outputs:"
echo "  ${BASE}/PICCAI_extended/Benign/symmetry_features.csv"
echo "  ${BASE}/PICCAI_extended/ciPCA/symmetry_features.csv"
echo "  ${BASE}/PICCAI_extended/csPCA/symmetry_features.csv"
echo "  ${BASE}/Chimera/symmetry_features.csv"
echo "  ${BASE}/GIFU/symmetry_features.csv"
echo "  ${BASE}/VA/Benign/symmetry_features.csv"
echo "  ${BASE}/VA/ciPCA/symmetry_features.csv"
echo "  ${BASE}/VA/csPCA/symmetry_features.csv"
echo "  ${BASE}/EDRN/symmetry_features.csv"