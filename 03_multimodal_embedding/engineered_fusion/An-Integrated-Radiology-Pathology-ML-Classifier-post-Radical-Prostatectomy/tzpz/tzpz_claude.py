#!/usr/bin/env python3
# tzpz_symmetry_features.py
#
# Author: Kutsev B. Ozyoruk
# Purpose: Quantify TZ–PZ symmetry, intensity, and shape features
#          for prostate aging analysis using T2W MRI and zone masks.

import argparse
import sys
from pathlib import Path
import re
import numpy as np
import pandas as pd
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import binary_erosion, generate_binary_structure, distance_transform_edt, sobel
from skimage.measure import regionprops, label

# ---------- BASIC HELPERS ----------

def normalize_pid(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\.0+$", "", s)
    s = re.sub(r"^0+(\d+)$", r"\1", s)
    return s if s else None

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
    return img1.shape[:3] == img2.shape[:3] and np.allclose(img1.affine, img2.affine, atol=atol)

def resample_label(moving_img, ref_img):
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    return np.rint(moved.get_fdata()).astype(np.int16)

def robust_normalize_t2w(arr):
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr)
    p1, p99 = np.percentile(vals, [1, 99])
    arr = np.clip(arr, p1, p99)
    arr = (arr - p1) / (p99 - p1 + 1e-8)
    arr[~np.isfinite(arr)] = 0
    return arr.astype(np.float32)

# ---------- FEATURE FUNCTIONS ----------

def zone_volumes(tz_mask, pz_mask, spacing):
    tz_vol = np.sum(tz_mask) * np.prod(spacing)
    pz_vol = np.sum(pz_mask) * np.prod(spacing)
    total = tz_vol + pz_vol
    return {
        "tz_vol_mm3": tz_vol,
        "pz_vol_mm3": pz_vol,
        "tz_to_pz_ratio": tz_vol / (pz_vol + 1e-8),
        "tz_pz_sum_vol_mm3": total,
    }

def zone_symmetry(mask, spacing, prefix):
    """Compute left-right volume symmetry for given mask"""
    if not np.any(mask):
        return {
            f"{prefix}_left_vol_mm3": np.nan,
            f"{prefix}_right_vol_mm3": np.nan,
            f"{prefix}_left_right_ratio": np.nan,
            f"{prefix}_abs_diff_mm3": np.nan,
        }

    center_x = mask.shape[0] // 2
    left = mask[:center_x, :, :]
    right = mask[center_x:, :, :]
    left_vol = np.sum(left) * np.prod(spacing)
    right_vol = np.sum(right) * np.prod(spacing)
    return {
        f"{prefix}_left_vol_mm3": left_vol,
        f"{prefix}_right_vol_mm3": right_vol,
        f"{prefix}_left_right_ratio": right_vol / (left_vol + 1e-8),
        f"{prefix}_abs_diff_mm3": abs(left_vol - right_vol),
    }

def zone_intensity_features(norm_t2w, tz_mask, pz_mask):
    def zone_stats(vals):
        if vals.size == 0:
            return {"mean": np.nan, "std": np.nan, "p90": np.nan}
        return {"mean": np.mean(vals), "std": np.std(vals), "p90": np.percentile(vals, 90)}

    tz_vals = norm_t2w[tz_mask > 0]
    pz_vals = norm_t2w[pz_mask > 0]
    f_tz, f_pz = zone_stats(tz_vals), zone_stats(pz_vals)

    contrast = f_tz["mean"] / (f_pz["mean"] + 1e-6) if np.isfinite(f_tz["mean"]) and np.isfinite(f_pz["mean"]) else np.nan
    return {
        "tz_mean_intensity": f_tz["mean"],
        "pz_mean_intensity": f_pz["mean"],
        "tz_pz_mean_ratio": contrast,
        "tz_intensity_std": f_tz["std"],
        "pz_intensity_std": f_pz["std"],
        "tz_pz_std_ratio": f_tz["std"] / (f_pz["std"] + 1e-6),
    }

def shape_descriptors(tz_mask, pz_mask):
    def safe_regionprops(mask):
        try:
            props = regionprops(label(mask))
            if len(props) == 0:
                return np.nan, np.nan
            return props[0].eccentricity, props[0].orientation
        except Exception:
            return np.nan, np.nan
    tz_ecc, tz_orient = safe_regionprops(tz_mask)
    pz_ecc, pz_orient = safe_regionprops(pz_mask)
    return {
        "tz_eccentricity": tz_ecc,
        "pz_eccentricity": pz_ecc,
        "tz_orientation": tz_orient,
        "pz_orientation": pz_orient,
    }

def edge_intensity_features(t2w_norm, mask, spacing, prefix):
    gx, gy, gz = sobel(t2w_norm, axis=0), sobel(t2w_norm, axis=1), sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx**2 + gy**2 + gz**2)
    vals = edge[mask > 0]
    if vals.size == 0:
        return {f"{prefix}_edge_mean": np.nan, f"{prefix}_edge_p90": np.nan}
    return {
        f"{prefix}_edge_mean": float(np.mean(vals)),
        f"{prefix}_edge_p90": float(np.percentile(vals, 90)),
    }

# ---------- FILE MATCHING ----------

def find_file_with_study_patient(base_dir, study_id, patient_id, suffix_list=None):
    """File naming pattern: study_patient_suffix.nii.gz or patient_study_suffix.nii.gz"""
    if not base_dir or not Path(base_dir).exists():
        return None
    sid = normalize_pid(study_id)
    pid = normalize_pid(patient_id)
    if not sid or not pid:
        return None
    if suffix_list is None:
        suffix_list = ["", "_0000", "_t2w", "_tzpz"]

    for a, b in [(sid, pid), (pid, sid)]:
        for suf in suffix_list:
            for ext in [".nii.gz", ".nii"]:
                f = Path(base_dir) / f"{a}_{b}{suf}{ext}"
                if f.exists():
                    return f
    return None

# ---------- MAIN FEATURE EXTRACTION ----------

def extract_tzpz_features(pid, sid, t2w_dir, tzpz_dir):
    # find images
    t2w_path = find_file_with_study_patient(t2w_dir, sid, pid, ["_0000", "_t2w", ""])
    tzpz_path = find_file_with_study_patient(tzpz_dir, sid, pid, ["_tzpz", "", "_t2w"])
    print(f"[resolve] pid={pid}, sid={sid}")
    print(f"  T2W  : {t2w_path if t2w_path else 'MISS'}")
    print(f"  TZPZ : {tzpz_path if tzpz_path else 'MISS'}")
    if not (t2w_path and tzpz_path):
        return None, "missing_files"

    t2w_img = load_canonical_img(t2w_path)
    t2w = get_array_from_img(t2w_img)
    spacing = get_spacing_mm(t2w_img)

    tzpz_img = load_canonical_img(tzpz_path)
    tzpz_arr = resample_label(tzpz_img, t2w_img) if not imgs_same_grid(tzpz_img, t2w_img) else get_array_from_img(tzpz_img)
    tzpz_arr = np.rint(tzpz_arr).astype(np.int16)

    tz_mask = (tzpz_arr == 1).astype(np.uint8)
    pz_mask = (tzpz_arr == 2).astype(np.uint8)
    if not (np.any(tz_mask) or np.any(pz_mask)):
        return None, "empty_tzpz"

    norm_t2w = robust_normalize_t2w(t2w)

    rec = {
        "patient_id": pid,
        "study_id": sid,
    }

    rec.update(zone_volumes(tz_mask, pz_mask, spacing))
    rec.update(zone_symmetry(tz_mask, spacing, "tz"))
    rec.update(zone_symmetry(pz_mask, spacing, "pz"))
    rec.update(zone_intensity_features(norm_t2w, tz_mask, pz_mask))
    rec.update(shape_descriptors(tz_mask, pz_mask))
    rec.update(edge_intensity_features(norm_t2w, tz_mask, spacing, "tz"))
    rec.update(edge_intensity_features(norm_t2w, pz_mask, spacing, "pz"))
    return rec, None

# ---------- MAIN SCRIPT ----------

def main():
    ap = argparse.ArgumentParser(description="Extract TZ–PZ symmetry and intensity features for prostate aging.")
    ap.add_argument("--t2w_dir", required=True, type=str, help="T2W NIfTI directory")
    ap.add_argument("--tzpz_dir", required=True, type=str, help="TZ/PZ label directory (1=TZ, 2=PZ)")
    ap.add_argument("--excel_path", required=True, type=str, help="CSV with patient_id and study_id")
    ap.add_argument("--output_csv", required=True, type=str, help="Output CSV path")
    args = ap.parse_args()

    t2w_dir = Path(args.t2w_dir)
    tzpz_dir = Path(args.tzpz_dir)
    excel = Path(args.excel_path)
    output = Path(args.output_csv)

    if not excel.exists():
        print(f"Missing metadata file: {excel}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(excel, dtype=str)
    pid_col, sid_col = None, None
    for alt in ["patient_id", "pid", "PatientID"]:
        if alt in df.columns:
            pid_col = alt
            break
    for alt in ["study_id", "StudyID", "sid"]:
        if alt in df.columns:
            sid_col = alt
            break
    if not pid_col:
        raise SystemExit("CSV must contain patient_id column.")
    if not sid_col:
        raise SystemExit("CSV must contain study_id column.")

    recs, skipped = [], []
    print(f"[scan] total records: {len(df)}")

    for _, row in df.iterrows():
        pid = normalize_pid(row[pid_col])
        sid = normalize_pid(row[sid_col])
        rec, reason = extract_tzpz_features(pid, sid, t2w_dir, tzpz_dir)
        if rec is None:
            skipped.append({"patient_id": pid, "study_id": sid, "reason": reason})
            print(f"[skip] {sid}_{pid}: {reason}")
            continue
        recs.append(rec)
        print(f"[done] {sid}_{pid}")

    if not recs:
        print("No features extracted.")
        sys.exit(0)

    out = pd.DataFrame(recs)
    out.to_csv(output, index=False)
    print(f"[saved] {output} ({len(out)} cases)")

    if skipped:
        skipped_df = pd.DataFrame(skipped)
        skipped_path = output.with_name(output.stem + "_skipped.csv")
        skipped_df.to_csv(skipped_path, index=False)
        print(f"[saved] skipped cases → {skipped_path}")

if __name__ == "__main__":
    main()
