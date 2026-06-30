#!/usr/bin/env python3
# ppf_features_va.py — use MRI_FILE column directly for matching files

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import argparse
import re
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nibabel.processing import resample_from_to
from scipy.ndimage import (
    binary_erosion,
    distance_transform_edt,
    generate_binary_structure,
    sobel,
)


# =============================================================================
# Helpers
# =============================================================================

def normalize_id(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\.0+$", "", s)
    return s if s else None


def strip_nii_ext(name: str) -> str:
    if name.endswith(".nii.gz"):
        return name[:-7]
    if name.endswith(".nii"):
        return name[:-4]
    return name


def load_canonical_img(path: Path) -> nib.Nifti1Image:
    return nib.as_closest_canonical(nib.load(str(path)))


def get_array_from_img(img: nib.Nifti1Image) -> np.ndarray:
    arr = img.get_fdata(dtype=np.float32)
    return arr[..., 0] if arr.ndim > 3 else arr


def get_spacing_mm(img: nib.Nifti1Image) -> np.ndarray:
    return np.sqrt((img.affine[:3, :3] ** 2).sum(axis=0)).astype(float)


def imgs_same_grid(img1, img2, atol=1e-3):
    return (
        img1.shape[:3] == img2.shape[:3]
        and np.allclose(img1.affine, img2.affine, atol=atol)
    )


def resample_mask_to_ref(moving_img, ref_img) -> np.ndarray:
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return (get_array_from_img(moved) > 0.5).astype(np.uint8)


def resample_label_to_ref(moving_img, ref_img) -> np.ndarray:
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return np.rint(get_array_from_img(moved)).astype(np.int16)


def robust_normalize_t2w(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr)

    p1, p99 = np.percentile(vals, [1, 99])
    if p99 <= p1:
        vmax = np.max(vals)
        if vmax <= 0:
            return np.zeros_like(arr)
        out = np.clip(arr, 0, vmax) / vmax
        out[~np.isfinite(out)] = 0
        return out.astype(np.float32)

    out = np.clip(arr, p1, p99)
    out = (out - p1) / (p99 - p1)
    out[~np.isfinite(out)] = 0
    return out.astype(np.float32)


def first_order_stats(arr: np.ndarray) -> dict:
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "mean": np.nan,
            "std": np.nan,
            "median": np.nan,
            "p10": np.nan,
            "p90": np.nan,
            "skew": np.nan,
            "kurt": np.nan,
        }

    mean = float(np.mean(arr))
    std = float(np.std(arr))
    return {
        "mean": mean,
        "std": std,
        "median": float(np.median(arr)),
        "p10": float(np.percentile(arr, 10)),
        "p90": float(np.percentile(arr, 90)),
        "skew": float(np.mean((arr - mean) ** 3) / (std + 1e-8) ** 3),
        "kurt": float(np.mean((arr - mean) ** 4) / (np.var(arr) + 1e-8) ** 2),
    }


def percentile_or_nan(vals, q):
    vals = vals[np.isfinite(vals)]
    return float(np.percentile(vals, q)) if vals.size > 0 else np.nan


def safe_mean(vals):
    vals = vals[np.isfinite(vals)]
    return float(np.mean(vals)) if vals.size > 0 else np.nan


def mask_volume_mm3(mask, spacing_mm):
    return float(np.sum(mask > 0) * np.prod(spacing_mm))


# =============================================================================
# Reference prostate mask
# =============================================================================

def boundary_mask_from_ref(ref_mask: np.ndarray) -> np.ndarray:
    ref_mask = ref_mask.astype(bool)
    if not np.any(ref_mask):
        return np.zeros_like(ref_mask, dtype=bool)
    st = generate_binary_structure(3, 1)
    eroded = binary_erosion(ref_mask, structure=st, iterations=1, border_value=0)
    return ref_mask & (~eroded)


def distance_to_ref_boundary_mm(ref_mask, spacing_mm):
    boundary = boundary_mask_from_ref(ref_mask)
    if not np.any(boundary):
        return None
    return distance_transform_edt(~boundary, sampling=spacing_mm)


def build_ref_mask(t2w_img, tzpz_path: Path | None):
    """Build whole-prostate reference mask from tzpz (TZ=1, PZ=2)."""
    if tzpz_path is None or not tzpz_path.exists():
        return None, None

    tzpz_img = load_canonical_img(tzpz_path)
    if imgs_same_grid(tzpz_img, t2w_img):
        tzpz_arr = get_array_from_img(tzpz_img)
    else:
        tzpz_arr = resample_label_to_ref(tzpz_img, t2w_img)

    tzpz_arr = np.rint(tzpz_arr).astype(np.int16)
    ref_mask = ((tzpz_arr == 1) | (tzpz_arr == 2)).astype(np.uint8)

    if np.sum(ref_mask) == 0:
        return None, None

    return ref_mask, "tzpz_union"


# =============================================================================
# Feature blocks
# =============================================================================

def ppf_volume_features(ppf_mask, ref_mask, spacing_mm):
    ppf_vol = mask_volume_mm3(ppf_mask, spacing_mm)
    ref_vol = mask_volume_mm3(ref_mask, spacing_mm)
    return {
        "prostate_ref_vol_mm3": ref_vol,
        "ppf_vol_mm3": ppf_vol,
        "ppf_to_prostate_ref_vol_ratio": ppf_vol / ref_vol if ref_vol > 0 else np.nan,
    }


def ppf_t2w_features(t2w_norm, ppf_mask):
    vals = t2w_norm[ppf_mask > 0]
    stats = first_order_stats(vals)

    gx = sobel(t2w_norm, axis=0)
    gy = sobel(t2w_norm, axis=1)
    gz = sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2).astype(np.float32)

    edge_vals = edge[ppf_mask > 0]
    out = {f"ppf_t2w_{k}": v for k, v in stats.items()}
    out["ppf_t2w_edge_mean"] = safe_mean(edge_vals)
    out["ppf_t2w_edge_p90"] = percentile_or_nan(edge_vals, 90)
    return out


def ppf_thickness_features(ppf_mask, ref_mask, spacing_mm):
    nan_out = {k: np.nan for k in [
        "ppf_thick_mean_mm", "ppf_thick_std_mm",
        "ppf_thick_p50_mm", "ppf_thick_p75_mm",
        "ppf_thick_p90_mm", "ppf_thick_p95_mm", "ppf_thick_max_mm",
        "ppf_thick_anterior_mean_mm", "ppf_thick_posterior_mean_mm",
        "ppf_thick_left_mean_mm", "ppf_thick_right_mean_mm",
        "ppf_thick_anterior_p90_mm", "ppf_thick_posterior_p90_mm",
        "ppf_thick_left_p90_mm", "ppf_thick_right_p90_mm",
        "ppf_thick_ap_gap_mean_mm", "ppf_thick_lr_gap_mean_mm",
        "ppf_thick_ap_gap_p90_mm", "ppf_thick_lr_gap_p90_mm",
    ]}

    ppf_mask = ppf_mask.astype(bool)
    ref_mask = ref_mask.astype(bool)
    if not np.any(ppf_mask) or not np.any(ref_mask):
        return nan_out

    dist_mm = distance_to_ref_boundary_mm(ref_mask, spacing_mm)
    if dist_mm is None:
        return nan_out

    ppf_idx = np.argwhere(ppf_mask)
    if ppf_idx.size == 0:
        return nan_out

    dvals = dist_mm[tuple(ppf_idx.T)]
    center = np.argwhere(ref_mask).mean(axis=0)
    dx = ppf_idx[:, 0] - center[0]
    dy = ppf_idx[:, 1] - center[1]

    ant_vals = dvals[dy >= 0]
    post_vals = dvals[dy < 0]
    left_vals = dvals[dx < 0]
    right_vals = dvals[dx >= 0]

    ant_mean = safe_mean(ant_vals)
    post_mean = safe_mean(post_vals)
    left_mean = safe_mean(left_vals)
    right_mean = safe_mean(right_vals)
    ant_p90 = percentile_or_nan(ant_vals, 90)
    post_p90 = percentile_or_nan(post_vals, 90)
    left_p90 = percentile_or_nan(left_vals, 90)
    right_p90 = percentile_or_nan(right_vals, 90)

    return {
        "ppf_thick_mean_mm": float(np.mean(dvals)),
        "ppf_thick_std_mm": float(np.std(dvals)),
        "ppf_thick_p50_mm": percentile_or_nan(dvals, 50),
        "ppf_thick_p75_mm": percentile_or_nan(dvals, 75),
        "ppf_thick_p90_mm": percentile_or_nan(dvals, 90),
        "ppf_thick_p95_mm": percentile_or_nan(dvals, 95),
        "ppf_thick_max_mm": float(np.max(dvals)),
        "ppf_thick_anterior_mean_mm": ant_mean,
        "ppf_thick_posterior_mean_mm": post_mean,
        "ppf_thick_left_mean_mm": left_mean,
        "ppf_thick_right_mean_mm": right_mean,
        "ppf_thick_anterior_p90_mm": ant_p90,
        "ppf_thick_posterior_p90_mm": post_p90,
        "ppf_thick_left_p90_mm": left_p90,
        "ppf_thick_right_p90_mm": right_p90,
        "ppf_thick_ap_gap_mean_mm": (
            float(abs(ant_mean - post_mean))
            if np.isfinite(ant_mean) and np.isfinite(post_mean) else np.nan
        ),
        "ppf_thick_lr_gap_mean_mm": (
            float(abs(left_mean - right_mean))
            if np.isfinite(left_mean) and np.isfinite(right_mean) else np.nan
        ),
        "ppf_thick_ap_gap_p90_mm": (
            float(abs(ant_p90 - post_p90))
            if np.isfinite(ant_p90) and np.isfinite(post_p90) else np.nan
        ),
        "ppf_thick_lr_gap_p90_mm": (
            float(abs(left_p90 - right_p90))
            if np.isfinite(left_p90) and np.isfinite(right_p90) else np.nan
        ),
    }


# =============================================================================
# Per-case extraction
# =============================================================================

def extract_features(mri_file: str, t2w_dir: Path, ppf_dir: Path, tzpz_dir: Path | None):
    t2w_path = t2w_dir / mri_file
    ppf_path = ppf_dir / mri_file
    tzpz_path = (tzpz_dir / mri_file) if tzpz_dir else None

    print(f"  T2W  : {t2w_path if t2w_path.exists() else 'MISS'}")
    print(f"  PPF  : {ppf_path if ppf_path.exists() else 'MISS'}")
    print(f"  TZPZ : {tzpz_path if (tzpz_path and tzpz_path.exists()) else 'MISS'}")

    if not t2w_path.exists():
        return None, "missing_t2w"
    if not ppf_path.exists():
        return None, "missing_ppf"

    t2w_img = load_canonical_img(t2w_path)
    t2w_arr = get_array_from_img(t2w_img)
    spacing = get_spacing_mm(t2w_img)

    ppf_img = load_canonical_img(ppf_path)
    ppf_mask = (
        (get_array_from_img(ppf_img) > 0).astype(np.uint8)
        if imgs_same_grid(ppf_img, t2w_img)
        else resample_mask_to_ref(ppf_img, t2w_img)
    )
    if np.sum(ppf_mask) == 0:
        return None, "empty_ppf_after_resampling"

    ref_mask, ref_source = build_ref_mask(
        t2w_img,
        tzpz_path if (tzpz_path and tzpz_path.exists()) else None
    )
    if ref_mask is None:
        return None, "missing_or_empty_ref_mask"

    t2w_norm = robust_normalize_t2w(t2w_arr)

    rec = {"MRI_FILE": mri_file, "prostate_ref_source": ref_source}
    rec.update(ppf_volume_features(ppf_mask, ref_mask, spacing))
    rec.update(ppf_thickness_features(ppf_mask, ref_mask, spacing))
    rec.update(ppf_t2w_features(t2w_norm, ppf_mask))
    return rec, None


# =============================================================================
# CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="PPF feature extraction using MRI_FILE column directly."
    )
    ap.add_argument("--t2w_dir", required=True)
    ap.add_argument("--ppf_dir", required=True)
    ap.add_argument("--tzpz_dir", default=None)
    ap.add_argument("--excel_path", required=True)
    ap.add_argument("--output_csv", required=True)
    ap.add_argument("--skipped_csv", default=None)
    ap.add_argument("--id_col", default="MRI_FILE")
    args = ap.parse_args()

    t2w_dir = Path(args.t2w_dir)
    ppf_dir = Path(args.ppf_dir)
    tzpz_dir = Path(args.tzpz_dir) if args.tzpz_dir else None
    excel = Path(args.excel_path)
    output = Path(args.output_csv)

    for d, name in [(t2w_dir, "t2w_dir"), (ppf_dir, "ppf_dir")]:
        if not d.exists():
            sys.exit(f"Directory not found: {name} -> {d}")

    if tzpz_dir and not tzpz_dir.exists():
        sys.exit(f"Directory not found: tzpz_dir -> {tzpz_dir}")

    if not excel.exists():
        sys.exit(f"Metadata file not found: {excel}")

    df = pd.read_csv(excel, dtype=str)
    print(f"CSV columns : {list(df.columns)}")
    print(f"CSV rows    : {len(df)}")

    id_col = args.id_col
    if id_col not in df.columns:
        sys.exit(f"Column '{id_col}' not found. Columns: {list(df.columns)}")

    print(f"Using file column: '{id_col}'")

    recs, skipped = [], []

    for _, row in df.iterrows():
        mri_file = row[id_col]

        if pd.isna(mri_file) or not str(mri_file).strip():
            skipped.append({"MRI_FILE": "", "reason": "empty_mri_file"})
            continue

        mri_file = str(mri_file).strip()

        print(f"\n[{mri_file}]")
        rec, reason = extract_features(mri_file, t2w_dir, ppf_dir, tzpz_dir)

        if rec is None:
            skipped.append({"MRI_FILE": mri_file, "reason": reason})
            print(f"  -> SKIPPED: {reason}")
        else:
            recs.append(rec)
            print("  -> OK")

    if not recs:
        sys.exit("No features extracted.")

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
        print(f"Skipped {len(skipped)} -> {skipped_path}")


if __name__ == "__main__":
    main()