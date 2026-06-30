#!/usr/bin/env python3
# tzpz_symmetry_features.py
#
# Fixed for Chimere dataset:
#   - Supports single case_id column
#   - Handles nnUNet _0000 T2W suffix
#   - Robust file matching

import argparse
import sys
from pathlib import Path
import re
import numpy as np
import pandas as pd
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import sobel
from skimage.measure import regionprops, label


# =============================================================================
# Basic helpers
# =============================================================================

def normalize_id(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\.0+$", "", s)
    return s if s else None


def strip_channel_suffix(stem: str) -> str:
    return re.sub(r"_\d{4}$", "", stem)


def strip_nii_ext(name: str) -> str:
    if name.endswith(".nii.gz"):
        return name[:-7]
    if name.endswith(".nii"):
        return name[:-4]
    return name


def iter_nii_files(directory: Path):
    seen = set()
    for p in sorted(directory.rglob("*.nii.gz")):
        seen.add(p)
        yield p
    for p in sorted(directory.rglob("*.nii")):
        if p not in seen:
            yield p


def load_canonical_img(path: Path) -> nib.Nifti1Image:
    img = nib.load(str(path))
    return nib.as_closest_canonical(img)


def get_array_from_img(img: nib.Nifti1Image) -> np.ndarray:
    arr = img.get_fdata()
    return arr[..., 0] if arr.ndim > 3 else arr


def get_spacing_mm(img: nib.Nifti1Image) -> np.ndarray:
    aff = img.affine
    return np.sqrt((aff[:3, :3] ** 2).sum(axis=0))


def imgs_same_grid(img1, img2, atol=1e-3):
    return (
        img1.shape[:3] == img2.shape[:3]
        and np.allclose(img1.affine, img2.affine, atol=atol)
    )


def resample_label_to_ref(moving_img, ref_img):
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return np.rint(moved.get_fdata()).astype(np.int16)


def robust_normalize_t2w(arr: np.ndarray) -> np.ndarray:
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr)
    p1, p99 = np.percentile(vals, [1, 99])
    arr = np.clip(arr, p1, p99)
    arr = (arr - p1) / (p99 - p1 + 1e-8)
    arr[~np.isfinite(arr)] = 0
    return arr.astype(np.float32)


# =============================================================================
# File matching
# =============================================================================

def find_matching_file(case_id: str, search_dir: Path) -> Path | None:
    """
    Match NIfTI file by case_id with fallbacks:
      1. Exact stem match             e.g. 1003.nii.gz
      2. With _0000 suffix            e.g. 1003_0000.nii.gz
      3. Walk + strip channel suffix  e.g. 1003_0000.nii.gz -> 1003
      4. Walk + case_id as substring  e.g. 10003_1000003.nii.gz contains 1003
    """
    if not search_dir or not search_dir.exists():
        return None

    cid = strip_channel_suffix(case_id)

    # 1. exact
    for ext in [".nii.gz", ".nii"]:
        p = search_dir / f"{cid}{ext}"
        if p.exists():
            return p

    # 2. _0000 suffix
    for ext in [".nii.gz", ".nii"]:
        p = search_dir / f"{cid}_0000{ext}"
        if p.exists():
            return p

    # 3. walk + strip channel suffix exact match
    for p in iter_nii_files(search_dir):
        stem = strip_channel_suffix(strip_nii_ext(p.name))
        if stem == cid:
            return p

    # 4. walk + case_id as one of the underscore-split parts
    # e.g. case_id='1003' matches '1003_something' but NOT '10030_something'
    for p in iter_nii_files(search_dir):
        stem = strip_channel_suffix(strip_nii_ext(p.name))
        parts = stem.split("_")
        if cid in parts:
            return p

    return None


# =============================================================================
# Feature functions
# =============================================================================

def zone_volumes(tz_mask, pz_mask, spacing):
    vx = float(np.prod(spacing))
    tz_vol = float(np.sum(tz_mask)) * vx
    pz_vol = float(np.sum(pz_mask)) * vx
    return {
        "tz_vol_mm3":        tz_vol,
        "pz_vol_mm3":        pz_vol,
        "tz_vol_ml":         tz_vol / 1000.0,
        "pz_vol_ml":         pz_vol / 1000.0,
        "tz_to_pz_ratio":    tz_vol / (pz_vol + 1e-8),
        "tz_pz_sum_vol_mm3": tz_vol + pz_vol,
        "tz_pz_sum_vol_ml":  (tz_vol + pz_vol) / 1000.0,
    }


def zone_symmetry(mask, spacing, prefix):
    """Left-right volume symmetry along x-axis (axis=0 in canonical space)."""
    if not np.any(mask):
        return {
            f"{prefix}_left_vol_mm3":      np.nan,
            f"{prefix}_right_vol_mm3":     np.nan,
            f"{prefix}_left_right_ratio":  np.nan,
            f"{prefix}_asymmetry_index":   np.nan,
            f"{prefix}_abs_diff_mm3":      np.nan,
        }

    vx = float(np.prod(spacing))
    cx = mask.shape[0] // 2
    left_vol  = float(np.sum(mask[:cx, :, :])) * vx
    right_vol = float(np.sum(mask[cx:, :, :])) * vx

    asym = (
        abs(left_vol - right_vol) / (left_vol + right_vol)
        if (left_vol + right_vol) > 0 else np.nan
    )

    return {
        f"{prefix}_left_vol_mm3":     left_vol,
        f"{prefix}_right_vol_mm3":    right_vol,
        f"{prefix}_left_right_ratio": right_vol / (left_vol + 1e-8),
        f"{prefix}_asymmetry_index":  asym,
        f"{prefix}_abs_diff_mm3":     abs(left_vol - right_vol),
    }


def zone_intensity_features(norm_t2w, tz_mask, pz_mask):
    def stats(vals):
        if vals.size == 0:
            return {
                "mean": np.nan, "std": np.nan,
                "median": np.nan, "p10": np.nan, "p90": np.nan
            }
        return {
            "mean":   float(np.mean(vals)),
            "std":    float(np.std(vals)),
            "median": float(np.median(vals)),
            "p10":    float(np.percentile(vals, 10)),
            "p90":    float(np.percentile(vals, 90)),
        }

    tz = stats(norm_t2w[tz_mask > 0])
    pz = stats(norm_t2w[pz_mask > 0])

    contrast = (
        tz["mean"] / (pz["mean"] + 1e-6)
        if np.isfinite(tz["mean"]) and np.isfinite(pz["mean"])
        else np.nan
    )

    return {
        "tz_mean_intensity":   tz["mean"],
        "tz_std_intensity":    tz["std"],
        "tz_median_intensity": tz["median"],
        "tz_p10_intensity":    tz["p10"],
        "tz_p90_intensity":    tz["p90"],
        "pz_mean_intensity":   pz["mean"],
        "pz_std_intensity":    pz["std"],
        "pz_median_intensity": pz["median"],
        "pz_p10_intensity":    pz["p10"],
        "pz_p90_intensity":    pz["p90"],
        "tz_pz_mean_ratio":    contrast,
        "tz_pz_std_ratio":     tz["std"] / (pz["std"] + 1e-6),
    }


def shape_descriptors(tz_mask, pz_mask):
    def safe_props(mask):
        try:
            props = regionprops(label(mask.astype(np.uint8)))
            if not props:
                return np.nan, np.nan
            # use largest region
            p = max(props, key=lambda x: x.area)
            return float(p.eccentricity), float(p.orientation)
        except Exception:
            return np.nan, np.nan

    tz_ecc, tz_ori = safe_props(tz_mask)
    pz_ecc, pz_ori = safe_props(pz_mask)

    return {
        "tz_eccentricity": tz_ecc,
        "pz_eccentricity": pz_ecc,
        "tz_orientation":  tz_ori,
        "pz_orientation":  pz_ori,
    }


def edge_intensity_features(t2w_norm, mask, prefix):
    gx = sobel(t2w_norm, axis=0)
    gy = sobel(t2w_norm, axis=1)
    gz = sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx**2 + gy**2 + gz**2)
    vals = edge[mask > 0]
    if vals.size == 0:
        return {
            f"{prefix}_edge_mean": np.nan,
            f"{prefix}_edge_std":  np.nan,
            f"{prefix}_edge_p90":  np.nan,
        }
    return {
        f"{prefix}_edge_mean": float(np.mean(vals)),
        f"{prefix}_edge_std":  float(np.std(vals)),
        f"{prefix}_edge_p90":  float(np.percentile(vals, 90)),
    }


# =============================================================================
# Per-case extraction
# =============================================================================

def extract_features(case_id: str, t2w_dir: Path, tzpz_dir: Path):
    t2w_path  = find_matching_file(case_id, t2w_dir)
    tzpz_path = find_matching_file(case_id, tzpz_dir)

    print(f"  T2W  : {t2w_path  or 'MISS'}")
    print(f"  TZPZ : {tzpz_path or 'MISS'}")

    if not t2w_path:
        return None, "missing_t2w"
    if not tzpz_path:
        return None, "missing_tzpz"

    # load
    t2w_img  = load_canonical_img(t2w_path)
    t2w_arr  = get_array_from_img(t2w_img)
    spacing  = get_spacing_mm(t2w_img)

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

    rec = {"case_id": case_id}
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
        description="Extract TZ-PZ symmetry and intensity features for prostate aging."
    )
    ap.add_argument("--t2w_dir",    required=True, help="T2W NIfTI directory")
    ap.add_argument("--tzpz_dir",   required=True, help="TZ/PZ label directory (1=TZ, 2=PZ)")
    ap.add_argument("--excel_path", required=True, help="CSV with case identifiers")
    ap.add_argument("--output_csv", required=True, help="Output CSV path")
    ap.add_argument("--skipped_csv", default=None, help="Optional: path to save skipped cases")
    ap.add_argument("--id_col",     default=None,
                    help="Column name for case ID in CSV (auto-detected if not set)")
    args = ap.parse_args()

    t2w_dir  = Path(args.t2w_dir)
    tzpz_dir = Path(args.tzpz_dir)
    excel    = Path(args.excel_path)
    output   = Path(args.output_csv)

    if not excel.exists():
        sys.exit(f"Metadata file not found: {excel}")

    df = pd.read_csv(excel, dtype=str)
    print(f"CSV columns: {list(df.columns)}")
    print(f"CSV rows: {len(df)}")

    # auto-detect ID column
    id_col = args.id_col
    if id_col is None:
        for candidate in ["case_id", "patient_id", "PatientID", "pid", "id", "ID"]:
            if candidate in df.columns:
                id_col = candidate
                break
    if id_col is None:
        sys.exit(
            f"Could not auto-detect ID column. Columns found: {list(df.columns)}\n"
            f"Use --id_col to specify explicitly."
        )
    print(f"Using ID column: '{id_col}'")

    recs, skipped = [], []

    for _, row in df.iterrows():
        case_id = normalize_id(row[id_col])
        if not case_id:
            skipped.append({"case_id": "", "reason": "empty_id"})
            continue

        print(f"\n[{case_id}]")
        rec, reason = extract_features(case_id, t2w_dir, tzpz_dir)

        if rec is None:
            skipped.append({"case_id": case_id, "reason": reason})
            print(f"  -> SKIPPED: {reason}")
        else:
            recs.append(rec)
            print(f"  -> OK")

    if not recs:
        sys.exit("No features extracted. Check file naming and directory paths.")

    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(recs).to_csv(output, index=False)
    print(f"\nSaved {len(recs)} cases -> {output}")

    skipped_path = Path(args.skipped_csv) if args.skipped_csv else output.with_name(
        output.stem + "_skipped.csv"
    )
    if skipped:
        pd.DataFrame(skipped).to_csv(skipped_path, index=False)
        print(f"Skipped {len(skipped)} cases -> {skipped_path}")


if __name__ == "__main__":
    main()
