import os
import glob
import pandas as pd

ROOT = "/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere"

clinical = pd.read_csv(f"{ROOT}/Chimere_prostate_clinical_data.csv")

rows = []

for _, row in clinical.iterrows():

    case = str(row["case_id"])
    bcr = int(row["BCR"])

    t2w = f"{ROOT}/t2w/{case}_0001_t2w.nii.gz"
    path = f"{ROOT}/pathology/images/{case}/{case}_1.tif"

    if os.path.exists(t2w) and os.path.exists(path):

        rows.append({
            "case_id": case,
            "bcr": bcr,
            "t2w_path": t2w,
            "pathology_path": path
        })

df = pd.DataFrame(rows)

os.makedirs(f"{ROOT}/manifests", exist_ok=True)

df.to_csv(f"{ROOT}/manifests/data_table.csv", index=False)

print("Saved:", f"{ROOT}/manifests/data_table.csv")
print("Cases:", len(df))