import pandas as pd
import os

chimere_root = "/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere"

data_table_file = os.path.join(chimere_root, "data_table.csv")
clinical_file = "/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere/manifests/Chimere_prostate_clinical_data.csv"

out_file = os.path.join(chimere_root, "data_table_bcr.csv")

df_data = pd.read_csv(data_table_file)
df_clin = pd.read_csv(clinical_file)

# make sure IDs are strings
df_data["pathology_folder_name"] = df_data["pathology_folder_name"].astype(str)
df_clin["case_id"] = df_clin["case_id"].astype(str)

# merge clinical info
df = df_data.merge(
    df_clin[["case_id", "BCR", "time_to_followup_BCR"]],
    left_on="pathology_folder_name",
    right_on="case_id",
    how="left"
)

# set binary classification target
df["grade"] = df["BCR"].astype(float)

# optional placeholders for unused columns
df["DFS"] = df["time_to_followup_BCR"].fillna(0).astype(float)
df["DFS_censor"] = df["BCR"].astype(float)

# keep OS placeholders if your code still expects them
if "OS" not in df.columns:
    df["OS"] = 0.0
if "OS_censor" not in df.columns:
    df["OS_censor"] = 0.0

# drop redundant helper column if desired
# df = df.drop(columns=["case_id"])

df.to_csv(out_file, index=False)

print("Saved:", out_file)
print("Rows:", len(df))
print(df[[
    "radiology_folder_name",
    "pathology_folder_name",
    "grade",
    "BCR",
    "time_to_followup_BCR"
]].head())
print("BCR counts:")
print(df["grade"].value_counts(dropna=False))
print("Missing BCR labels:", df["grade"].isna().sum())