#!/usr/bin/env python3
"""
SV geometry-only features from nnUNet binary masks (NO T2W), with auto Left/Right split.

If the SV mask has a single label (binary 0/1), this script derives left/right lobes by:
  - Connected components: if >=2 components, use the 2 largest.
  - If only 1 component, split into left/right using KMeans on x-coordinate (robust fallback).

Left vs Right assignment:
  - Assumes LPS orientation (standard DICOM/ITK): smaller x => "left", larger x => "right".
  - If your pipeline reorients to RAS, left/right will be swapped — verify with a known case.

Outputs per-case CSV:
  - left/right/total volumes (mL)
  - surface area + sphericity
  - elongation / flatness / major-axis / minor-axis ratio (PCA)
  - asymmetry indices (volume, surface area, major axis)
  - centroid distance L-R + L-R split confidence (x-distance in mm)
  - bounding box dimensions (W x H x D) and craniocaudal length
  - (optional) prostate masks: prostate volume, SV/prostate ratio, SV centroid to prostate centroid distance

USAGE:
  python sv_geometry_from_mask_autolr.py \
    --sv_masks_dir /path/pred_sv \
    --out_csv sv_geom_lr.csv \
    --sv_label 1 \
    --derive_lr

Optional prostate:
  --prostate_masks_dir /path/pred_prostate
"""

import os
import csv
import math
import argparse
from typing import Dict, Optional, Tuple, List

import numpy as np
import SimpleITK as sitk

try:
    from skimage.measure import marching_cubes
    _HAS_SKIMAGE = True
except Exception:
    _HAS_SKIMAGE = False

try:
    from sklearn.cluster import KMeans
    _HAS_SKLEARN = True
except Exception:
    _HAS_SKLEARN = False

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except Exception:
    _HAS_TQDM = False


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def iter_nii_files(root: str) -> List[str]:
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".nii") or fn.endswith(".nii.gz"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def strip_nii_ext(name: str) -> str:
    if name.endswith(".nii.gz"):
        return name[:-7]
    if name.endswith(".nii"):
        return name[:-4]
    return name


def read_image(path: str) -> sitk.Image:
    return sitk.ReadImage(path)


def resample_to_ref(
    moving: sitk.Image,
    ref: sitk.Image,
    interp=sitk.sitkNearestNeighbor,
) -> sitk.Image:
    """
    Resample `moving` into the physical space of `ref`.
    Uses the correct 2-argument Resample overload to avoid origin/spacing bugs.
    """
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(ref)
    resampler.SetInterpolator(interp)
    resampler.SetDefaultPixelValue(0)
    resampler.SetOutputPixelType(moving.GetPixelIDValue())
    return resampler.Execute(moving)


def voxel_volume_mm3(img: sitk.Image) -> float:
    sx, sy, sz = img.GetSpacing()
    return float(sx * sy * sz)


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

def centroid_mm(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    idx = np.argwhere(binary_zyx > 0)  # rows: z, y, x
    if idx.size == 0:
        return (np.nan, np.nan, np.nan)
    zyx = idx.mean(axis=0)
    sx, sy, sz = spacing_xyz
    return (float(zyx[2] * sx), float(zyx[1] * sy), float(zyx[0] * sz))


def euclidean(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
) -> float:
    if any(np.isnan(x) for x in a) or any(np.isnan(x) for x in b):
        return float("nan")
    return float(math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b))))


def pca_axes_metrics(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Dict[str, float]:
    pts = np.argwhere(binary_zyx > 0)  # z, y, x

    if pts.shape[0] < 5:
        return {
            "major_axis_mm": np.nan,
            "minor_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan,
            "axis_ratio": np.nan,
        }

    sx, sy, sz = spacing_xyz
    pts_mm = np.stack([pts[:, 2] * sx, pts[:, 1] * sy, pts[:, 0] * sz], axis=1)
    pts_mm -= pts_mm.mean(axis=0, keepdims=True)

    try:
        cov = np.cov(pts_mm.T)
        if np.isnan(cov).any() or np.isinf(cov).any():
            raise ValueError("Invalid covariance matrix")
        w, _ = np.linalg.eigh(cov)
    except Exception:
        return {
            "major_axis_mm": np.nan,
            "minor_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan,
            "axis_ratio": np.nan,
        }

    w = np.sort(w)[::-1]  # descending: w[0]=major, w[1]=mid, w[2]=minor

    if w[0] <= 0:
        return {
            "major_axis_mm": np.nan,
            "minor_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan,
            "axis_ratio": np.nan,
        }

    major = float(4.0 * math.sqrt(max(w[0], 0.0)))
    minor = float(4.0 * math.sqrt(max(w[2], 0.0)))

    return {
        # 4*sqrt(eigenvalue) gives the axis length in the same sense as
        # the standard ellipsoid semi-axis approximation
        "major_axis_mm": major,
        "minor_axis_mm": minor,
        # elongation: how far from a sphere along the principal axis
        "elongation": float(math.sqrt(max(w[1], 0.0) / w[0])) if w[1] >= 0 else np.nan,
        # flatness: compression along the smallest axis
        "flatness": float(math.sqrt(max(w[2], 0.0) / w[0])) if w[2] >= 0 else np.nan,
        # direct ratio of minor to major — intuitive for aging studies
        "axis_ratio": float(minor / major) if major > 0 else np.nan,
    }


def surface_area_mm2(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> float:
    """
    Marching-cubes surface area.
    Array is z,y,x so spacing tuple passed to marching_cubes is (sz, sy, sx).
    """
    if not _HAS_SKIMAGE or np.count_nonzero(binary_zyx) == 0:
        return float("nan")

    sx, sy, sz = spacing_xyz
    try:
        verts, faces, _, _ = marching_cubes(
            binary_zyx.astype(np.float32),
            level=0.5,
            spacing=(sz, sy, sx),   # matches z,y,x array axis order
        )
    except Exception:
        return float("nan")

    tri = verts[faces]
    a = tri[:, 1] - tri[:, 0]
    b = tri[:, 2] - tri[:, 0]
    return float(0.5 * np.linalg.norm(np.cross(a, b), axis=1).sum())


def sphericity(volume_mm3: float, sa_mm2: float) -> float:
    if volume_mm3 <= 0 or sa_mm2 <= 0 or np.isnan(volume_mm3) or np.isnan(sa_mm2):
        return float("nan")
    return float((math.pi ** (1.0 / 3.0)) * ((6.0 * volume_mm3) ** (2.0 / 3.0)) / sa_mm2)


def bounding_box_mm(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Dict[str, float]:
    """
    Returns width (x), height (y), depth/craniocaudal (z) in mm,
    derived from the axis-aligned bounding box of foreground voxels.
    """
    pts = np.argwhere(binary_zyx > 0)
    if pts.shape[0] == 0:
        return {"bbox_width_mm": np.nan, "bbox_height_mm": np.nan, "bbox_depth_mm": np.nan}

    sx, sy, sz = spacing_xyz
    z_min, y_min, x_min = pts.min(axis=0)
    z_max, y_max, x_max = pts.max(axis=0)

    return {
        "bbox_width_mm":  float((x_max - x_min + 1) * sx),   # x
        "bbox_height_mm": float((y_max - y_min + 1) * sy),   # y
        "bbox_depth_mm":  float((z_max - z_min + 1) * sz),   # z (craniocaudal)
    }


# ---------------------------------------------------------------------------
# L/R splitting
# ---------------------------------------------------------------------------

def split_lr_from_binary(
    sv_bin_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Tuple[np.ndarray, np.ndarray, str]:
    """
    Returns (left_mask, right_mask, method_note).

    Orientation assumption: LPS (standard DICOM/ITK).
      smaller x in voxel space => patient left
    """
    cc_img = sitk.ConnectedComponent(
        sitk.GetImageFromArray(sv_bin_zyx.astype(np.uint8))
    )
    cc_arr = sitk.GetArrayFromImage(cc_img)  # z,y,x; metadata discarded intentionally
    labels = np.unique(cc_arr)
    labels = labels[labels != 0]

    note = ""

    if labels.size >= 2:
        sizes = sorted(
            [(lab, int((cc_arr == lab).sum())) for lab in labels],
            key=lambda x: x[1],
            reverse=True,
        )
        lab1, lab2 = sizes[0][0], sizes[1][0]
        m1 = (cc_arr == lab1).astype(bool)
        m2 = (cc_arr == lab2).astype(bool)
        note = "LR_from_connected_components"

    else:
        if not _HAS_SKLEARN:
            raise RuntimeError(
                "Only one connected component; need scikit-learn for KMeans split.\n"
                "Install: pip install scikit-learn"
            )
        pts = np.argwhere(sv_bin_zyx > 0)
        if pts.shape[0] < 20:
            empty = np.zeros_like(sv_bin_zyx, dtype=bool)
            return sv_bin_zyx.astype(bool), empty, "too_few_voxels_left_equals_all"

        x_idx = pts[:, 2:3].astype(np.float32)
        km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(x_idx)
        lbl = km.labels_

        m1 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m2 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m1[pts[lbl == 0, 0], pts[lbl == 0, 1], pts[lbl == 0, 2]] = True
        m2[pts[lbl == 1, 0], pts[lbl == 1, 1], pts[lbl == 1, 2]] = True
        note = "LR_from_KMeans_single_component"

    # Assign left = smaller centroid x (LPS convention)
    c1 = centroid_mm(m1, spacing_xyz)
    c2 = centroid_mm(m2, spacing_xyz)

    if (not np.isnan(c1[0])) and (not np.isnan(c2[0])):
        left, right = (m1, m2) if c1[0] <= c2[0] else (m2, m1)
        cl = centroid_mm(left, spacing_xyz)
        cr = centroid_mm(right, spacing_xyz)

        # Warn if both components are on the same side of the image midline
        size_x = sv_bin_zyx.shape[2]
        mid_x_mm = ((size_x - 1) / 2.0) * spacing_xyz[0]
        if (cl[0] < mid_x_mm) == (cr[0] < mid_x_mm):
            note += ";BOTH_CENTROIDS_SAME_SIDE_CHECK_ORIENTATION"
    else:
        left, right = m1, m2

    return left.astype(bool), right.astype(bool), note


# ---------------------------------------------------------------------------
# Per-region metrics bundle
# ---------------------------------------------------------------------------

def part_metrics(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
    vx_mm3: float,
) -> Dict[str, float]:
    nvox = int(np.count_nonzero(binary_zyx))
    vol_mm3 = nvox * vx_mm3
    vol_ml = vol_mm3 / 1000.0
    sa = surface_area_mm2(binary_zyx, spacing_xyz)
    sph = sphericity(vol_mm3, sa)
    pca = pca_axes_metrics(binary_zyx, spacing_xyz)
    cen = centroid_mm(binary_zyx, spacing_xyz)
    bb = bounding_box_mm(binary_zyx, spacing_xyz)

    return {
        "voxel_count":       nvox,
        "volume_ml":         vol_ml,
        "surface_area_mm2":  sa,
        "sphericity":        sph,
        "elongation":        pca["elongation"],
        "flatness":          pca["flatness"],
        "major_axis_mm":     pca["major_axis_mm"],
        "minor_axis_mm":     pca["minor_axis_mm"],
        "axis_ratio":        pca["axis_ratio"],
        "centroid_x_mm":     cen[0],
        "centroid_y_mm":     cen[1],
        "centroid_z_mm":     cen[2],
        "bbox_width_mm":     bb["bbox_width_mm"],
        "bbox_height_mm":    bb["bbox_height_mm"],
        "bbox_depth_mm":     bb["bbox_depth_mm"],
    }


def safe_asymmetry(a: float, b: float) -> float:
    """|(a - b)| / (a + b), returns nan if sum is zero or either is nan."""
    if np.isnan(a) or np.isnan(b) or (a + b) == 0:
        return float("nan")
    return float(abs(a - b) / (a + b))


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_one(
    sv_mask_path: str,
    sv_label: int,
    derive_lr: bool,
    prostate_mask_path: Optional[str] = None,
) -> Dict:

    sv_img = read_image(sv_mask_path)
    sv_arr = sitk.GetArrayFromImage(sv_img).astype(np.int32)  # z,y,x
    spacing = sv_img.GetSpacing()                              # (sx, sy, sz)
    vx_mm3 = voxel_volume_mm3(sv_img)

    sv_bin = (sv_arr == sv_label)

    out: Dict = {"notes": ""}

    if derive_lr:
        left, right, note = split_lr_from_binary(sv_bin, spacing)
        out["notes"] = note

        L = part_metrics(left,   spacing, vx_mm3)
        R = part_metrics(right,  spacing, vx_mm3)
        T = part_metrics(sv_bin, spacing, vx_mm3)

        for k, v in L.items():
            out[f"sv_left_{k}"] = v
        for k, v in R.items():
            out[f"sv_right_{k}"] = v
        for k, v in T.items():
            out[f"sv_total_{k}"] = v

        # --- asymmetry indices (aging-relevant) ---
        out["sv_asymmetry_index_volume"]     = safe_asymmetry(L["volume_ml"],        R["volume_ml"])
        out["sv_asymmetry_index_surface"]    = safe_asymmetry(L["surface_area_mm2"], R["surface_area_mm2"])
        out["sv_asymmetry_index_major_axis"] = safe_asymmetry(L["major_axis_mm"],    R["major_axis_mm"])

        # --- L-R spatial relationship ---
        lc = (L["centroid_x_mm"], L["centroid_y_mm"], L["centroid_z_mm"])
        rc = (R["centroid_x_mm"], R["centroid_y_mm"], R["centroid_z_mm"])
        out["sv_centroid_distance_lr_mm"] = euclidean(lc, rc)

        # x-distance between centroids: simple split quality indicator
        if not (np.isnan(lc[0]) or np.isnan(rc[0])):
            out["sv_lr_split_confidence_x_mm"] = float(abs(rc[0] - lc[0]))
        else:
            out["sv_lr_split_confidence_x_mm"] = float("nan")

    else:
        T = part_metrics(sv_bin, spacing, vx_mm3)
        for k, v in T.items():
            out[f"sv_total_{k}"] = v

        nan_keys = [
            "voxel_count", "volume_ml", "surface_area_mm2", "sphericity",
            "elongation", "flatness", "major_axis_mm", "minor_axis_mm", "axis_ratio",
            "centroid_x_mm", "centroid_y_mm", "centroid_z_mm",
            "bbox_width_mm", "bbox_height_mm", "bbox_depth_mm",
        ]
        for side in ["sv_left", "sv_right"]:
            for k in nan_keys:
                out[f"{side}_{k}"] = np.nan

        out["sv_asymmetry_index_volume"]      = np.nan
        out["sv_asymmetry_index_surface"]     = np.nan
        out["sv_asymmetry_index_major_axis"]  = np.nan
        out["sv_centroid_distance_lr_mm"]     = np.nan
        out["sv_lr_split_confidence_x_mm"]    = np.nan

    # --- prostate-relative features (aging-relevant) ---
    out["prostate_volume_ml"]                    = np.nan
    out["sv_to_prostate_volume_ratio"]           = np.nan
    out["sv_centroid_to_prostate_centroid_mm"]   = np.nan

    if prostate_mask_path and os.path.exists(prostate_mask_path):
        p_img = read_image(prostate_mask_path)

        need_resample = (
            p_img.GetSize()      != sv_img.GetSize()      or
            p_img.GetSpacing()   != sv_img.GetSpacing()   or
            p_img.GetDirection() != sv_img.GetDirection() or
            p_img.GetOrigin()    != sv_img.GetOrigin()
        )
        if need_resample:
            p_img = resample_to_ref(p_img, sv_img, interp=sitk.sitkNearestNeighbor)

        p_arr = sitk.GetArrayFromImage(p_img)
        p_bin = (p_arr > 0)

        p_vol_ml = float(np.count_nonzero(p_bin) * vx_mm3 / 1000.0)
        out["prostate_volume_ml"] = p_vol_ml

        sv_tot = out.get("sv_total_volume_ml", np.nan)
        if not np.isnan(sv_tot) and p_vol_ml > 0:
            out["sv_to_prostate_volume_ratio"] = float(sv_tot / p_vol_ml)

        sv_c = (
            out["sv_total_centroid_x_mm"],
            out["sv_total_centroid_y_mm"],
            out["sv_total_centroid_z_mm"],
        )
        p_c = centroid_mm(p_bin, spacing)
        out["sv_centroid_to_prostate_centroid_mm"] = euclidean(sv_c, p_c)

    if not _HAS_SKIMAGE:
        warn = "surface_area/sphericity require scikit-image"
        out["notes"] = f"{out['notes']}; {warn}" if out["notes"] else warn

    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def find_matching_mask(case_id: str, masks_dir: str) -> Optional[str]:
    for ext in [".nii.gz", ".nii"]:
        p = os.path.join(masks_dir, f"{case_id}{ext}")
        if os.path.exists(p):
            return p
    for p in iter_nii_files(masks_dir):
        if strip_nii_ext(os.path.basename(p)) == case_id:
            return p
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Extract SV geometry features from binary nnUNet masks."
    )
    ap.add_argument("--sv_masks_dir",      required=True,  help="Directory with SV .nii/.nii.gz masks.")
    ap.add_argument("--out_csv",           required=True,  help="Output CSV path.")
    ap.add_argument("--sv_label",          type=int, default=1, help="Foreground label in SV mask (default: 1).")
    ap.add_argument("--derive_lr",         action="store_true", help="Derive left/right SV from binary mask.")
    ap.add_argument("--prostate_masks_dir", default=None,  help="Optional: directory with prostate masks.")
    args = ap.parse_args()

    sv_paths = iter_nii_files(args.sv_masks_dir)
    if not sv_paths:
        raise SystemExit(f"No .nii/.nii.gz files found under: {args.sv_masks_dir}")

    print(f"Found {len(sv_paths)} mask file(s) under: {args.sv_masks_dir}")
    print(f"scikit-image available : {_HAS_SKIMAGE}  (surface area / sphericity)")
    print(f"scikit-learn available : {_HAS_SKLEARN}  (KMeans L/R fallback)")

    rows = []
    iterator = (
        tqdm(sv_paths, desc="Processing SV masks", unit="case")
        if _HAS_TQDM else sv_paths
    )

    for i, sv_mask_path in enumerate(iterator, start=1):
        case_id = strip_nii_ext(os.path.basename(sv_mask_path))
        msg = f"[{i}/{len(sv_paths)}] {case_id}"
        (tqdm.write(msg) if _HAS_TQDM else print(msg))

        prostate_path = None
        if args.prostate_masks_dir:
            prostate_path = find_matching_mask(case_id, args.prostate_masks_dir)
            if prostate_path is None:
                print(f"  WARNING: no prostate mask found for {case_id}")

        try:
            feats = compute_one(
                sv_mask_path=sv_mask_path,
                sv_label=args.sv_label,
                derive_lr=args.derive_lr,
                prostate_mask_path=prostate_path,
            )
        except Exception as e:
            print(f"  ERROR on {case_id}: {e}")
            feats = {"notes": f"ERROR: {e}"}

        row = {
            "case_id":       case_id,
            "sv_mask_path":  sv_mask_path,
            "sv_label":      args.sv_label,
            "derive_lr":     int(args.derive_lr),
        }
        row.update(feats)
        rows.append(row)

    if not rows:
        raise SystemExit("No rows to write.")

    base_cols = ["case_id", "sv_mask_path", "sv_label", "derive_lr"]
    other_cols = sorted(c for c in rows[0] if c not in base_cols)
    cols = base_cols + other_cols

    out_dir = os.path.dirname(os.path.abspath(args.out_csv))
    os.makedirs(out_dir, exist_ok=True)

    with open(args.out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    print(f"\nWrote {len(rows)} row(s) to: {args.out_csv}")


if __name__ == "__main__":
    main()
