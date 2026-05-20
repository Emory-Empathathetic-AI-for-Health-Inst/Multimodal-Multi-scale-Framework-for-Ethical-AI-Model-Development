#!/usr/bin/env python3
import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split


def normalize_bcr(x):
    if pd.isna(x):
        return None

    s = str(x).strip().lower()

    pos_set = {"1", "true", "yes", "y", "pos", "positive", "bcr", "recur", "recurrence"}
    neg_set = {"0", "false", "no", "n", "neg", "negative", "non-bcr", "no_bcr", "none"}

    if s in pos_set:
        return 1
    if s in neg_set:
        return 0

    try:
        v = int(float(s))
        if v in (0, 1):
            return v
    except Exception:
        pass

    raise ValueError(f"Unrecognized BCR label: {x}")


def main():
    parser = argparse.ArgumentParser(description="Prepare BCR train/test manifests for T2W MRI")
    parser.add_argument(
        "--input_csv",
        default="/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere/manifests/data_table.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="/storage/home/hcoda1/1/kozyoruk3/scratch/Chimere",
    )
    parser.add_argument("--test_size", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=2023)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_csv(args.input_csv, dtype={"case_id": str})
    print("[INFO] Original columns:", list(df.columns))

    required = ["case_id", "bcr", "t2w_path"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.drop_duplicates().reset_index(drop=True)

    df["case_id"] = df["case_id"].astype(str).str.strip()
    df["bcr"] = df["bcr"].apply(normalize_bcr)
    df["t2w_path"] = df["t2w_path"].astype(str).str.strip()

    if "pathology_path" in df.columns:
        df["pathology_path"] = df["pathology_path"].astype(str).fillna("").str.strip()

    df = df.dropna(subset=["case_id", "bcr", "t2w_path"]).reset_index(drop=True)

    # Classification target expected by your code
    df["grade"] = df["bcr"].astype(int)

    # Dummy placeholders for compatibility with utility/loss code
    df["DFS"] = 0
    df["DFS_censor"] = 0

    # String IDs
    df["ID"] = df["case_id"].astype(str)
    df["radiology_folder_name"] = df["case_id"].astype(str)

    preferred = [
        "case_id",
        "ID",
        "radiology_folder_name",
        "bcr",
        "grade",
        "DFS",
        "DFS_censor",
        "t2w_path",
    ]
    if "pathology_path" in df.columns:
        preferred.append("pathology_path")

    remaining = [c for c in df.columns if c not in preferred]
    df = df[preferred + remaining]

    print("[INFO] Full dataset label counts:")
    print(df["grade"].value_counts(dropna=False))

    train_df, test_df = train_test_split(
        df,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=df["grade"],
    )

    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    # Force string dtype again before save
    for xdf in (train_df, test_df):
        xdf["case_id"] = xdf["case_id"].astype(str)
        xdf["ID"] = xdf["ID"].astype(str)
        xdf["radiology_folder_name"] = xdf["radiology_folder_name"].astype(str)
        xdf["t2w_path"] = xdf["t2w_path"].astype(str)

    print("[INFO] Train label counts:")
    print(train_df["grade"].value_counts(dropna=False))
    print("[INFO] Test label counts:")
    print(test_df["grade"].value_counts(dropna=False))

    train_out = os.path.join(args.out_dir, "data_table_output.csv")
    test_out = os.path.join(args.out_dir, "data_table_output_test.csv")

    train_df.to_csv(train_out, index=False)
    test_df.to_csv(test_out, index=False)

    print(f"[DONE] Wrote: {train_out}")
    print(f"[DONE] Wrote: {test_out}")


if __name__ == "__main__":
    main()