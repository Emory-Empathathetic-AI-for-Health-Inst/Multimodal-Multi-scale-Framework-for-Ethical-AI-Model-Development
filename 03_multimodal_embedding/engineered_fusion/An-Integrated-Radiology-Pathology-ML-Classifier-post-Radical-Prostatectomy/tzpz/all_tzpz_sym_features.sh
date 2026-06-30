#!/bin/bash
# run_all_tzpz_symmetry.sh
# Run tzpz_symmetry_features extraction for GIFU, Chimera, PICCAI (all 3 groups), VA (all 3 groups)
#
# Three script variants are used depending on each cohort's CSV ID convention:
#   tzpz_claude.py            — generic, auto-detects patient_id (PICCAI extended)
#   tzpz_claude_chimera.py    — robust file matching with nnUNet _0000 suffix (Chimera, Gifu)
#   tzpz_claude_va.py         — uses MRI_FILE column directly as full filename (VA)
#
# Author: Kutsev B. Ozyoruk

set -e

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

BASE="/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026"
SCRIPTS="${BASE}/feature_extractor/tzpz"   # adjust if your scripts live elsewhere

# =============================================================
# PI-CAI extended  (Benign / ciPCA / csPCA)
# Script: tzpz_claude.py — auto-detects patient_id from marksheet.csv
# =============================================================
echo "==================== PI-CAI extended ===================="
for grp in Benign ciPCA csPCA; do
    echo ""
    echo "--- PICCAI_extended / ${grp} ---"
    python "${SCRIPTS}/tzpz_claude.py" \
        --t2w_dir     "${BASE}/PICCAI_extended/${grp}/t2w" \
        --tzpz_dir    "${BASE}/PICCAI_extended/${grp}/tzpz" \
        --excel_path  "${BASE}/PICCAI_extended/marksheet.csv" \
        --output_csv  "${BASE}/PICCAI_extended/${grp}/tzpz_symmetry_features.csv"
done

# =============================================================
# Chimera (single csPCA cohort, surgical)
# Script: tzpz_claude_chimera.py — uses case_id (auto-detected)
# =============================================================
echo ""
echo "==================== Chimera ===================="
python "${SCRIPTS}/tzpz_claude_chimera.py" \
    --t2w_dir     "${BASE}/Chimera/t2w" \
    --tzpz_dir    "${BASE}/Chimera/tzpz" \
    --excel_path  "${BASE}/Chimera/Chimere_prostate_clinical_data.csv" \
    --output_csv  "${BASE}/Chimera/tzpz_symmetry_features.csv" \
    --skipped_csv "${BASE}/Chimera/tzpz_symmetry_features_skipped.csv"

# =============================================================
# Gifu (csPCA cohort, surgical)
# Script: tzpz_claude_chimera.py — uses patient_id (auto-detected)
# =============================================================
echo ""
echo "==================== Gifu ===================="
python "${SCRIPTS}/tzpz_claude_chimera.py" \
    --t2w_dir     "${BASE}/GIFU/t2w/csPCA" \
    --tzpz_dir    "${BASE}/GIFU/tzpz/csPCA" \
    --excel_path  "${BASE}/GIFU/clinical_table_with_valid_pzvr_pv.csv" \
    --output_csv  "${BASE}/GIFU/tzpz_symmetry_features.csv" \
    --skipped_csv "${BASE}/GIFU/tzpz_symmetry_features_skipped.csv"

# =============================================================
# VA (Benign / ciPCA / csPCA)
# Script: tzpz_claude_va.py — uses MRI_FILE column directly
# =============================================================
echo ""
echo "==================== VA ===================="
for grp in Benign ciPCA csPCA; do
    echo ""
    echo "--- VA / ${grp} ---"
    python "${SCRIPTS}/tzpz_claude_va.py" \
        --t2w_dir     "${BASE}/VA/${grp}/t2w" \
        --tzpz_dir    "${BASE}/VA/${grp}/tzpz" \
        --excel_path  "${BASE}/VA/CLE_MAPP_Radiology+Pathology_v1-31-2025_Deidentified2.csv" \
        --output_csv  "${BASE}/VA/${grp}/tzpz_symmetry_features.csv" \
        --skipped_csv "${BASE}/VA/${grp}/tzpz_symmetry_features_skipped.csv" \
        --id_col      MRI_FILE
done

echo ""
echo "============================================================"
echo "All tzpz symmetry feature extractions complete."
echo "============================================================"
echo ""
echo "Outputs:"
echo "  ${BASE}/PICCAI_extended/Benign/tzpz_symmetry_features.csv"
echo "  ${BASE}/PICCAI_extended/ciPCA/tzpz_symmetry_features.csv"
echo "  ${BASE}/PICCAI_extended/csPCA/tzpz_symmetry_features.csv"
echo "  ${BASE}/Chimera/tzpz_symmetry_features.csv"
echo "  ${BASE}/GIFU/tzpz_symmetry_features.csv"
echo "  ${BASE}/VA/Benign/tzpz_symmetry_features.csv"
echo "  ${BASE}/VA/ciPCA/tzpz_symmetry_features.csv"
echo "  ${BASE}/VA/csPCA/tzpz_symmetry_features.csv"