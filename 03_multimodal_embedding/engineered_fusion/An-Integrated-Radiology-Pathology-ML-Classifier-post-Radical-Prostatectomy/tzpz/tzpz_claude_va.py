#!/usr/bin/env python3
# tzpz_symmetry_features_va.py
#
# Uses MRI_FILE column directly from CSV.
# Expects exact filenames like:
#   PCA_CleVA_00006_MR_MR_day_0000_t2w_0000.nii.gz
#
# Example:
#   --t2w_dir  /home/kozyoru/emory_ts/personal_space/KOZYORU/nnUNet/infer/VA_Benign_T2/imagesTs
#   --tzpz_dir /home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/VA/Benign/tzpz
#   --excel_path /home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/VA/CLE_MAPP_Radiology+Pathology_v1-31-2025_Deidentified2.csv
#   --id_col MRI_FILE

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import sobel
from skimage.measure import regionprops, label


# =============================================================================
# Basic helpers
# =============================================================================

def load_canonical_img(path: Path) -> nib.Nifti1Image:
    img = nib.load(str(path))
    return nib.as_closest_canonical(img)


def get_array_from_img(img: nib.Nifti1Image) -> np.ndarray:
    arr = img.get_fdata(dtype=np.float32)
    return arr[..., 0] if arr.ndim > 3 else arr


def get_spacing_mm(img: nib.Nifti1Image) -> np.ndarray:
    aff = img.affine
    return np.sqrt((aff[:3, :3] ** 2).sum(axis=0)).astype(np.float32)


def imgs_same_grid(img1, img2, atol=1e-3):
    return (
        img1.shape[:3] == img2.shape[:3]
        and np.allclose(img1.affine, img2.affine, atol=atol)
    )


def resample_label_to_ref(moving_img, ref_img):
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return np.rint(moved.get_fdata(dtype=np.float32)).astype(np.int16)


def robust_normalize_t2w(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr, dtype=np.float32)

    p1, p99 = np.percentile(vals, [1, 99])
    arr = np.clip(arr, p1, p99)
    arr = (arr - p1) / (p99 - p1 + 1e-8)
    arr[~np.isfinite(arr)] = 0
    return arr.astype(np.float32)


# =============================================================================
# Feature functions
# =============================================================================

def zone_volumes(tz_mask, pz_mask, spacing):
    vx = float(np.prod(spacing))
    tz_vol = float(np.sum(tz_mask)) * vx
    pz_vol = float(np.sum(pz_mask)) * vx
    return {
        "tz_vol_mm3": tz_vol,
        "pz_vol_mm3": pz_vol,
        "tz_vol_ml": tz_vol / 1000.0,
        "pz_vol_ml": pz_vol / 1000.0,
        "tz_to_pz_ratio": tz_vol / (pz_vol + 1e-8),
        "tz_pz_sum_vol_mm3": tz_vol + pz_vol,
        "tz_pz_sum_vol_ml": (tz_vol + pz_vol) / 1000.0,
    }


def zone_symmetry(mask, spacing, prefix):
    """Left-right volume symmetry along x-axis (axis=0 in canonical space)."""
    if not np.any(mask):
        return {
            f"{prefix}_left_vol_mm3": np.nan,
            f"{prefix}_right_vol_mm3": np.nan,
            f"{prefix}_left_right_ratio": np.nan,
            f"{prefix}_asymmetry_index": np.nan,
            f"{prefix}_abs_diff_mm3": np.nan,
        }

    vx = float(np.prod(spacing))
    cx = mask.shape[0] // 2
    left_vol = float(np.sum(mask[:cx, :, :])) * vx
    right_vol = float(np.sum(mask[cx:, :, :])) * vx

    asym = (
        abs(left_vol - right_vol) / (left_vol + right_vol)
        if (left_vol + right_vol) > 0 else np.nan
    )

    return {
        f"{prefix}_left_vol_mm3": left_vol,
        f"{prefix}_right_vol_mm3": right_vol,
        f"{prefix}_left_right_ratio": right_vol / (left_vol + 1e-8),
        f"{prefix}_asymmetry_index": asym,
        f"{prefix}_abs_diff_mm3": abs(left_vol - right_vol),
    }


def zone_intensity_features(norm_t2w, tz_mask, pz_mask):
    def stats(vals):
        if vals.size == 0:
            return {
                "mean": np.nan,
                "std": np.nan,
                "median": np.nan,
                "p10": np.nan,
                "p90": np.nan,
            }
        return {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "median": float(np.median(vals)),
            "p10": float(np.percentile(vals, 10)),
            "p90": float(np.percentile(vals, 90)),
        }

    tz = stats(norm_t2w[tz_mask > 0])
    pz = stats(norm_t2w[pz_mask > 0])

    contrast = (
        tz["mean"] / (pz["mean"] + 1e-6)
        if np.isfinite(tz["mean"]) and np.isfinite(pz["mean"])
        else np.nan
    )

    return {
        "tz_mean_intensity": tz["mean"],
        "tz_std_intensity": tz["std"],
        "tz_median_intensity": tz["median"],
        "tz_p10_intensity": tz["p10"],
        "tz_p90_intensity": tz["p90"],
        "pz_mean_intensity": pz["mean"],
        "pz_std_intensity": pz["std"],
        "pz_median_intensity": pz["median"],
        "pz_p10_intensity": pz["p10"],
        "pz_p90_intensity": pz["p90"],
        "tz_pz_mean_ratio": contrast,
        "tz_pz_std_ratio": tz["std"] / (pz["std"] + 1e-6),
    }


def shape_descriptors(tz_mask, pz_mask):
    def safe_props(mask):
        try:
            props = regionprops(label(mask.astype(np.uint8)))
            if not props:
                return np.nan, np.nan
            p = max(props, key=lambda x: x.area)
            return float(p.eccentricity), float(p.orientation)
        except Exception:
            return np.nan, np.nan

    tz_ecc, tz_ori = safe_props(tz_mask)
    pz_ecc, pz_ori = safe_props(pz_mask)

    return {
        "tz_eccentricity": tz_ecc,
        "pz_eccentricity": pz_ecc,
        "tz_orientation": tz_ori,
        "pz_orientation": pz_ori,
    }


def edge_intensity_features(t2w_norm, mask, prefix):
    gx = sobel(t2w_norm, axis=0)
    gy = sobel(t2w_norm, axis=1)
    gz = sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx**2 + gy**2 + gz**2).astype(np.float32)

    vals = edge[mask > 0]
    if vals.size == 0:
        return {
            f"{prefix}_edge_mean": np.nan,
            f"{prefix}_edge_std": np.nan,
            f"{prefix}_edge_p90": np.nan,
        }
    return {
        f"{prefix}_edge_mean": float(np.mean(vals)),
        f"{prefix}_edge_std": float(np.std(vals)),
        f"{prefix}_edge_p90": float(np.percentile(vals, 90)),
    }


# =============================================================================
# Per-case extraction
# =============================================================================

def extract_features(mri_file: str, t2w_dir: Path, tzpz_dir: Path):
    t2w_path = t2w_dir / mri_file
    tzpz_path = tzpz_dir / mri_file

    print(f"  T2W  : {t2w_path if t2w_path.exists() else 'MISS'}")
    print(f"  TZPZ : {tzpz_path if tzpz_path.exists() else 'MISS'}")

    if not t2w_path.exists():
        return None, "missing_t2w"
    if not tzpz_path.exists():
        return None, "missing_tzpz"

    t2w_img = load_canonical_img(t2w_path)
    t2w_arr = get_array_from_img(t2w_img)
    spacing = get_spacing_mm(t2w_img)

    tzpz_img = load_canonical_img(tzpz_path)
    if imgs_same_grid(tzpz_img, t2w_img):
        tzpz_arr = get_array_from_img(tzpz_img)
    else:
        tzpz_arr = resample_label_to_ref(tzpz_img, t2w_img)
    tzpz_arr = np.rint(tzpz_arr).astype(np.int16)

    tz_mask = (tzpz_arr == 1).astype(np.uint8)
    pz_mask = (tzpz_arr == 2).astype(np.uint8)

    if not np.any(tz_mask) and not np.any(pz_mask):
        return None, "empty_tzpz_mask"

    norm_t2w = robust_normalize_t2w(t2w_arr)

    rec = {"MRI_FILE": mri_file}
    rec.update(zone_volumes(tz_mask, pz_mask, spacing))
    rec.update(zone_symmetry(tz_mask, spacing, "tz"))
    rec.update(zone_symmetry(pz_mask, spacing, "pz"))
    rec.update(zone_intensity_features(norm_t2w, tz_mask, pz_mask))
    rec.update(shape_descriptors(tz_mask, pz_mask))
    rec.update(edge_intensity_features(norm_t2w, tz_mask, "tz"))
    rec.update(edge_intensity_features(norm_t2w, pz_mask, "pz"))

    return rec, None


# =============================================================================
# CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Extract TZ-PZ symmetry and intensity features using MRI_FILE directly."
    )
    ap.add_argument("--t2w_dir", required=True, help="T2W NIfTI directory")
    ap.add_argument("--tzpz_dir", required=True, help="TZ/PZ label directory (1=TZ, 2=PZ)")
    ap.add_argument("--excel_path", required=True, help="CSV with MRI_FILE column")
    ap.add_argument("--output_csv", required=True, help="Output CSV path")
    ap.add_argument("--skipped_csv", default=None, help="Optional: path to save skipped cases")
    ap.add_argument("--id_col", default="MRI_FILE", help="CSV column containing exact filenames")
    args = ap.parse_args()

    t2w_dir = Path(args.t2w_dir)
    tzpz_dir = Path(args.tzpz_dir)
    excel = Path(args.excel_path)
    output = Path(args.output_csv)

    if not t2w_dir.exists():
        sys.exit(f"T2W directory not found: {t2w_dir}")
    if not tzpz_dir.exists():
        sys.exit(f"TZPZ directory not found: {tzpz_dir}")
    if not excel.exists():
        sys.exit(f"Metadata file not found: {excel}")

    df = pd.read_csv(excel, dtype=str)
    print(f"CSV columns: {list(df.columns)}")
    print(f"CSV rows: {len(df)}")

    id_col = args.id_col
    if id_col not in df.columns:
        sys.exit(f"Column '{id_col}' not found. Columns found: {list(df.columns)}")

    print(f"Using file column: '{id_col}'")

    recs = []
    skipped = []

    for _, row in df.iterrows():
        mri_file = row[id_col]

        if pd.isna(mri_file) or not str(mri_file).strip():
            skipped.append({"MRI_FILE": "", "reason": "empty_mri_file"})
            continue

        mri_file = str(mri_file).strip()

        print(f"\n[{mri_file}]")
        rec, reason = extract_features(mri_file, t2w_dir, tzpz_dir)

        if rec is None:
            skipped.append({"MRI_FILE": mri_file, "reason": reason})
            print(f"  -> SKIPPED: {reason}")
        else:
            recs.append(rec)
            print("  -> OK")

    if not recs:
        sys.exit("No features extracted. Check filenames in MRI_FILE and folder contents.")

    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(recs).to_csv(output, index=False)
    print(f"\nSaved {len(recs)} cases -> {output}")

    skipped_path = (
        Path(args.skipped_csv)
        if args.skipped_csv
        else output.with_name(output.stem + "_skipped.csv")
    )
    if skipped:
        pd.DataFrame(skipped).to_csv(skipped_path, index=False)
        print(f"Skipped {len(skipped)} cases -> {skipped_path}")


if __name__ == "__main__":
    main()