#!/usr/bin/env python3
# ppf_features_only_with_tzpz_fallback.py

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


def load_canonical_img(path: Path) -> nib.Nifti1Image:
    img = nib.load(str(path))
    img = nib.as_closest_canonical(img)
    return img


def get_array_from_img(img: nib.Nifti1Image) -> np.ndarray:
    arr = img.get_fdata()
    if arr.ndim > 3:
        arr = arr[..., 0]
    return arr


def get_spacing_mm(img: nib.Nifti1Image) -> np.ndarray:
    aff = img.affine
    spacing = np.sqrt((aff[:3, :3] ** 2).sum(axis=0))
    return spacing.astype(float)


def imgs_same_grid(img1: nib.Nifti1Image, img2: nib.Nifti1Image, atol: float = 1e-3) -> bool:
    return (img1.shape[:3] == img2.shape[:3]) and np.allclose(img1.affine, img2.affine, atol=atol)


def resample_mask_to_ref(moving_img: nib.Nifti1Image, ref_img: nib.Nifti1Image) -> np.ndarray:
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    arr = get_array_from_img(moved)
    return (arr > 0.5).astype(np.uint8)


def resample_label_to_ref(moving_img: nib.Nifti1Image, ref_img: nib.Nifti1Image) -> np.ndarray:
    """
    Preserve integer labels like TZ=1, PZ=2 during nearest-neighbor resampling.
    """
    moved = resample_from_to(moving_img, ref_img, order=0, cval=0)
    arr = get_array_from_img(moved)
    return np.rint(arr).astype(np.int16)


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


def mask_volume_mm3(mask: np.ndarray, spacing_mm: np.ndarray) -> float:
    return float(np.sum(mask > 0) * np.prod(spacing_mm))


# ---------------- filename normalization + robust matching ----------------

def strip_nii_ext(name: str) -> str:
    if name.endswith(".nii.gz"):
        return name[:-7]
    if name.endswith(".nii"):
        return name[:-4]
    return Path(name).stem


def normalize_case_id_from_name(name: str) -> str | None:
    base = strip_nii_ext(Path(name).name)

    suffixes = [
        "_t2w_fat_without_gland",
        "_fat_without_gland",
        "_t2w_gland_corrected",
        "_gland_corrected",
        "_t2w_gland",
        "_gland",
        "_t2w_ppf",
        "_ppf",
        "_tzpz",
        "_t2w",
        "_0000",
    ]

    changed = True
    while changed:
        changed = False
        for suf in suffixes:
            if base.endswith(suf):
                base = base[:-len(suf)]
                changed = True

    return normalize_pid(base)


def list_nifti_files(base_dir: Path | None) -> list[Path]:
    if base_dir is None or not base_dir.exists():
        return []
    return sorted(
        p for p in base_dir.iterdir()
        if p.is_file() and (p.name.endswith(".nii.gz") or p.name.endswith(".nii"))
    )


def find_matching_nifti(
    base_dir: Path | None,
    pid: str,
    preferred_suffixes: list[str] | None = None,
) -> Path | None:
    target = normalize_pid(pid)
    if target is None:
        return None

    matches = []
    for p in list_nifti_files(base_dir):
        file_pid = normalize_case_id_from_name(p.name)
        if file_pid == target:
            matches.append(p)

    if not matches:
        return None

    if preferred_suffixes:
        for suf in preferred_suffixes:
            for p in matches:
                stem = strip_nii_ext(p.name)
                if suf == "":
                    if normalize_case_id_from_name(p.name) == target and stem == target:
                        return p
                elif stem.endswith(suf):
                    return p

    matches = sorted(
        matches,
        key=lambda p: (
            0 if p.name.endswith(".nii.gz") else 1,
            len(strip_nii_ext(p.name)),
            p.name,
        )
    )
    return matches[0]


def resolve_case_paths(pid: str, t2w_dir: Path, ppf_dir: Path, gland_dir: Path | None, tzpz_dir: Path | None):
    t2w_path = find_matching_nifti(
        t2w_dir,
        pid,
        preferred_suffixes=["_0000", "_t2w", ""],
    )

    ppf_path = find_matching_nifti(
        ppf_dir,
        pid,
        preferred_suffixes=[
            "_t2w_ppf",
            "_ppf",
            "_t2w_fat_without_gland",
            "_fat_without_gland",
            "",
        ],
    )

    gland_path = find_matching_nifti(
        gland_dir,
        pid,
        preferred_suffixes=[
            "_t2w_gland_corrected",
            "_gland_corrected",
            "_t2w_gland",
            "_gland",
            "",
        ],
    )

    tzpz_path = find_matching_nifti(
        tzpz_dir,
        pid,
        preferred_suffixes=[
            "_tzpz",
            "_t2w",
            "",
        ],
    )

    print(
        f"[resolve] pid={pid}\n"
        f"  T2W : {t2w_path if t2w_path else 'MISS'}\n"
        f"  PPF : {ppf_path if ppf_path else 'MISS'}\n"
        f"  GLAND : {gland_path if gland_path else 'MISS'}\n"
        f"  TZPZ : {tzpz_path if tzpz_path else 'MISS'}"
    )

    return t2w_path, ppf_path, gland_path, tzpz_path


# ---------------- reference prostate mask ----------------

def boundary_mask_from_ref(ref_mask: np.ndarray) -> np.ndarray:
    ref_mask = ref_mask.astype(bool)
    if not np.any(ref_mask):
        return np.zeros_like(ref_mask, dtype=bool)

    st = generate_binary_structure(3, 1)
    eroded = binary_erosion(ref_mask, structure=st, iterations=1, border_value=0)
    boundary = ref_mask & (~eroded)
    return boundary


def distance_to_ref_boundary_mm(ref_mask: np.ndarray, spacing_mm: np.ndarray) -> np.ndarray | None:
    boundary = boundary_mask_from_ref(ref_mask)
    if not np.any(boundary):
        return None
    dist = distance_transform_edt(~boundary, sampling=spacing_mm)
    return dist


def build_ref_mask_from_sources(
    t2w_img: nib.Nifti1Image,
    gland_path: Path | None,
    tzpz_path: Path | None,
) -> tuple[np.ndarray | None, str | None]:
    if gland_path is not None:
        gland_img = load_canonical_img(gland_path)
        if imgs_same_grid(gland_img, t2w_img):
            gland_arr = get_array_from_img(gland_img)
            ref_mask = (gland_arr > 0).astype(np.uint8)
        else:
            ref_mask = resample_mask_to_ref(gland_img, t2w_img)

        if np.sum(ref_mask) > 0:
            return ref_mask, "gland"

    if tzpz_path is not None:
        tzpz_img = load_canonical_img(tzpz_path)
        if imgs_same_grid(tzpz_img, t2w_img):
            tzpz_arr = get_array_from_img(tzpz_img)
            tzpz_arr = np.rint(tzpz_arr).astype(np.int16)
        else:
            tzpz_arr = resample_label_to_ref(tzpz_img, t2w_img)

        # assumes 1 = TZ, 2 = PZ
        ref_mask = ((tzpz_arr == 1) | (tzpz_arr == 2)).astype(np.uint8)

        if np.sum(ref_mask) > 0:
            return ref_mask, "tzpz_union"

    return None, None


# ---------------- feature blocks ----------------

def ppf_volume_features(ppf_mask: np.ndarray, ref_mask: np.ndarray, spacing_mm: np.ndarray) -> dict:
    ppf_vol_mm3 = mask_volume_mm3(ppf_mask, spacing_mm)
    ref_vol_mm3 = mask_volume_mm3(ref_mask, spacing_mm)

    return {
        "prostate_ref_vol_mm3": float(ref_vol_mm3),
        "ppf_vol_mm3": float(ppf_vol_mm3),
        "ppf_to_prostate_ref_vol_ratio": float(ppf_vol_mm3 / ref_vol_mm3) if ref_vol_mm3 > 0 else np.nan,
    }


def ppf_t2w_features(t2w_norm: np.ndarray, ppf_mask: np.ndarray) -> dict:
    vals = t2w_norm[ppf_mask > 0]
    stats = first_order_stats(vals)

    gx = sobel(t2w_norm, axis=0)
    gy = sobel(t2w_norm, axis=1)
    gz = sobel(t2w_norm, axis=2)
    edge = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
    edge_vals = edge[ppf_mask > 0]

    out = {f"ppf_t2w_{k}": v for k, v in stats.items()}
    out["ppf_t2w_edge_mean"] = safe_mean(edge_vals)
    out["ppf_t2w_edge_p90"] = percentile_or_nan(edge_vals, 90)
    return out


def ppf_thickness_features(ppf_mask: np.ndarray, ref_mask: np.ndarray, spacing_mm: np.ndarray) -> dict:
    nan_out = {
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

    out = {
        "ppf_thick_mean_mm": float(np.mean(dvals)),
        "ppf_thick_std_mm": float(np.std(dvals)),
        "ppf_thick_p50_mm": percentile_or_nan(dvals, 50),
        "ppf_thick_p75_mm": percentile_or_nan(dvals, 75),
        "ppf_thick_p90_mm": percentile_or_nan(dvals, 90),
        "ppf_thick_p95_mm": percentile_or_nan(dvals, 95),
        "ppf_thick_max_mm": float(np.max(dvals)),
    }

    ref_idx = np.argwhere(ref_mask)
    center = ref_idx.mean(axis=0)

    dx = ppf_idx[:, 0] - center[0]
    dy = ppf_idx[:, 1] - center[1]

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

    return out


# ---------------- per-case extraction ----------------

def extract_ppf_features_for_pid(
    pid: str,
    t2w_dir: Path,
    ppf_dir: Path,
    gland_dir: Path | None,
    tzpz_dir: Path | None,
) -> tuple[dict | None, str | None]:
    t2w_path, ppf_path, gland_path, tzpz_path = resolve_case_paths(
        pid, t2w_dir, ppf_dir, gland_dir, tzpz_dir
    )

    if t2w_path is None:
        return None, "missing_t2w"
    if ppf_path is None:
        return None, "missing_ppf"

    t2w_img = load_canonical_img(t2w_path)
    t2w = get_array_from_img(t2w_img)
    if t2w.ndim != 3:
        return None, f"t2w_not_3d_shape_{t2w.shape}"

    spacing_mm = get_spacing_mm(t2w_img)

    ppf_img = load_canonical_img(ppf_path)
    if imgs_same_grid(ppf_img, t2w_img):
        ppf_arr = get_array_from_img(ppf_img)
        ppf_mask = (ppf_arr > 0).astype(np.uint8)
    else:
        ppf_mask = resample_mask_to_ref(ppf_img, t2w_img)

    if np.sum(ppf_mask) == 0:
        return None, "empty_ppf_after_resampling"

    ref_mask, ref_source = build_ref_mask_from_sources(t2w_img, gland_path, tzpz_path)
    if ref_mask is None or np.sum(ref_mask) == 0:
        return None, "missing_or_empty_gland_and_tzpz_reference"

    t2w_norm = robust_normalize_t2w(t2w)

    rec = {"patient_id": pid, "prostate_ref_source": ref_source}
    rec.update(ppf_volume_features(ppf_mask, ref_mask, spacing_mm))
    rec.update(ppf_thickness_features(ppf_mask, ref_mask, spacing_mm))
    rec.update(ppf_t2w_features(t2w_norm, ppf_mask))
    return rec, None


# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser(
        description="Standalone PPF-only feature extraction with gland->TZPZ fallback."
    )
    ap.add_argument("--t2w_dir", required=True, type=str, help="Directory containing T2W NIfTI files")
    ap.add_argument("--ppf_dir", required=True, type=str, help="Directory containing PPF mask NIfTI files")
    ap.add_argument("--excel_path", required=True, type=str, help="CSV file containing patient_id column")
    ap.add_argument("--output_csv", required=True, type=str, help="Output CSV path")
    ap.add_argument("--gland_dir", default=None, type=str, help="Optional directory containing gland masks")
    ap.add_argument("--tzpz_dir", default=None, type=str, help="Optional directory containing TZ/PZ masks")
    ap.add_argument("--skipped_csv", default=None, type=str, help="Optional CSV path for skipped/incomplete cases")
    ap.add_argument("--delimiter", default=",", type=str, help="CSV delimiter (default: ,)")
    args = ap.parse_args()

    t2w_dir = Path(args.t2w_dir)
    ppf_dir = Path(args.ppf_dir)
    excel_path = Path(args.excel_path)
    output_csv = Path(args.output_csv)
    gland_dir = Path(args.gland_dir) if args.gland_dir else None
    tzpz_dir = Path(args.tzpz_dir) if args.tzpz_dir else None

    if not t2w_dir.exists():
        print(f"Missing directory: t2w_dir -> {t2w_dir}", file=sys.stderr)
        sys.exit(1)
    if not ppf_dir.exists():
        print(f"Missing directory: ppf_dir -> {ppf_dir}", file=sys.stderr)
        sys.exit(1)
    if gland_dir is not None and not gland_dir.exists():
        print(f"Missing directory: gland_dir -> {gland_dir}", file=sys.stderr)
        sys.exit(1)
    if tzpz_dir is not None and not tzpz_dir.exists():
        print(f"Missing directory: tzpz_dir -> {tzpz_dir}", file=sys.stderr)
        sys.exit(1)
    if gland_dir is None and tzpz_dir is None:
        print("At least one of --gland_dir or --tzpz_dir must be provided.", file=sys.stderr)
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

    records = []
    skipped = []

    # --- FIXED: use both patient_id and study_id for correct filename detection ---
    study_id_col = None
    for alt in ["study_id", "studyID", "StudyID", "study"]:
        if alt in df.columns:
            study_id_col = alt
            break

    records = []
    skipped = []

    def find_file_with_study_patient(base_dir, study_id, patient_id, suffix_list=None):
        """Look for files named like study_patient[_suffix].nii.gz or patient_study[_suffix].nii.gz"""
        if not base_dir or not Path(base_dir).exists():
            return None
        study_str = normalize_pid(study_id)
        patient_str = normalize_pid(patient_id)
        if not study_str or not patient_str:
            return None
        if suffix_list is None:
            suffix_list = ["", "_0000", "_t2w", "_ppf", "_tzpz", "_gland"]

        candidates = [
            f"{study_str}_{patient_str}",
            f"{patient_str}_{study_str}",
        ]
        for cand in candidates:
            for suf in suffix_list:
                for ext in (".nii.gz", ".nii"):
                    p = Path(base_dir) / f"{cand}{suf}{ext}"
                    if p.exists():
                        return p
        return None

    for _, row in df.iterrows():
        pid = normalize_pid(row.get("patient_id"))
        sid = normalize_pid(row.get(study_id_col)) if study_id_col else None
        if not pid:
            continue

        # Use the helper to match files following your naming convention
        t2w_path  = find_file_with_study_patient(t2w_dir,  sid, pid, ["_0000", "_t2w", ""])
        ppf_path  = find_file_with_study_patient(ppf_dir,  sid, pid, ["_ppf", "", "_t2w_ppf"])
        gland_path = find_file_with_study_patient(gland_dir, sid, pid, ["_gland", "_t2w_gland"]) if gland_dir else None
        tzpz_path  = find_file_with_study_patient(tzpz_dir, sid, pid, ["_tzpz", "", "_t2w"]) if tzpz_dir else None

        print(f"[resolve] pid={pid}, sid={sid}")
        print(f"  T2W : {t2w_path if t2w_path else 'MISS'}")
        print(f"  PPF : {ppf_path if ppf_path else 'MISS'}")
        print(f"  GLAND : {gland_path if gland_path else 'MISS'}")
        print(f"  TZPZ : {tzpz_path if tzpz_path else 'MISS'}")

        if (not t2w_path) or (not ppf_path):
            skipped.append({
                "patient_id": pid,
                "study_id": sid,
                "reason": "missing_t2w_or_ppf"
            })
            continue

        # Load, normalize, and extract features
        try:
            t2w_img = load_canonical_img(t2w_path)
            t2w = get_array_from_img(t2w_img)
            spacing_mm = get_spacing_mm(t2w_img)

            ppf_img = load_canonical_img(ppf_path)
            if imgs_same_grid(ppf_img, t2w_img):
                ppf_arr = get_array_from_img(ppf_img)
                ppf_mask = (ppf_arr > 0).astype(np.uint8)
            else:
                ppf_mask = resample_mask_to_ref(ppf_img, t2w_img)

            if np.sum(ppf_mask) == 0:
                skipped.append({"patient_id": pid, "study_id": sid, "reason": "empty_ppf"})
                continue

            ref_mask, ref_source = build_ref_mask_from_sources(t2w_img, gland_path, tzpz_path)
            if ref_mask is None or np.sum(ref_mask) == 0:
                skipped.append({"patient_id": pid, "study_id": sid, "reason": "missing_ref_mask"})
                continue

            t2w_norm = robust_normalize_t2w(t2w)
            rec = {
                "patient_id": pid,
                "study_id": sid,
                "prostate_ref_source": ref_source
            }
            rec.update(ppf_volume_features(ppf_mask, ref_mask, spacing_mm))
            rec.update(ppf_thickness_features(ppf_mask, ref_mask, spacing_mm))
            rec.update(ppf_t2w_features(t2w_norm, ppf_mask))
            records.append(rec)
            print(f"[done] {sid}_{pid}")

        except Exception as e:
            skipped.append({"patient_id": pid, "study_id": sid, "reason": repr(e)})
            continue


    if skipped:
        print(f"[summary] skipped/incomplete cases: {len(skipped)}")
        print(f"[summary] first few skipped: {skipped[:10]}")

        skipped_df = pd.DataFrame(skipped)
        skipped_csv = Path(args.skipped_csv) if args.skipped_csv else output_csv.with_name(output_csv.stem + "_skipped.csv")
        skipped_df.to_csv(skipped_csv, index=False)
        print(f"[saved] skipped cases CSV: {skipped_csv}")

    if not records:
        print("No PPF features extracted. Exiting.")
        sys.exit(0)

    out_df = pd.DataFrame(records)
    out_df.to_csv(output_csv, index=False)
    print(f"[saved] {output_csv}")
    print(f"[summary] extracted {len(out_df)} cases with {out_df.shape[1] - 2} PPF feature columns")


if __name__ == "__main__":
    main()