BASE="/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026"

for grp in csPCA; do
    python /home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/feature_extractor/tzpz/piccai_missing.py \
        --t2w_dir   "${BASE}/PICCAI_extended/${grp}/t2w" \
        --tzpz_dir  "${BASE}/PICCAI_extended/${grp}/tzpz" \
        --old_csv   "${BASE}/PICCAI_extended/${grp}/tzpz_symmetry_features.csv" \
        --output_csv "${BASE}/PICCAI_extended/${grp}/tzpz_symmetry_features_40col.csv"
done