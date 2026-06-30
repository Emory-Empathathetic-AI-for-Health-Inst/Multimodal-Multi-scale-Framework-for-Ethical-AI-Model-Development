#!/usr/bin/env python3
"""
SV geometry-only features from nnUNet binary masks (NO T2W), with auto Left/Right split.

If the SV mask has a single label (binary 0/1), this script derives left/right lobes by:
  - Connected components: if >=2 components, use the 2 largest.
  - If only 1 component, split into left/right using KMeans on x-coordinate (robust fallback).

Left vs Right assignment:
  - computed from centroids in mm along x-axis (x < mid_x => "left", else "right")

Outputs per-case CSV:
- left/right/total volumes (mL)
- surface area + sphericity (requires scikit-image)
- elongation/flatness/major-axis (PCA on voxel coords)
- asymmetry index + centroid distance L-R
- (optional) prostate masks: prostate volume, SV/prostate ratio, SV centroid to prostate centroid distance

USAGE (your case: binary masks with label=1):
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


def resample_to_ref(moving: sitk.Image, ref: sitk.Image, interp=sitk.sitkNearestNeighbor) -> sitk.Image:
    return sitk.Resample(
        moving, ref, sitk.Transform(), interp,
        moving.GetOrigin(), ref.GetSpacing(), moving.GetDirection(),
        0, moving.GetPixelIDValue()
    )


def voxel_volume_mm3(img: sitk.Image) -> float:
    sx, sy, sz = img.GetSpacing()
    return float(sx * sy * sz)


def centroid_mm(binary_zyx: np.ndarray, spacing_xyz: Tuple[float, float, float]) -> Tuple[float, float, float]:
    idx = np.argwhere(binary_zyx > 0)  # z,y,x
    if idx.size == 0:
        return (np.nan, np.nan, np.nan)
    zyx = idx.mean(axis=0)
    sx, sy, sz = spacing_xyz
    return (float(zyx[2] * sx), float(zyx[1] * sy), float(zyx[0] * sz))


def euclidean(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    if any(np.isnan(x) for x in a) or any(np.isnan(x) for x in b):
        return float("nan")
    return float(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2))


def pca_axes_metrics(binary_zyx: np.ndarray, spacing_xyz: Tuple[float, float, float]) -> Dict[str, float]:
    pts = np.argwhere(binary_zyx > 0)  # z,y,x

    # 🔥 critical fix: too few points
    if pts.shape[0] < 5:
        return {
            "major_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan
        }

    sx, sy, sz = spacing_xyz
    pts_mm = np.stack([pts[:, 2]*sx, pts[:, 1]*sy, pts[:, 0]*sz], axis=1)

    pts_mm -= pts_mm.mean(axis=0, keepdims=True)

    try:
        cov = np.cov(pts_mm.T)

        # additional safety
        if np.isnan(cov).any() or np.isinf(cov).any():
            raise ValueError("Invalid covariance matrix")

        w, _ = np.linalg.eigh(cov)

    except Exception:
        return {
            "major_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan
        }

    w = np.sort(w)[::-1]

    if w[0] <= 0:
        return {
            "major_axis_mm": np.nan,
            "elongation": np.nan,
            "flatness": np.nan
        }

    return {
        "major_axis_mm": float(4.0 * math.sqrt(max(w[0], 0.0))),
        "elongation": float(math.sqrt(max(w[1], 0.0) / w[0])) if w[1] >= 0 else np.nan,
        "flatness": float(math.sqrt(max(w[2], 0.0) / w[0])) if w[2] >= 0 else np.nan,
    }


def surface_area_mm2(binary_zyx: np.ndarray, spacing_xyz: Tuple[float, float, float]) -> float:
    if not _HAS_SKIMAGE or np.count_nonzero(binary_zyx) == 0:
        return float("nan")

    sx, sy, sz = spacing_xyz
    verts, faces, _, _ = marching_cubes(
        binary_zyx.astype(np.float32),
        level=0.5,
        spacing=(sz, sy, sx)
    )
    tri = verts[faces]
    a = tri[:, 1] - tri[:, 0]
    b = tri[:, 2] - tri[:, 0]
    return float(0.5 * np.linalg.norm(np.cross(a, b), axis=1).sum())


def sphericity(volume_mm3: float, surface_area_mm2: float) -> float:
    if volume_mm3 <= 0 or surface_area_mm2 <= 0 or np.isnan(volume_mm3) or np.isnan(surface_area_mm2):
        return float("nan")
    return float((math.pi ** (1 / 3)) * ((6.0 * volume_mm3) ** (2 / 3)) / surface_area_mm2)


def find_matching_mask(case_id: str, masks_dir: str) -> Optional[str]:
    for ext in [".nii.gz", ".nii"]:
        p = os.path.join(masks_dir, f"{case_id}{ext}")
        if os.path.exists(p):
            return p

    for p in iter_nii_files(masks_dir):
        if strip_nii_ext(os.path.basename(p)) == case_id:
            return p

    return None


def split_lr_from_binary(sv_bin_zyx: np.ndarray, spacing_xyz: Tuple[float, float, float]) -> Tuple[np.ndarray, np.ndarray, str]:
    """
    Returns (left_mask, right_mask, method_note).
    left/right decided by centroid x compared to mid_x (image center in mm).
    """
    cc = sitk.ConnectedComponent(sitk.GetImageFromArray(sv_bin_zyx.astype(np.uint8)))
    cc_arr = sitk.GetArrayFromImage(cc)  # z,y,x
    labels = np.unique(cc_arr)
    labels = labels[labels != 0]

    note = ""
    if labels.size >= 2:
        sizes = [(lab, int((cc_arr == lab).sum())) for lab in labels]
        sizes.sort(key=lambda x: x[1], reverse=True)
        lab1, lab2 = sizes[0][0], sizes[1][0]
        m1 = (cc_arr == lab1)
        m2 = (cc_arr == lab2)
        note = "LR from 2-largest connected components"
    else:
        if not _HAS_SKLEARN:
            raise RuntimeError(
                "Only one connected component found; need scikit-learn for KMeans split.\n"
                "Install: pip install scikit-learn"
            )

        pts = np.argwhere(sv_bin_zyx > 0)  # z,y,x
        if pts.shape[0] < 20:
            empty = np.zeros_like(sv_bin_zyx, dtype=bool)
            return sv_bin_zyx.astype(bool), empty, "Too few voxels to split; left=all"

        x = pts[:, 2:3].astype(np.float32)  # x index only
        km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(x)
        lab = km.labels_

        m1 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m2 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m1[pts[lab == 0, 0], pts[lab == 0, 1], pts[lab == 0, 2]] = True
        m2[pts[lab == 1, 0], pts[lab == 1, 1], pts[lab == 1, 2]] = True
        note = "LR from KMeans split (single component)"

    size_x = sv_bin_zyx.shape[2]
    mid_x_mm = ((size_x - 1) / 2.0) * spacing_xyz[0]

    c1 = centroid_mm(m1, spacing_xyz)
    c2 = centroid_mm(m2, spacing_xyz)

    if (not np.isnan(c1[0])) and (not np.isnan(c2[0])) and (c1[0] <= c2[0]):
        left, right = m1, m2
    else:
        left, right = m2, m1

    if (not np.isnan(c1[0])) and (not np.isnan(c2[0])):
        if (c1[0] < mid_x_mm and c2[0] < mid_x_mm) or (c1[0] > mid_x_mm and c2[0] > mid_x_mm):
            note += " (both centroids on same side of midline; check orientation)"

    return left.astype(bool), right.astype(bool), note


def part_metrics(binary_zyx: np.ndarray, spacing_xyz: Tuple[float, float, float], vx_mm3: float) -> Dict[str, float]:
    nvox = int(np.count_nonzero(binary_zyx))
    vol_mm3 = nvox * vx_mm3
    vol_ml = vol_mm3 / 1000.0
    sa = surface_area_mm2(binary_zyx, spacing_xyz)
    sph = sphericity(vol_mm3, sa)
    pca = pca_axes_metrics(binary_zyx, spacing_xyz)
    cen = centroid_mm(binary_zyx, spacing_xyz)

    return {
        "voxel_count": nvox,
        "volume_ml": vol_ml,
        "surface_area_mm2": sa,
        "sphericity": sph,
        "elongation": pca["elongation"],
        "flatness": pca["flatness"],
        "major_axis_mm": pca["major_axis_mm"],
        "centroid_x_mm": cen[0],
        "centroid_y_mm": cen[1],
        "centroid_z_mm": cen[2],
    }


def compute_one(
    sv_mask_path: str,
    sv_label: int,
    derive_lr: bool,
    prostate_mask_path: Optional[str] = None,
) -> Dict[str, float]:

    sv_img = read_image(sv_mask_path)
    sv_arr = sitk.GetArrayFromImage(sv_img).astype(np.int32)  # z,y,x
    spacing = sv_img.GetSpacing()  # x,y,z
    vx_mm3 = voxel_volume_mm3(sv_img)

    sv_bin = (sv_arr == sv_label)

    out: Dict[str, float] = {}
    out["notes"] = ""

    if derive_lr:
        left, right, note = split_lr_from_binary(sv_bin, spacing)
        out["notes"] = note

        m_total = sv_bin
        L = part_metrics(left, spacing, vx_mm3)
        R = part_metrics(right, spacing, vx_mm3)
        T = part_metrics(m_total, spacing, vx_mm3)

        for k, v in L.items():
            out[f"sv_left_{k}"] = v
        for k, v in R.items():
            out[f"sv_right_{k}"] = v
        for k, v in T.items():
            out[f"sv_total_{k}"] = v

        lv, rv = out["sv_left_volume_ml"], out["sv_right_volume_ml"]
        out["sv_asymmetry_index_volume"] = float(abs(lv - rv) / (lv + rv)) if (lv + rv) > 0 else np.nan

        lc = (
            out["sv_left_centroid_x_mm"],
            out["sv_left_centroid_y_mm"],
            out["sv_left_centroid_z_mm"]
        )
        rc = (
            out["sv_right_centroid_x_mm"],
            out["sv_right_centroid_y_mm"],
            out["sv_right_centroid_z_mm"]
        )
        out["sv_centroid_distance_lr_mm"] = euclidean(lc, rc)

    else:
        T = part_metrics(sv_bin, spacing, vx_mm3)
        for k, v in T.items():
            out[f"sv_total_{k}"] = v

        for side in ["sv_left", "sv_right"]:
            for k in [
                "voxel_count", "volume_ml", "surface_area_mm2", "sphericity",
                "elongation", "flatness", "major_axis_mm",
                "centroid_x_mm", "centroid_y_mm", "centroid_z_mm"
            ]:
                out[f"{side}_{k}"] = np.nan

        out["sv_asymmetry_index_volume"] = np.nan
        out["sv_centroid_distance_lr_mm"] = np.nan

    out["prostate_volume_ml"] = np.nan
    out["sv_to_prostate_volume_ratio"] = np.nan
    out["sv_centroid_to_prostate_centroid_mm"] = np.nan

    if prostate_mask_path and os.path.exists(prostate_mask_path):
        p_img = read_image(prostate_mask_path)
        if (
            (p_img.GetSize() != sv_img.GetSize()) or
            (p_img.GetSpacing() != sv_img.GetSpacing()) or
            (p_img.GetDirection() != sv_img.GetDirection()) or
            (p_img.GetOrigin() != sv_img.GetOrigin())
        ):
            p_img = resample_to_ref(p_img, sv_img, interp=sitk.sitkNearestNeighbor)

        p_arr = sitk.GetArrayFromImage(p_img)
        p_bin = (p_arr > 0)

        p_nvox = int(np.count_nonzero(p_bin))
        p_vol_ml = (p_nvox * vx_mm3) / 1000.0
        out["prostate_volume_ml"] = p_vol_ml

        sv_tot = out.get("sv_total_volume_ml", np.nan)
        if not np.isnan(sv_tot) and p_vol_ml > 0:
            out["sv_to_prostate_volume_ratio"] = float(sv_tot / p_vol_ml)

        sv_c = (
            out["sv_total_centroid_x_mm"],
            out["sv_total_centroid_y_mm"],
            out["sv_total_centroid_z_mm"]
        )
        p_c = centroid_mm(p_bin, spacing)
        out["sv_centroid_to_prostate_centroid_mm"] = euclidean(sv_c, p_c)

    if not _HAS_SKIMAGE:
        out["notes"] = (out["notes"] + "; " if out["notes"] else "") + "surface_area/sphericity require scikit-image"

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sv_masks_dir", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--sv_label", type=int, default=1, help="Label value representing SV in mask (default=1).")
    ap.add_argument("--derive_lr", action="store_true", help="Derive left/right SV from binary mask.")
    ap.add_argument("--prostate_masks_dir", default=None, help="Optional prostate masks dir for ratio/distance.")
    args = ap.parse_args()

    sv_paths = iter_nii_files(args.sv_masks_dir)
    if not sv_paths:
        raise SystemExit(f"No .nii/.nii.gz found under: {args.sv_masks_dir}")

    print(f"Found {len(sv_paths)} mask files under: {args.sv_masks_dir}")

    rows = []

    if _HAS_TQDM:
        iterator = tqdm(sv_paths, desc="Processing SV masks", unit="case")
    else:
        print("tqdm not installed. Progress bar disabled. Install with: python -m pip install tqdm")
        iterator = sv_paths

    total_cases = len(sv_paths)

    for i, sv_mask_path in enumerate(iterator, start=1):
        case_id = strip_nii_ext(os.path.basename(sv_mask_path))

        if _HAS_TQDM:
            tqdm.write(f"[{i}/{total_cases}] Processing: {case_id}")
        else:
            print(f"[{i}/{total_cases}] Processing: {case_id}")

        prostate_mask_path = None
        if args.prostate_masks_dir:
            prostate_mask_path = find_matching_mask(case_id, args.prostate_masks_dir)

        feats = compute_one(
            sv_mask_path=sv_mask_path,
            sv_label=args.sv_label,
            derive_lr=args.derive_lr,
            prostate_mask_path=prostate_mask_path,
        )

        row = {
            "case_id": case_id,
            "sv_mask_path": sv_mask_path,
            "sv_label": args.sv_label,
            "derive_lr": int(args.derive_lr)
        }
        row.update(feats)
        rows.append(row)

    base_cols = ["case_id", "sv_mask_path", "sv_label", "derive_lr"]
    other_cols = sorted([c for c in rows[0].keys() if c not in base_cols])
    cols = base_cols + other_cols

    os.makedirs(os.path.dirname(os.path.abspath(args.out_csv)) or ".", exist_ok=True)
    with open(args.out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    print(f"Wrote {len(rows)} rows to: {args.out_csv}")


if __name__ == "__main__":
    main()