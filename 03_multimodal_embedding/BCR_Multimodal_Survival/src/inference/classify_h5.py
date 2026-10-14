
import h5py
import numpy as np
import pandas as pd
import joblib
import argparse
import os
from tqdm import tqdm


def run_classification(h5_path, model_path, output_csv):
    # 1. Load the Model Checkpoint
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    print(f"Loading model from {model_path}...")
    checkpoint = joblib.load(model_path)
    clf = checkpoint["model"]

    # Use the saved index or default to 0
    pos_idx = checkpoint.get("pos_class_idx", 0)
    if not 0 <= pos_idx < len(clf.classes_):
        raise ValueError(f"Invalid positive-class index {pos_idx} for classes {clf.classes_}")
    cancer_class = clf.classes_[pos_idx]

    # 2. Open Embeddings with high-performance cache
    print(f"Opening embeddings: {h5_path}")

    if not os.path.isfile(h5_path):
        raise FileNotFoundError(f"Embeddings not found at {h5_path}")
    with h5py.File(h5_path, "r", rdcc_nbytes=256 * 1024**2) as f:

        # Support different H5 formats
        feat_key = "train_embeddings" if "train_embeddings" in f else "embeddings"
        name_key = "file_names" if "file_names" in f else "filenames"

        if feat_key not in f or name_key not in f:
            raise KeyError(f"Required datasets missing. Available keys: {list(f.keys())}")
        feats = f[feat_key]
        raw_names = f[name_key][:]

        filenames = [
            fn.decode() if isinstance(fn, bytes) else fn
            for fn in raw_names
        ]

        total = len(filenames)
        if len(feats) != total:
            raise ValueError("Embedding and filename counts do not match")
        print(f"Processing {total} patches...")

        all_probs = []
        all_preds = []

        batch_size = 25000

        for start in tqdm(range(0, total, batch_size), desc="Classifying"):

            end = min(start + batch_size, total)

            X_batch = feats[start:end]

            probs = clf.predict_proba(X_batch)[:, pos_idx]
            preds = clf.predict(X_batch)

            all_probs.extend(probs)
            all_preds.extend(preds)

    # 3. Save results
    results = pd.DataFrame({
        "filename": filenames,
        "prediction": all_preds,
        "probability_class0": all_probs,
        "cancer_probability": all_probs,
        "is_cancer": np.asarray(all_probs) >= 0.5,
    })

    output_parent = os.path.dirname(os.path.abspath(output_csv))
    os.makedirs(output_parent, exist_ok=True)
    results.to_csv(output_csv, index=False)

    print(f"Cancer class: {cancer_class!r} (probability column index {pos_idx})")
    print(f"Done! Results saved to {output_csv}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--h5",
        type=str,
        required=True,
        help="Path to the patch embeddings H5 file",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="checkpoints/pathology/prostate_uni2_model.joblib",
        help="Path to the pathology classifier checkpoint",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="outputs/predictions/patch_predictions.csv",
        help="Output CSV path",
    )

    args = parser.parse_args()

    run_classification(
        args.h5,
        args.model,
        args.output,
    )
