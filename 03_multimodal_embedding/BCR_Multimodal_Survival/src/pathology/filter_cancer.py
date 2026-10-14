import os
import argparse
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


def decode_name(x):
    return x.decode() if isinstance(x, (bytes, bytearray)) else str(x)


def get_wsi_stems(wsi_dir):
    """
    Read original WSI filenames from the raw WSI directory.

    Example:
        0760_11.svs  -> 0760_11
        CASE123.tiff -> CASE123
    """
    valid_exts = {".svs", ".ndpi", ".tif", ".tiff"}
    stems = []

    for f in os.listdir(wsi_dir):
        path = Path(f)
        if path.suffix.lower() in valid_exts:
            stems.append(path.stem)

    # Longest first so more specific names win
    return sorted(set(stems), key=len, reverse=True)


def parse_case_id_from_wsi_name(patch_filename, wsi_stems):
    """
    Match a patch filename back to the original WSI stem.

    Example:
        patch: 0760_11_10208_1024_None.png
        raw WSI stem: 0760_11
    """
    base = os.path.basename(patch_filename)

    for stem in wsi_stems:
        if base.startswith(stem + "_") or base == stem:
            return stem

    # fallback: strip patch suffix if no raw WSI stem matched
    parts = os.path.splitext(base)[0].split("_")

    while parts and parts[-1].lower() == "none":
        parts.pop()

    while parts and parts[-1].isdigit():
        parts.pop()

    return "_".join(parts) if parts else os.path.splitext(base)[0]


def filter_cancer_embeddings(h5_path, prediction_csv, wsi_dir, output_h5):
    """
    Keep only embeddings predicted as cancer.
    patient_ids are recovered by matching patch filenames
    against the original raw WSI filenames in wsi_dir.
    """
    df = pd.read_csv(prediction_csv)

    if "is_cancer" in df:
        values = df["is_cancer"]
        if values.dtype == object:
            values = values.astype(str).str.lower().map({"true": True, "false": False})
        cancer_df = df[values.fillna(False).astype(bool)]
    elif "cancer_probability" in df:
        cancer_df = df[df["cancer_probability"] >= 0.5]
    elif "probability_class0" in df:
        # The bundled checkpoint records class index 0 as the positive/cancer class.
        cancer_df = df[df["probability_class0"] >= 0.5]
    else:
        raise KeyError("Predictions must contain is_cancer or a cancer probability column")
    keep = set(cancer_df["filename"].astype(str).tolist())

    wsi_stems = get_wsi_stems(wsi_dir)
    if len(wsi_stems) == 0:
        raise FileNotFoundError(f"No WSI files found in: {wsi_dir}")

    with h5py.File(h5_path, "r") as f:
        feat_key = None
        for candidate in ["train_embeddings", "embeddings", "test_embeddings"]:
            if candidate in f:
                feat_key = candidate
                break

        name_key = None
        for candidate in ["file_names", "filenames", "image_path", "paths"]:
            if candidate in f:
                name_key = candidate
                break

        if feat_key is None:
            raise KeyError(f"No embedding key found in H5. Available keys: {list(f.keys())}")
        if name_key is None:
            raise KeyError(f"No filename key found in H5. Available keys: {list(f.keys())}")

        embeddings = f[feat_key][:]
        raw_names = f[name_key][:]
        filenames = [decode_name(x) for x in raw_names]

    mask = np.array([name in keep for name in filenames], dtype=bool)

    if not mask.any():
        raise RuntimeError(
            "No patches met the cancer threshold. If this was a bounded smoke test, "
            "increase --sample-count; otherwise inspect the segmentation heatmaps."
        )

    cancer_embeddings = embeddings[mask]
    cancer_filenames = np.asarray(raw_names)[mask]
    cancer_case_ids = np.asarray(
        [parse_case_id_from_wsi_name(name, wsi_stems) for name in np.asarray(filenames)[mask]],
        dtype="S",
    )

    os.makedirs(os.path.dirname(output_h5), exist_ok=True)

    with h5py.File(output_h5, "w") as f:
        f.create_dataset("embeddings", data=cancer_embeddings)
        f.create_dataset("filenames", data=cancer_filenames)
        f.create_dataset("patient_ids", data=cancer_case_ids)

    print("=" * 60)
    print(f"Original patches : {len(filenames)}")
    print(f"Cancer patches   : {len(cancer_embeddings)}")
    print(f"Saved to         : {output_h5}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--h5", required=True, type=str)
    parser.add_argument("--predictions", required=True, type=str)
    parser.add_argument("--wsi_dir", required=True, type=str)
    parser.add_argument(
        "--output",
        default="data/interim/wsi/cancer_only/cancer_embeddings.h5",
        type=str,
    )
    args = parser.parse_args()

    filter_cancer_embeddings(
        args.h5,
        args.predictions,
        args.wsi_dir,
        args.output,
    )
