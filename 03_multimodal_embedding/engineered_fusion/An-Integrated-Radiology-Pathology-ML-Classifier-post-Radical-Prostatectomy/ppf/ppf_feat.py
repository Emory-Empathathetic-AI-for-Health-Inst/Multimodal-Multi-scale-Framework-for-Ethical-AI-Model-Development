#!/usr/bin/env python3
# ppf_features_only.py
#
# Standalone peri-prostatic fat (PPF) feature extractor.
#
# Inputs:
#   - T2W directory
#   - FAT mask directory
#   - GLAND mask directory
#   - CSV file containing patient_id column
#
# Outputs:
#   - One CSV with patient_id + PPF-only features
#
# Key design changes:
#   1) No dependency on prior symmetry/TZ/PZ CSVs
#   2) "Thickness" is restricted to a local shell around the gland surface
#   3) Masks are resampled to T2W space if shape/affine mismatch exists
#   4) T2W features are computed in the local peri-capsular shell, not over broad fat

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

# ---------------- helpers ----------------

def normalize_pid(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\.0+$", "", s)
    s = re.sub(r"^0+(\d)$", r"\1", s)
    s = re.sub(r"^0+(\d+)$", r"\1", s)
    return s if s != "" else None


def find_first_existing(base_dir: Path, candidates: list[str]) -> Path | None:
    for name in candidates:
        p = base_dir / name
        if p.exists():
            return p
    return None


def load_canonical_img(path: Path) -> nib.Nifti1Image:
    img = nib.load(str(path))
    img = nib.as_closest_canonical(img)
    return img


def get_spacing_mm(img: nib.Nifti1Image) -> np.ndarray:
    aff = img.affine
    spacing = np.sqrt((aff[:3, :3] ** 2).sum(axis=0))
    return spacing.astype(float)


def get_array_from_img(img: nib.Nifti1Image) -> np.ndarray:
    arr = img.get_fdata()
    if arr.ndim > 3:
        arr = arr[..., 0]
    return arr


def imgs_same_grid(img1: nib.Nifti1Image, img2: nib.Nifti1Image, atol: float = 1e-3) -> bool:
    return (img1.shape[:3] == img2.shape[:3]) and np.allclose(img1.affine, img2.affine, atol=atol)


def resample_to_ref(
    moving_img: nib.Nifti1Image,
    ref_img: nib.Nifti1Image,
    is_mask: bool,
) -> np.ndarray:
    order = 0 if is_mask else 1
    moved = resample_from_to(moving_img, ref_img, order=order, cval=0)
    arr = get_array_from_img(moved)
    if is_mask:
        arr = (arr > 0.5).astype(np.uint8)
    return arr


def robust_normalize_t2w(t2w: np.ndarray) -> np.ndarray:
    arr = np.asarray(t2w, dtype=np.float32)
    vals = arr[np.isfinite(arr) & (arr != 0)]
    if vals.size == 0:
        return np.zeros_like(arr, dtype=np.float32)

    p1, p99 = np.percentile(vals, [1, 99])
    if p99 <= p1:
        vmax = np.max(vals)
        if vmax <= 0:
            return np.zeros_like(arr, dtype=np.float32)
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
    median = float(np.median(arr))
    p10 = float(np.percentile(arr, 10))
    p90 = float(np.percentile(arr, 90))

    denom3 = (std + 1e-8) ** 3
    denom4 = (np.var(arr) + 1e-8) ** 2
    skew = float(np.mean((arr - mean) ** 3) / denom3)
    kurt = float(np.mean((arr - mean) ** 4) / denom4)

    return {
        "mean": mean,
        "std": std,
        "median": median,
        "p10": p10,
        "p90": p90,
        "skew": skew,
        "kurt": kurt,
    }


def mask_volume_mm3(mask: np.ndarray, spacing_mm: np.ndarray) -> float:
    return float(np.sum(mask > 0) * np.prod(spacing_mm))


def gland_boundary_mask(gland_mask: np.ndarray) -> np.ndarray:
    gland_mask = gland_mask.astype(bool)
    if not np.any(gland_mask):
        return np.zeros_like(gland_mask, dtype=bool)

    st = generate_binary_structure(3, 1)
    eroded = binary_erosion(gland_mask, structure=st, iterations=1, border_value=0)
    boundary = gland_mask & (~eroded)
    return boundary


def distance_to_gland_boundary_mm(gland_mask: np.ndarray, spacing_mm: np.ndarray) -> np.ndarray | None:
    boundary = gland_boundary_mask(gland_mask)
    if not np.any(boundary):
        return None

    # EDT returns distance for True voxels to nearest False voxel.
    # Make boundary=False, everything else=True.
    dist = distance_transform_edt(~boundary, sampling=spacing_mm)
    return dist


def percentile_or_nan(vals: np.ndarray, q: float) -> float:
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return np.nan
    return float(np.percentile(vals, q))


def safe_mean(vals: np.ndarray) -> float:
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return np.nan
    return float(np.mean(vals))


def ppf_shell_thickness_features(
    fat_mask: np.ndarray,
    gland_mask: np.ndarray,
    spacing_mm: np.ndarray,
    shell_mm: float = 15.0,
) -> tuple[dict, np.ndarray]:
    """
    Fixed local PPF thickness logic.

    Instead of summarizing distances across all fat voxels in the pelvis,
    we restrict analysis to fat within `shell_mm` of the gland boundary.
    This makes features more "peri-prostatic" and less driven by remote fat.

    Returned features include:
      - shell volume
      - thickness summaries (mean, std, p50, p75, p90, p95, max)
      - A/P and L/R means, p90s, and gaps
    """
    nan_out = {
        "ppf_shell_mm": float(shell_mm),
        "ppf_shell_vol_mm3": np.nan,
        "ppf_shell_fraction_of_ppf": np.nan,
        "ppf_thick_mean_mm": np.nan,
        "ppf_thick_std_mm": np.nan,
        "ppf_thick_p50_mm": np.nan,
        "ppf_thick_p75_mm": np.nan,
        "ppf_thick_p90_mm": np.nan,
        "ppf_thick_p95_mm": np.nan,
        "ppf_thick_max_mm": np.nan,
        "ppf_thick_anterior_mean_mm": np.nan,
        "ppf_thick_posterior_mean_mm": np.nan,
        "ppf_thick_left_mean_mm": np.nan,
        "ppf_thick_right_mean_mm": np.nan,
        "ppf_thick_anterior_p90_mm": np.nan,
        "ppf_thick_posterior_p90_mm": np.nan,
        "ppf_thick_left_p90_mm": np.nan,
        "ppf_thick_right_p90_mm": np.nan,
        "ppf_thick_ap_gap_mean_mm": np.nan,
        "ppf_thick_lr_gap_mean_mm": np.nan,
        "ppf_thick_ap_gap_p90_mm": np.nan,
        "ppf_thick_lr_gap_p90_mm": np.nan,
    }

    fat_mask = fat_mask.astype(bool)
    gland_mask = gland_mask.astype(bool)

    if not np.any(fat_mask) or not np.any(gland_mask):
        return nan_out, np.zeros_like(fat_mask, dtype=bool)

    dist_mm = distance_to_gland_boundary_mm(gland_mask, spacing_mm)
    if dist_mm is None:
        return nan_out, np.zeros_like(fat_mask, dtype=bool)

    # Restrict to local peri-capsular fat only
    peri_shell_mask = fat_mask & (dist_mm > 0) & (dist_mm <= shell_mm)
    if not np.any(peri_shell_mask):
        return nan_out, peri_shell_mask

    dvals = dist_mm[peri_shell_mask]
    ppf_vol_mm3 = mask_volume_mm3(fat_mask, spacing_mm)
    shell_vol_mm3 = mask_volume_mm3(peri_shell_mask, spacing_mm)

    out = {
        "ppf_shell_mm": float(shell_mm),
        "ppf_shell_vol_mm3": float(shell_vol_mm3),
        "ppf_shell_fraction_of_ppf": float(shell_vol_mm3 / ppf_vol_mm3) if ppf_vol_mm3 > 0 else np.nan,
        "ppf_thick_mean_mm": float(np.mean(dvals)),
        "ppf_thick_std_mm": float(np.std(dvals)),
        "ppf_thick_p50_mm": percentile_or_nan(dvals, 50),
        "ppf_thick_p75_mm": percentile_or_nan(dvals, 75),
        "ppf_thick_p90_mm": percentile_or_nan(dvals, 90),
        "ppf_thick_p95_mm": percentile_or_nan(dvals, 95),
        "ppf_thick_max_mm": float(np.max(dvals)),
    }

    # Quadrants relative to gland centroid after canonical RAS+:
    # axis 0: Right(+)/Left(-)
    # axis 1: Anterior(+)/Posterior(-)
    gland_idx = np.argwhere(gland_mask)
    center = gland_idx.mean(axis=0)

    shell_idx = np.argwhere(peri_shell_mask)
    dx = shell_idx[:, 0] - center[0]
    dy = shell_idx[:, 1] - center[1]

    left_sel = dx < 0
    right_sel = dx >= 0
    post_sel = dy < 0
    ant_sel = dy >= 0

    ant_vals = dvals[ant_sel]
    post_vals = dvals[post_sel]
    left_vals = dvals[left_sel]
    right_vals = dvals[right_sel]

    ant_mean = safe_mean(ant_vals)
    post_mean = safe_mean(post_vals)
    left_mean = safe_mean(left_vals)
    right_mean = safe_mean(right_vals)

    ant_p90 = percentile_or_nan(ant_vals, 90)
    post_p90 = percentile_or_nan(post_vals, 90)
    left_p90 = percentile_or_nan(left_vals, 90)
    right_p90 = percentile_or_nan(right_vals, 90)

    out["ppf_thick_anterior_mean_mm"] = ant_mean
    out["ppf_thick_posterior_mean_mm"] = post_mean
    out["ppf_thick_left_mean_mm"] = left_mean
    out["ppf_thick_right_mean_mm"] = right_mean

    out["ppf_thick_anterior_p90_mm"] = ant_p90
    out["ppf_thick_posterior_p90_mm"] = post_p90
    out["ppf_thick_left_p90_mm"] = left_p90
    out["ppf_thick_right_p90_mm"] = right_p90

    out["ppf_thick_ap_gap_mean_mm"] = (
        float(abs(ant_mean - post_mean)) if np.isfinite(ant_mean) and np.isfinite(post_mean) else np.nan
    )
    out["ppf_thick_lr_gap_mean_mm"] = (
        float(abs(left_mean - right_mean)) if np.isfinite(left_mean) and np.isfinite(right_mean) else np.nan
    )
    out["ppf_thick_ap_gap_p90_mm"] = (
        float(abs(ant_p90 - post_p90)) if np.isfinite(ant_p90) and np.isfinite(post_p90) else np.nan
    )
    out["ppf_thick_lr_gap_p90_mm"] = (
        float(abs(left_p90 - right_p90)) if np.isfinite(left_p90) and np.isfinite(right_p90) else np.nan
    )

    return out, peri_shell_mask


def ppf_volume_features(
    fat_mask: np.ndarray,
    gland_mask: np.ndarray,
    peri_shell_mask: np.ndarray,
    spacing_mm: np.ndarray,
) -> dict:
    ppf_vol_mm3 = mask_volume_mm3(fat_mask, spacing_mm)
    gland_vol_mm3 = mask_volume_mm3(gland_mask, spacing_mm)
    shell_vol_mm3 = mask_volume_mm3(peri_shell_mask, spacing_mm)

    return {
        "gland_vol_mm3": float(gland_vol_mm3),
        "ppf_vol_mm3": float(ppf_vol_mm3),
        "ppf_to_gland_vol_ratio": float(ppf_vol_mm3 / gland_vol_mm3) if gland_vol_mm3 > 0 else np.nan,
        "ppf_shell_to_gland_vol_ratio": float(shell_vol_mm3 / gland_vol_mm3) if gland_vol_mm3 > 0 else np.nan,
    }


def ppf_t2w_features(t2w_norm: np.ndarray, peri_shell_mask: np.ndarray) -> dict:
    vals = t2w_norm[peri_shell_mask > 0]
    stats = first_order_stats(vals)

    gx = sobel(t2w_norm, axis=0)
    gy = sobel(t2w_norm, axis=1)
    gz = sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
    edge_vals = edge[peri_shell_mask > 0]

    out = {f"ppf_shell_t2w_{k}": v for k, v in stats.items()}
    out["ppf_shell_t2w_edge_mean"] = safe_mean(edge_vals)
    out["ppf_shell_t2w_edge_p90"] = percentile_or_nan(edge_vals, 90)
    return out


def resolve_case_paths(pid: str, t2w_dir: Path, fat_dir: Path, gland_dir: Path):
    t2w_candidates = [
        f"{pid}.nii.gz", f"{pid}.nii",
        f"{pid}_t2w.nii.gz", f"{pid}_t2w.nii",
    ]
    fat_candidates = [
        f"{pid}_t2w_fat_without_gland.nii.gz", f"{pid}_t2w_fat_without_gland.nii",
        f"{pid}_fat_without_gland.nii.gz", f"{pid}_fat_without_gland.nii",
        f"{pid}_fat.nii.gz", f"{pid}_fat.nii",
        f"{pid}.nii.gz", f"{pid}.nii",
    ]
    gland_candidates = [
        f"{pid}_t2w_gland_corrected.nii.gz", f"{pid}_t2w_gland_corrected.nii",
        f"{pid}_gland_corrected.nii.gz", f"{pid}_gland_corrected.nii",
        f"{pid}_gland.nii.gz", f"{pid}_gland.nii",
        f"{pid}.nii.gz", f"{pid}.nii",
    ]

    t2w_path = find_first_existing(t2w_dir, t2w_candidates)
    fat_path = find_first_existing(fat_dir, fat_candidates)
    gland_path = find_first_existing(gland_dir, gland_candidates)

    print(
        f"[resolve] pid={pid} "
        f"T2W={'OK' if t2w_path else 'MISS'} "
        f"FAT={'OK' if fat_path else 'MISS'} "
        f"GLAND={'OK' if gland_path else 'MISS'}"
    )

    return t2w_path, fat_path, gland_path


def extract_ppf_features_for_pid(
    pid: str,
    t2w_dir: Path,
    fat_dir: Path,
    gland_dir: Path,
    shell_mm: float,
) -> dict | None:
    t2w_path, fat_path, gland_path = resolve_case_paths(pid, t2w_dir, fat_dir, gland_dir)
    if t2w_path is None or fat_path is None or gland_path is None:
        return None

    # T2W is reference space
    t2w_img = load_canonical_img(t2w_path)
    t2w = get_array_from_img(t2w_img)
    if t2w.ndim != 3:
        print(f"[skip] {pid}: T2W is not 3D after squeeze -> shape {t2w.shape}")
        return None

    spacing_mm = get_spacing_mm(t2w_img)

    fat_img = load_canonical_img(fat_path)
    gland_img = load_canonical_img(gland_path)

    if imgs_same_grid(fat_img, t2w_img):
        fat = get_array_from_img(fat_img)
        fat_mask = (fat > 0).astype(np.uint8)
    else:
        fat_mask = resample_to_ref(fat_img, t2w_img, is_mask=True)

    if imgs_same_grid(gland_img, t2w_img):
        gland = get_array_from_img(gland_img)
        gland_mask = (gland > 0).astype(np.uint8)
    else:
        gland_mask = resample_to_ref(gland_img, t2w_img, is_mask=True)

    if np.sum(fat_mask) == 0:
        print(f"[skip] {pid}: fat mask empty after loading/resampling")
        return None
    if np.sum(gland_mask) == 0:
        print(f"[skip] {pid}: gland mask empty after loading/resampling")
        return None

    t2w_norm = robust_normalize_t2w(t2w)

    thick_feats, peri_shell_mask = ppf_shell_thickness_features(
        fat_mask=fat_mask,
        gland_mask=gland_mask,
        spacing_mm=spacing_mm,
        shell_mm=shell_mm,
    )

    if np.sum(peri_shell_mask) == 0:
        print(f"[warn] {pid}: no peri-prostatic fat found within {shell_mm} mm shell")
        # still return volume + NaN shell metrics if desired
        vol_feats = ppf_volume_features(
            fat_mask=fat_mask,
            gland_mask=gland_mask,
            peri_shell_mask=peri_shell_mask,
            spacing_mm=spacing_mm,
        )
        rec = {"patient_id": pid}
        rec.update(vol_feats)
        rec.update(thick_feats)
        return rec

    vol_feats = ppf_volume_features(
        fat_mask=fat_mask,
        gland_mask=gland_mask,
        peri_shell_mask=peri_shell_mask,
        spacing_mm=spacing_mm,
    )
    tex_feats = ppf_t2w_features(t2w_norm, peri_shell_mask)

    rec = {"patient_id": pid}
    rec.update(vol_feats)
    rec.update(thick_feats)
    rec.update(tex_feats)
    return rec


# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser(description="Standalone PPF-only feature extraction.")
    ap.add_argument("--t2w_dir", required=True, type=str, help="Directory containing T2W NIfTI files")
    ap.add_argument("--fat_dir", required=True, type=str, help="Directory containing FAT mask NIfTI files")
    ap.add_argument("--gland_dir", required=True, type=str, help="Directory containing GLAND mask NIfTI files")
    ap.add_argument("--excel_path", required=True, type=str, help="CSV file containing patient_id column")
    ap.add_argument("--output_csv", required=True, type=str, help="Output CSV path for PPF-only features")
    ap.add_argument("--delimiter", default=",", type=str, help="CSV delimiter (default: ,)")
    ap.add_argument("--shell_mm", default=15.0, type=float,
                    help="Peri-capsular shell thickness in mm for local PPF features (default: 15.0)")
    args = ap.parse_args()

    t2w_dir = Path(args.t2w_dir)
    fat_dir = Path(args.fat_dir)
    gland_dir = Path(args.gland_dir)
    excel_path = Path(args.excel_path)
    output_csv = Path(args.output_csv)

    for label, d in [("t2w_dir", t2w_dir), ("fat_dir", fat_dir), ("gland_dir", gland_dir)]:
        if not d.exists():
            print(f"Missing directory: {label} -> {d}", file=sys.stderr)
            sys.exit(1)

    if not excel_path.exists():
        print(f"Missing CSV: {excel_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(excel_path, sep=args.delimiter, dtype=str, engine="python")
    except Exception:
        df = pd.read_csv(excel_path, sep=None, dtype=str, engine="python")

    if "patient_id" not in df.columns:
        for alt in ["patient", "pid", "studyID", "PatientID"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "patient_id"})
                break

    if "patient_id" not in df.columns:
        raise SystemExit("No patient_id column found in CSV.")

    df["patient_id"] = df["patient_id"].map(normalize_pid)
    pids = sorted([p for p in df["patient_id"].dropna().unique()])

    print(f"[scan] unique patient_ids: {len(pids)}")
    print(f"[scan] shell_mm = {args.shell_mm}")

    records = []
    missing = []

    for pid in pids:
        rec = extract_ppf_features_for_pid(
            pid=pid,
            t2w_dir=t2w_dir,
            fat_dir=fat_dir,
            gland_dir=gland_dir,
            shell_mm=args.shell_mm,
        )
        if rec is None:
            missing.append(pid)
            continue
        records.append(rec)
        print(f"[done] {pid}")

    if missing:
        print(f"[summary] missing/incomplete cases: {len(missing)}")
        print(f"[summary] first few missing: {missing[:10]}")

    if not records:
        print("No PPF features extracted. Exiting.")
        sys.exit(0)

    out_df = pd.DataFrame(records)
    out_df.to_csv(output_csv, index=False)
    print(f"[saved] {output_csv}")
    print(f"[summary] extracted {len(out_df)} cases with {out_df.shape[1] - 1} PPF feature columns")


if __name__ == "__main__":
    main()