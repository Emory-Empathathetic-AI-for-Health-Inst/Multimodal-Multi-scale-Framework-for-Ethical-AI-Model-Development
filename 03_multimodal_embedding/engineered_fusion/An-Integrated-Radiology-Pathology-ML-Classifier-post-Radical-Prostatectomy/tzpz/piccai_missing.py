#!/usr/bin/env python3
# augment_old_tzpz_to_40col.py
#
# Take an OLD 28-column tzpz_symmetry_features.csv and add the missing
# columns to make it match the NEW 40-column canonical schema, by:
#   - renaming the two changed column names (tz/pz_intensity_std -> tz/pz_std_intensity)
#   - deriving the *_vol_ml columns from existing *_vol_mm3 columns
#   - re-extracting only the missing per-zone stats (PZ asymmetry, percentiles,
#     edge std) from the T2W + TZ/PZ NIfTI files
#
# Output: a new CSV with all 40 canonical columns plus the original
#         patient_id / study_id (or whatever ID columns existed).
#
# Usage:
#   python augment_old_tzpz_to_40col.py \
#       --t2w_dir  /path/to/PICCAI_extended/Benign/t2w \
#       --tzpz_dir /path/to/PICCAI_extended/Benign/tzpz \
#       --old_csv  /path/to/PICCAI_extended/Benign/tzpz_symmetry_features.csv \
#       --output_csv /path/to/PICCAI_extended/Benign/tzpz_symmetry_features_40col.csv

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import sobel


# ---------- helpers ---------------------------------------------------------
def load_canonical_img(path: Path):
    img = nib.load(str(path))
    return nib.as_closest_canonical(img)


def get_array(img):
    arr = img.get_fdata(dtype=np.float32)
    return arr[..., 0] if arr.ndim > 3 else arr


def get_spacing(img):
    aff = img.affine
    return np.sqrt((aff[:3, :3] ** 2).sum(axis=0)).astype(np.float32)


def imgs_same_grid(img1, img2, atol=1e-3):
    return img1.shape[:3] == img2.shape[:3] and np.allclose(img1.affine, img2.affine, atol=atol)


def resample_label_to_ref(moving_img, ref_img):
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return np.rint(moved.get_fdata(dtype=np.float32)).astype(np.int16)


def robust_normalize_t2w(arr):
    arr = np.asarray(arr, dtype=np.float32)
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr, dtype=np.float32)
    p1, p99 = np.percentile(vals, [1, 99])
    arr = np.clip(arr, p1, p99)
    arr = (arr - p1) / (p99 - p1 + 1e-8)
    arr[~np.isfinite(arr)] = 0
    return arr.astype(np.float32)


def clean_id(x):
    """Convert 10613.0 -> 10613, keep string IDs unchanged."""
    if x is None or pd.isna(x):
        return None

    s = str(x).strip()

    # Handle pandas/numpy float IDs like 10613.0
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass

    # Fallback: remove only trailing .0
    if s.endswith(".0"):
        s = s[:-2]

    return s


def find_nifti(directory: Path, patient_id, study_id=None):
    """Try several PI-CAI naming conventions with cleaned IDs."""
    candidates = []

    pid = clean_id(patient_id)
    sid = clean_id(study_id)

    if pid is None:
        return None

    if sid:
        candidates += [
            f"{pid}_{sid}.nii.gz", f"{pid}_{sid}.nii",
            f"{pid}_{sid}_t2w.nii.gz", f"{pid}_{sid}_t2w.nii",
            f"{pid}_{sid}_0000.nii.gz", f"{pid}_{sid}_0000.nii",
        ]

    candidates += [
        f"{pid}.nii.gz", f"{pid}.nii",
        f"{pid}_t2w.nii.gz", f"{pid}_t2w.nii",
        f"{pid}_0000.nii.gz", f"{pid}_0000.nii",
    ]

    for c in candidates:
        p = directory / c
        if p.exists():
            return p

    return None


# ---------- compute the missing pieces only ---------------------------------
def compute_missing(t2w_path, tzpz_path):
    """Return dict with only the columns that need re-computation."""
    t2w_img = load_canonical_img(t2w_path)
    t2w_arr = get_array(t2w_img)
    spacing = get_spacing(t2w_img)

    tzpz_img = load_canonical_img(tzpz_path)
    if imgs_same_grid(tzpz_img, t2w_img):
        tzpz_arr = get_array(tzpz_img)
    else:
        tzpz_arr = resample_label_to_ref(tzpz_img, t2w_img)
    tzpz_arr = np.rint(tzpz_arr).astype(np.int16)

    tz_mask = (tzpz_arr == 1).astype(np.uint8)
    pz_mask = (tzpz_arr == 2).astype(np.uint8)

    norm_t2w = robust_normalize_t2w(t2w_arr)

    out = {}
    vx = float(np.prod(spacing))

    # PZ asymmetry index (only field missing on the symmetry side)
    if np.any(pz_mask):
        cx = pz_mask.shape[0] // 2
        l = float(np.sum(pz_mask[:cx])) * vx
        r = float(np.sum(pz_mask[cx:])) * vx
        out["pz_asymmetry_index"] = abs(l - r) / (l + r) if (l + r) > 0 else np.nan
    else:
        out["pz_asymmetry_index"] = np.nan

    # PZ percentile / median intensities (TZ percentiles already in old file)
    pz_vals = norm_t2w[pz_mask > 0]
    if pz_vals.size:
        out["pz_median_intensity"] = float(np.median(pz_vals))
        out["pz_p10_intensity"]    = float(np.percentile(pz_vals, 10))
        out["pz_p90_intensity"]    = float(np.percentile(pz_vals, 90))
    else:
        out["pz_median_intensity"] = np.nan
        out["pz_p10_intensity"]    = np.nan
        out["pz_p90_intensity"]    = np.nan

    # TZ percentile / median intensities (in case the old file lacks them)
    tz_vals = norm_t2w[tz_mask > 0]
    if tz_vals.size:
        out["tz_median_intensity"] = float(np.median(tz_vals))
        out["tz_p10_intensity"]    = float(np.percentile(tz_vals, 10))
        out["tz_p90_intensity"]    = float(np.percentile(tz_vals, 90))
    else:
        out["tz_median_intensity"] = np.nan
        out["tz_p10_intensity"]    = np.nan
        out["tz_p90_intensity"]    = np.nan

    # PZ + TZ edge_std
    gx = sobel(norm_t2w, axis=0)
    gy = sobel(norm_t2w, axis=1)
    gz = sobel(norm_t2w, axis=2)
    edge = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2).astype(np.float32)
    pz_edge = edge[pz_mask > 0]
    tz_edge = edge[tz_mask > 0]
    out["pz_edge_std"] = float(np.std(pz_edge)) if pz_edge.size else np.nan
    out["tz_edge_std"] = float(np.std(tz_edge)) if tz_edge.size else np.nan

    return out


# ---------- main ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t2w_dir",   required=True)
    ap.add_argument("--tzpz_dir",  required=True)
    ap.add_argument("--old_csv",   required=True, help="Existing 28-col tzpz_symmetry_features.csv")
    ap.add_argument("--output_csv", required=True)
    args = ap.parse_args()

    t2w_dir  = Path(args.t2w_dir)
    tzpz_dir = Path(args.tzpz_dir)
    old      = Path(args.old_csv)
    out_path = Path(args.output_csv)

    df = pd.read_csv(old)
    print(f"Loaded {len(df)} rows × {len(df.columns)} cols from {old.name}")

    # 1. Rename old -> new column names (just two pure renames)
    rename_map = {
        "tz_intensity_std": "tz_std_intensity",
        "pz_intensity_std": "pz_std_intensity",
    }
    for old_name, new_name in rename_map.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})
            print(f"  renamed: {old_name} -> {new_name}")

    # 2. Derive *_vol_ml from *_vol_mm3 (cheap, no NIfTI needed)
    for prefix in ["tz", "pz"]:
        if f"{prefix}_vol_mm3" in df.columns and f"{prefix}_vol_ml" not in df.columns:
            df[f"{prefix}_vol_ml"] = df[f"{prefix}_vol_mm3"] / 1000.0
            print(f"  derived: {prefix}_vol_ml = {prefix}_vol_mm3 / 1000")
    if "tz_pz_sum_vol_mm3" in df.columns and "tz_pz_sum_vol_ml" not in df.columns:
        df["tz_pz_sum_vol_ml"] = df["tz_pz_sum_vol_mm3"] / 1000.0
        print("  derived: tz_pz_sum_vol_ml = tz_pz_sum_vol_mm3 / 1000")

    # 3. Identify missing columns relative to the 40-col canonical schema
    canonical_40 = {
        "tz_vol_mm3", "pz_vol_mm3", "tz_vol_ml", "pz_vol_ml",
        "tz_to_pz_ratio", "tz_pz_sum_vol_mm3", "tz_pz_sum_vol_ml",
        "tz_left_vol_mm3", "tz_right_vol_mm3", "tz_left_right_ratio",
        "tz_asymmetry_index", "tz_abs_diff_mm3",
        "pz_left_vol_mm3", "pz_right_vol_mm3", "pz_left_right_ratio",
        "pz_asymmetry_index", "pz_abs_diff_mm3",
        "tz_mean_intensity", "tz_std_intensity", "tz_median_intensity",
        "tz_p10_intensity", "tz_p90_intensity",
        "pz_mean_intensity", "pz_std_intensity", "pz_median_intensity",
        "pz_p10_intensity", "pz_p90_intensity",
        "tz_pz_mean_ratio", "tz_pz_std_ratio",
        "tz_eccentricity", "pz_eccentricity", "tz_orientation", "pz_orientation",
        "tz_edge_mean", "tz_edge_std", "tz_edge_p90",
        "pz_edge_mean", "pz_edge_std", "pz_edge_p90",
    }
    missing = [c for c in canonical_40 if c not in df.columns]
    print(f"  Missing {len(missing)} cols still requiring NIfTI re-computation: {missing}")

    if not missing:
        df.to_csv(out_path, index=False)
        print(f"Nothing to re-compute. Saved as 40-col CSV -> {out_path}")
        return

    # 4. Walk each row and compute the missing fields from NIfTI
    pid_col = "patient_id" if "patient_id" in df.columns else None
    sid_col = "study_id" if "study_id" in df.columns else None
    if pid_col is None:
        sys.exit("CSV has no patient_id column; cannot locate NIfTI files.")

    new_cols = {c: [] for c in missing}
    n_ok = 0
    n_skip = 0
    for idx, row in df.iterrows():
        pid = row[pid_col]
        sid = row[sid_col] if sid_col else None
        t2w_p  = find_nifti(t2w_dir,  pid, sid)
        tzpz_p = find_nifti(tzpz_dir, pid, sid)
        if t2w_p is None or tzpz_p is None:
            for c in missing:
                new_cols[c].append(np.nan)
            n_skip += 1
            print(f"  [skip] pid={pid} sid={sid}: missing files")
            continue
        try:
            extra = compute_missing(t2w_p, tzpz_p)
            for c in missing:
                new_cols[c].append(extra.get(c, np.nan))
            n_ok += 1
            if (idx + 1) % 50 == 0:
                print(f"  processed {idx + 1}/{len(df)}")
        except Exception as e:
            for c in missing:
                new_cols[c].append(np.nan)
            n_skip += 1
            print(f"  [skip] pid={pid}: {e}")

    for c, vals in new_cols.items():
        df[c] = vals

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nDone. {n_ok} rows augmented, {n_skip} skipped.")
    print(f"Saved -> {out_path}  (now {df.shape[1]} cols)")


if __name__ == "__main__":
    main()