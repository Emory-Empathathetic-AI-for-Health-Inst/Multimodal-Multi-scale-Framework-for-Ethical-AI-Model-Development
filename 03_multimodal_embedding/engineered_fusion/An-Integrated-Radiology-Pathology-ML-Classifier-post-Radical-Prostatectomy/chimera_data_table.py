import os
import glob
import numpy as np
import pandas as pd
import SimpleITK as sitk

ROOT = "/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere"
MASK_DIR = os.path.join(ROOT, "tzpz_masks")
FEATURE_DIR = os.path.join(ROOT, "hipt_features")
OUT_CSV = os.path.join(ROOT, "data_table.csv")

TZ_LABEL = 1
PZ_LABEL = 2

def bbox_from_mask(mask):
    coords = np.argwhere(mask > 0)
    if len(coords) == 0:
        return [np.nan] * 6

    # numpy order: z, y, x
    zmin, ymin, xmin = coords.min(axis=0)
    zmax, ymax, xmax = coords.max(axis=0)

    return [int(xmin), int(xmax), int(ymin), int(ymax), int(zmin), int(zmax)]

rows = []

mask_files = sorted(glob.glob(os.path.join(MASK_DIR, "*.nii.gz")))

for mask_file in mask_files:
    case_id = os.path.basename(mask_file).replace(".nii.gz", "")
    pathology_id = case_id.split("_")[0]   # 1003_0001_t2w -> 1003

    feature_file = os.path.join(FEATURE_DIR, pathology_id + ".pt")
    if not os.path.exists(feature_file):
        print(f"[SKIP] No pathology feature found for {case_id} -> {feature_file}")
        continue

    img = sitk.ReadImage(mask_file)
    arr = sitk.GetArrayFromImage(img)   # [z, y, x]

    tz_box = bbox_from_mask(arr == TZ_LABEL)
    pz_box = bbox_from_mask(arr == PZ_LABEL)

    if np.isnan(tz_box).any():
        print(f"[WARN] TZ missing in {case_id}")
    if np.isnan(pz_box).any():
        print(f"[WARN] PZ missing in {case_id}")

    row = {
        "radiology_folder_name": case_id,
        "pathology_folder_name": pathology_id,

        # TZ -> tumor
        "X_min_tumor": tz_box[0],
        "X_max_tumor": tz_box[1],
        "Y_min_tumor": tz_box[2],
        "Y_max_tumor": tz_box[3],
        "Z_min_tumor": tz_box[4],
        "Z_max_tumor": tz_box[5],

        # PZ -> lymph
        "X_min_lymph": pz_box[0],
        "X_max_lymph": pz_box[1],
        "Y_min_lymph": pz_box[2],
        "Y_max_lymph": pz_box[3],
        "Z_min_lymph": pz_box[4],
        "Z_max_lymph": pz_box[5],

        # placeholders — replace later with real labels
        "grade": 0,
        "DFS": 0,
        "DFS_censor": 0,
        "OS": 0,
        "OS_censor": 0,
    }

    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

print(f"Saved: {OUT_CSV}")
print(f"Number of rows: {len(df)}")
print(df.head())