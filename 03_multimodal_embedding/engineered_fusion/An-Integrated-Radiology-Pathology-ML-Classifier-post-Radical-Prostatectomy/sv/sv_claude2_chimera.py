#!/usr/bin/env python3
"""
SV geometry + T2W texture features — fixed for Chimere naming convention:
  SV mask : {case_id}_0001_t2w.nii.gz
  T2W     : {case_id}_0001_t2w.nii.gz  (same stem, different folder)
  TZPZ    : {case_id}_0001_t2w.nii.gz  (same stem, different folder)

case_id extracted as the first underscore-split part (e.g. '1003').
"""

import os
import re
import csv
import math
import argparse
import warnings
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
    from scipy.stats import skew as scipy_skew, kurtosis as scipy_kurtosis
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

try:
    from skimage.feature import greycomatrix, greycoprops
    _HAS_GLCM = True
except Exception:
    _HAS_GLCM = False

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except Exception:
    _HAS_TQDM = False


# =============================================================================
# I/O helpers
# =============================================================================

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


def extract_case_id(stem: str) -> str:
    """
    Extract clean numeric case_id from Chimere filename stem.
    '1003_0001_t2w' -> '1003'
    '1003'          -> '1003'  (passthrough)
    """
    return stem.split("_")[0]


def read_image(path: str) -> sitk.Image:
    return sitk.ReadImage(path)


def resample_to_ref(
    moving: sitk.Image,
    ref: sitk.Image,
    interp=sitk.sitkNearestNeighbor,
) -> sitk.Image:
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(ref)
    resampler.SetInterpolator(interp)
    resampler.SetDefaultPixelValue(0)
    resampler.SetOutputPixelType(moving.GetPixelIDValue())
    return resampler.Execute(moving)


def voxel_volume_mm3(img: sitk.Image) -> float:
    sx, sy, sz = img.GetSpacing()
    return float(sx * sy * sz)


def find_matching_file(sv_stem: str, search_dir: str) -> Optional[str]:
    """
    Find file in search_dir matching sv_stem.
    Chimere convention: all folders share the same filename stem.

    sv_stem = '1003_0001_t2w'
    Looks for: search_dir/1003_0001_t2w.nii.gz  (exact, preferred)
    Fallback : any file whose stem starts with the numeric case_id part.
    """
    # 1. Exact match (same stem, different folder)
    for ext in [".nii.gz", ".nii"]:
        p = os.path.join(search_dir, f"{sv_stem}{ext}")
        if os.path.exists(p):
            return p

    # 2. Fallback: match by numeric case_id prefix
    cid = extract_case_id(sv_stem)
    for p in iter_nii_files(search_dir):
        file_stem = strip_nii_ext(os.path.basename(p))
        if file_stem.split("_")[0] == cid:
            return p

    return None


# =============================================================================
# Geometry primitives
# =============================================================================

def centroid_mm(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    idx = np.argwhere(binary_zyx > 0)
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
    nan_result = {
        "major_axis_mm": np.nan,
        "minor_axis_mm": np.nan,
        "elongation":    np.nan,
        "flatness":      np.nan,
        "axis_ratio":    np.nan,
    }

    pts = np.argwhere(binary_zyx > 0)
    if pts.shape[0] < 5:
        return nan_result

    sx, sy, sz = spacing_xyz
    pts_mm = np.stack([pts[:, 2] * sx, pts[:, 1] * sy, pts[:, 0] * sz], axis=1)
    pts_mm -= pts_mm.mean(axis=0, keepdims=True)

    try:
        cov = np.cov(pts_mm.T)
        if np.isnan(cov).any() or np.isinf(cov).any():
            raise ValueError("Invalid covariance")
        w, _ = np.linalg.eigh(cov)
    except Exception:
        return nan_result

    w = np.sort(w)[::-1]
    if w[0] <= 0:
        return nan_result

    major = float(4.0 * math.sqrt(max(w[0], 0.0)))
    minor = float(4.0 * math.sqrt(max(w[2], 0.0)))

    return {
        "major_axis_mm": major,
        "minor_axis_mm": minor,
        "elongation":    float(math.sqrt(max(w[1], 0.0) / w[0])) if w[1] >= 0 else np.nan,
        "flatness":      float(math.sqrt(max(w[2], 0.0) / w[0])) if w[2] >= 0 else np.nan,
        "axis_ratio":    float(minor / major) if major > 0 else np.nan,
    }


def surface_area_mm2(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> float:
    if not _HAS_SKIMAGE or np.count_nonzero(binary_zyx) == 0:
        return float("nan")
    sx, sy, sz = spacing_xyz
    try:
        verts, faces, _, _ = marching_cubes(
            binary_zyx.astype(np.float32),
            level=0.5,
            spacing=(sz, sy, sx),
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
    pts = np.argwhere(binary_zyx > 0)
    if pts.shape[0] == 0:
        return {"bbox_width_mm": np.nan, "bbox_height_mm": np.nan, "bbox_depth_mm": np.nan}
    sx, sy, sz = spacing_xyz
    z_min, y_min, x_min = pts.min(axis=0)
    z_max, y_max, x_max = pts.max(axis=0)
    return {
        "bbox_width_mm":  float((x_max - x_min + 1) * sx),
        "bbox_height_mm": float((y_max - y_min + 1) * sy),
        "bbox_depth_mm":  float((z_max - z_min + 1) * sz),
    }


def safe_asymmetry(a: float, b: float) -> float:
    if np.isnan(a) or np.isnan(b) or (a + b) == 0:
        return float("nan")
    return float(abs(a - b) / (a + b))


# =============================================================================
# T2W texture features
# =============================================================================

def _glcm_features_manual(patch: np.ndarray) -> Dict[str, float]:
    n_levels = 32
    vmin, vmax = patch.min(), patch.max()
    if vmax == vmin:
        return {
            "glcm_contrast":    0.0,
            "glcm_homogeneity": 1.0,
            "glcm_energy":      1.0,
            "glcm_correlation": float("nan"),
            "glcm_asm":         1.0,
        }

    quantized = ((patch - vmin) / (vmax - vmin) * (n_levels - 1)).astype(np.int32)
    glcm = np.zeros((n_levels, n_levels), dtype=np.float64)
    i_idx = quantized[:, :-1].ravel()
    j_idx = quantized[:, 1:].ravel()
    for i, j in zip(i_idx, j_idx):
        glcm[i, j] += 1
        glcm[j, i] += 1

    total = glcm.sum()
    if total == 0:
        return {k: float("nan") for k in
                ["glcm_contrast", "glcm_homogeneity", "glcm_energy",
                 "glcm_correlation", "glcm_asm"]}

    glcm /= total
    I, J = np.meshgrid(np.arange(n_levels), np.arange(n_levels), indexing="ij")
    contrast    = float(np.sum(glcm * (I - J) ** 2))
    homogeneity = float(np.sum(glcm / (1.0 + np.abs(I - J))))
    asm         = float(np.sum(glcm ** 2))
    energy      = float(math.sqrt(asm))
    mu_i  = float(np.sum(I * glcm))
    mu_j  = float(np.sum(J * glcm))
    sig_i = float(math.sqrt(max(np.sum(glcm * (I - mu_i) ** 2), 1e-10)))
    sig_j = float(math.sqrt(max(np.sum(glcm * (J - mu_j) ** 2), 1e-10)))
    correlation = float(np.sum(glcm * (I - mu_i) * (J - mu_j)) / (sig_i * sig_j))

    return {
        "glcm_contrast":    contrast,
        "glcm_homogeneity": homogeneity,
        "glcm_energy":      energy,
        "glcm_correlation": correlation,
        "glcm_asm":         asm,
    }


def _glcm_features_skimage(patch: np.ndarray) -> Dict[str, float]:
    n_levels = 32
    vmin, vmax = patch.min(), patch.max()
    if vmax == vmin:
        return {
            "glcm_contrast":    0.0,
            "glcm_homogeneity": 1.0,
            "glcm_energy":      1.0,
            "glcm_correlation": float("nan"),
            "glcm_asm":         1.0,
        }
    quantized = ((patch - vmin) / (vmax - vmin) * (n_levels - 1)).astype(np.uint8)
    try:
        glcm = greycomatrix(
            quantized,
            distances=[1],
            angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
            levels=n_levels,
            symmetric=True,
            normed=True,
        )
        return {
            "glcm_contrast":    float(greycoprops(glcm, "contrast").mean()),
            "glcm_homogeneity": float(greycoprops(glcm, "homogeneity").mean()),
            "glcm_energy":      float(greycoprops(glcm, "energy").mean()),
            "glcm_correlation": float(greycoprops(glcm, "correlation").mean()),
            "glcm_asm":         float(greycoprops(glcm, "ASM").mean()),
        }
    except Exception:
        return _glcm_features_manual(patch)


def glcm_from_mask(
    t2w_arr: np.ndarray,
    binary_zyx: np.ndarray,
) -> Dict[str, float]:
    nan_result = {k: float("nan") for k in
                  ["glcm_contrast", "glcm_homogeneity", "glcm_energy",
                   "glcm_correlation", "glcm_asm"]}

    slice_counts = binary_zyx.sum(axis=(1, 2))
    if slice_counts.max() == 0:
        return nan_result

    best_z     = int(np.argmax(slice_counts))
    mask_slice = binary_zyx[best_z]
    t2w_slice  = t2w_arr[best_z]

    rows = np.any(mask_slice, axis=1)
    cols = np.any(mask_slice, axis=0)
    if not rows.any() or not cols.any():
        return nan_result

    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    patch      = t2w_slice[r0:r1+1, c0:c1+1].copy().astype(np.float32)
    mask_patch = mask_slice[r0:r1+1, c0:c1+1]
    patch[~mask_patch] = 0.0

    if patch.size < 4:
        return nan_result

    return _glcm_features_skimage(patch) if _HAS_GLCM else _glcm_features_manual(patch)


def gradient_features(
    t2w_arr: np.ndarray,
    binary_zyx: np.ndarray,
) -> Dict[str, float]:
    if np.count_nonzero(binary_zyx) == 0:
        return {"gradient_mean": float("nan"), "gradient_std": float("nan")}
    arr = t2w_arr.astype(np.float32)
    grad_mag = np.sqrt(
        np.gradient(arr, axis=0) ** 2 +
        np.gradient(arr, axis=1) ** 2 +
        np.gradient(arr, axis=2) ** 2
    )
    vals = grad_mag[binary_zyx > 0]
    return {
        "gradient_mean": float(vals.mean()),
        "gradient_std":  float(vals.std()),
    }


def t2w_intensity_features(
    binary_zyx: np.ndarray,
    t2w_arr: np.ndarray,
    background_arr: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    nan_keys = [
        "t2w_mean", "t2w_std", "t2w_median",
        "t2w_p10", "t2w_p90", "t2w_range",
        "t2w_skewness", "t2w_kurtosis",
        "t2w_to_background_ratio",
        "glcm_contrast", "glcm_homogeneity", "glcm_energy",
        "glcm_correlation", "glcm_asm",
        "gradient_mean", "gradient_std",
    ]

    vals = t2w_arr[binary_zyx > 0].astype(np.float64)
    if vals.size == 0:
        return {k: float("nan") for k in nan_keys}

    out: Dict[str, float] = {
        "t2w_mean":   float(vals.mean()),
        "t2w_std":    float(vals.std()),
        "t2w_median": float(np.median(vals)),
        "t2w_p10":    float(np.percentile(vals, 10)),
        "t2w_p90":    float(np.percentile(vals, 90)),
        "t2w_range":  float(vals.max() - vals.min()),
    }

    if _HAS_SCIPY:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out["t2w_skewness"] = float(scipy_skew(vals))
            out["t2w_kurtosis"] = float(scipy_kurtosis(vals))
    else:
        mu, std = vals.mean(), vals.std()
        if std > 0:
            out["t2w_skewness"] = float(np.mean(((vals - mu) / std) ** 3))
            out["t2w_kurtosis"] = float(np.mean(((vals - mu) / std) ** 4) - 3.0)
        else:
            out["t2w_skewness"] = float("nan")
            out["t2w_kurtosis"] = float("nan")

    if background_arr is not None:
        bg_vals = background_arr[binary_zyx == 0].astype(np.float64)
        bg_vals = bg_vals[bg_vals > 0]
        bg_mean = float(bg_vals.mean()) if bg_vals.size > 0 else float("nan")
        out["t2w_to_background_ratio"] = (
            float(out["t2w_mean"] / bg_mean)
            if not np.isnan(bg_mean) and bg_mean > 0
            else float("nan")
        )
    else:
        out["t2w_to_background_ratio"] = float("nan")

    out.update(glcm_from_mask(t2w_arr, binary_zyx))
    out.update(gradient_features(t2w_arr, binary_zyx))

    return out


# =============================================================================
# L/R splitting
# =============================================================================

def split_lr_from_binary(
    sv_bin_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
) -> Tuple[np.ndarray, np.ndarray, str]:
    cc_img = sitk.ConnectedComponent(
        sitk.GetImageFromArray(sv_bin_zyx.astype(np.uint8))
    )
    cc_arr = sitk.GetArrayFromImage(cc_img)
    labels = np.unique(cc_arr)
    labels = labels[labels != 0]
    note   = ""

    if labels.size >= 2:
        sizes = sorted(
            [(lab, int((cc_arr == lab).sum())) for lab in labels],
            key=lambda x: x[1], reverse=True,
        )
        lab1, lab2 = sizes[0][0], sizes[1][0]
        m1 = (cc_arr == lab1).astype(bool)
        m2 = (cc_arr == lab2).astype(bool)
        note = "LR_from_connected_components"
    else:
        if not _HAS_SKLEARN:
            raise RuntimeError("Need scikit-learn for KMeans L/R split: pip install scikit-learn")
        pts = np.argwhere(sv_bin_zyx > 0)
        if pts.shape[0] < 20:
            empty = np.zeros_like(sv_bin_zyx, dtype=bool)
            return sv_bin_zyx.astype(bool), empty, "too_few_voxels_left_equals_all"
        x_idx = pts[:, 2:3].astype(np.float32)
        km    = KMeans(n_clusters=2, n_init=10, random_state=0).fit(x_idx)
        lbl   = km.labels_
        m1 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m2 = np.zeros_like(sv_bin_zyx, dtype=bool)
        m1[pts[lbl == 0, 0], pts[lbl == 0, 1], pts[lbl == 0, 2]] = True
        m2[pts[lbl == 1, 0], pts[lbl == 1, 1], pts[lbl == 1, 2]] = True
        note = "LR_from_KMeans_single_component"

    c1 = centroid_mm(m1, spacing_xyz)
    c2 = centroid_mm(m2, spacing_xyz)

    if not (np.isnan(c1[0]) or np.isnan(c2[0])):
        left, right = (m1, m2) if c1[0] <= c2[0] else (m2, m1)
        cl    = centroid_mm(left, spacing_xyz)
        cr    = centroid_mm(right, spacing_xyz)
        mid_x = ((sv_bin_zyx.shape[2] - 1) / 2.0) * spacing_xyz[0]
        if (cl[0] < mid_x) == (cr[0] < mid_x):
            note += ";BOTH_CENTROIDS_SAME_SIDE_CHECK_ORIENTATION"
    else:
        left, right = m1, m2

    return left.astype(bool), right.astype(bool), note


# =============================================================================
# Per-region metrics bundle
# =============================================================================

def part_metrics(
    binary_zyx: np.ndarray,
    spacing_xyz: Tuple[float, float, float],
    vx_mm3: float,
    t2w_arr: Optional[np.ndarray] = None,
    full_t2w_arr: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    nvox    = int(np.count_nonzero(binary_zyx))
    vol_mm3 = nvox * vx_mm3
    vol_ml  = vol_mm3 / 1000.0
    sa      = surface_area_mm2(binary_zyx, spacing_xyz)
    sph     = sphericity(vol_mm3, sa)
    pca     = pca_axes_metrics(binary_zyx, spacing_xyz)
    cen     = centroid_mm(binary_zyx, spacing_xyz)
    bb      = bounding_box_mm(binary_zyx, spacing_xyz)

    result: Dict[str, float] = {
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

    if t2w_arr is not None:
        tex = t2w_intensity_features(binary_zyx, t2w_arr, background_arr=full_t2w_arr)
        result.update(tex)

    return result


# =============================================================================
# Main computation per case
# =============================================================================

def compute_one(
    sv_mask_path: str,
    sv_label: int,
    derive_lr: bool,
    t2w_path: Optional[str] = None,
    prostate_mask_path: Optional[str] = None,
) -> Dict:

    sv_img  = read_image(sv_mask_path)
    sv_arr  = sitk.GetArrayFromImage(sv_img).astype(np.int32)
    spacing = sv_img.GetSpacing()
    vx_mm3  = voxel_volume_mm3(sv_img)
    sv_bin  = (sv_arr == sv_label)

    out: Dict = {"notes": ""}

    # load and resample T2W
    t2w_arr_rs: Optional[np.ndarray] = None
    if t2w_path and os.path.exists(t2w_path):
        t2w_img    = read_image(t2w_path)
        t2w_img_rs = resample_to_ref(t2w_img, sv_img, interp=sitk.sitkLinear)
        t2w_arr_rs = sitk.GetArrayFromImage(t2w_img_rs).astype(np.float32)
    elif t2w_path:
        _note = f"T2W_not_found:{t2w_path}"
        out["notes"] = _note

    _geom_nan_keys = [
        "voxel_count", "volume_ml", "surface_area_mm2", "sphericity",
        "elongation", "flatness", "major_axis_mm", "minor_axis_mm",
        "axis_ratio", "centroid_x_mm", "centroid_y_mm", "centroid_z_mm",
        "bbox_width_mm", "bbox_height_mm", "bbox_depth_mm",
    ]
    _t2w_nan_keys = [
        "t2w_mean", "t2w_std", "t2w_median", "t2w_p10", "t2w_p90",
        "t2w_range", "t2w_skewness", "t2w_kurtosis",
        "t2w_to_background_ratio",
        "glcm_contrast", "glcm_homogeneity", "glcm_energy",
        "glcm_correlation", "glcm_asm",
        "gradient_mean", "gradient_std",
    ]
    _all_nan_keys = _geom_nan_keys + (_t2w_nan_keys if t2w_arr_rs is not None else [])

    if derive_lr:
        left, right, note = split_lr_from_binary(sv_bin, spacing)
        out["notes"] = (out["notes"] + "; " + note) if out["notes"] else note

        L = part_metrics(left,   spacing, vx_mm3, t2w_arr_rs, t2w_arr_rs)
        R = part_metrics(right,  spacing, vx_mm3, t2w_arr_rs, t2w_arr_rs)
        T = part_metrics(sv_bin, spacing, vx_mm3, t2w_arr_rs, t2w_arr_rs)

        for k, v in L.items():
            out[f"sv_left_{k}"] = v
        for k, v in R.items():
            out[f"sv_right_{k}"] = v
        for k, v in T.items():
            out[f"sv_total_{k}"] = v

        out["sv_asymmetry_index_volume"]     = safe_asymmetry(L["volume_ml"],        R["volume_ml"])
        out["sv_asymmetry_index_surface"]    = safe_asymmetry(L["surface_area_mm2"], R["surface_area_mm2"])
        out["sv_asymmetry_index_major_axis"] = safe_asymmetry(L["major_axis_mm"],    R["major_axis_mm"])
        out["sv_asymmetry_index_t2w_mean"]   = (
            safe_asymmetry(L.get("t2w_mean", np.nan), R.get("t2w_mean", np.nan))
            if t2w_arr_rs is not None else float("nan")
        )

        lc = (L["centroid_x_mm"], L["centroid_y_mm"], L["centroid_z_mm"])
        rc = (R["centroid_x_mm"], R["centroid_y_mm"], R["centroid_z_mm"])
        out["sv_centroid_distance_lr_mm"]   = euclidean(lc, rc)
        out["sv_lr_split_confidence_x_mm"]  = (
            float(abs(rc[0] - lc[0]))
            if not (np.isnan(lc[0]) or np.isnan(rc[0]))
            else float("nan")
        )

    else:
        T = part_metrics(sv_bin, spacing, vx_mm3, t2w_arr_rs, t2w_arr_rs)
        for k, v in T.items():
            out[f"sv_total_{k}"] = v
        for side in ["sv_left", "sv_right"]:
            for k in _all_nan_keys:
                out[f"{side}_{k}"] = np.nan
        out["sv_asymmetry_index_volume"]     = np.nan
        out["sv_asymmetry_index_surface"]    = np.nan
        out["sv_asymmetry_index_major_axis"] = np.nan
        out["sv_asymmetry_index_t2w_mean"]   = np.nan
        out["sv_centroid_distance_lr_mm"]    = np.nan
        out["sv_lr_split_confidence_x_mm"]   = np.nan

    # prostate-relative features
    out["prostate_volume_ml"]                  = np.nan
    out["sv_to_prostate_volume_ratio"]         = np.nan
    out["sv_centroid_to_prostate_centroid_mm"] = np.nan

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
        p_vol = float(np.count_nonzero(p_bin) * vx_mm3 / 1000.0)
        out["prostate_volume_ml"] = p_vol

        sv_tot = out.get("sv_total_volume_ml", np.nan)
        if not np.isnan(sv_tot) and p_vol > 0:
            out["sv_to_prostate_volume_ratio"] = float(sv_tot / p_vol)

        sv_c = (
            out["sv_total_centroid_x_mm"],
            out["sv_total_centroid_y_mm"],
            out["sv_total_centroid_z_mm"],
        )
        out["sv_centroid_to_prostate_centroid_mm"] = euclidean(
            sv_c, centroid_mm(p_bin, spacing)
        )

    if not _HAS_SKIMAGE:
        w = "surface_area/sphericity/GLCM require scikit-image"
        out["notes"] = (out["notes"] + "; " + w) if out["notes"] else w
    if not _HAS_SCIPY:
        w = "skewness/kurtosis using manual fallback (install scipy)"
        out["notes"] = (out["notes"] + "; " + w) if out["notes"] else w

    return out


# =============================================================================
# CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="SV geometry + T2W texture — Chimere dataset."
    )
    ap.add_argument("--sv_masks_dir",       required=True)
    ap.add_argument("--out_csv",            required=True)
    ap.add_argument("--sv_label",           type=int, default=1)
    ap.add_argument("--derive_lr",          action="store_true")
    ap.add_argument("--t2w_dir",            default=None)
    ap.add_argument("--prostate_masks_dir", default=None)
    args = ap.parse_args()

    sv_paths = iter_nii_files(args.sv_masks_dir)
    if not sv_paths:
        raise SystemExit(f"No .nii/.nii.gz files found under: {args.sv_masks_dir}")

    print(f"Found {len(sv_paths)} SV mask file(s)")
    print(f"  scikit-image : {_HAS_SKIMAGE}")
    print(f"  scikit-learn : {_HAS_SKLEARN}")
    print(f"  scipy        : {_HAS_SCIPY}")
    print(f"  GLCM         : {_HAS_GLCM}")
    print(f"  T2W texture  : {'enabled' if args.t2w_dir else 'disabled'}")
    print(f"  Prostate     : {'enabled' if args.prostate_masks_dir else 'disabled'}")

    rows = []
    iterator = (
        tqdm(sv_paths, desc="Processing", unit="case")
        if _HAS_TQDM else sv_paths
    )

    for i, sv_mask_path in enumerate(iterator, start=1):
        sv_stem = strip_nii_ext(os.path.basename(sv_mask_path))
        case_id = extract_case_id(sv_stem)  # '1003_0001_t2w' -> '1003'

        msg = f"[{i}/{len(sv_paths)}] {case_id} (stem: {sv_stem})"
        (tqdm.write(msg) if _HAS_TQDM else print(msg))

        # T2W: same stem, different folder
        t2w_path = None
        if args.t2w_dir:
            t2w_path = find_matching_file(sv_stem, args.t2w_dir)
            if t2w_path is None:
                print(f"  WARNING: no T2W found for {sv_stem}")

        # prostate: same stem, different folder
        prostate_path = None
        if args.prostate_masks_dir:
            prostate_path = find_matching_file(sv_stem, args.prostate_masks_dir)
            if prostate_path is None:
                print(f"  WARNING: no prostate mask found for {sv_stem}")

        try:
            feats = compute_one(
                sv_mask_path=sv_mask_path,
                sv_label=args.sv_label,
                derive_lr=args.derive_lr,
                t2w_path=t2w_path,
                prostate_mask_path=prostate_path,
            )
        except Exception as e:
            print(f"  ERROR on {case_id}: {e}")
            feats = {"notes": f"ERROR: {e}"}

        row = {
            "case_id":      case_id,
            "sv_stem":      sv_stem,
            "sv_mask_path": sv_mask_path,
            "sv_label":     args.sv_label,
            "derive_lr":    int(args.derive_lr),
            "t2w_path":     t2w_path or "",
        }
        row.update(feats)
        rows.append(row)

    if not rows:
        raise SystemExit("No rows to write.")

    base_cols  = ["case_id", "sv_stem", "sv_mask_path", "t2w_path", "sv_label", "derive_lr"]
    other_cols = sorted(c for c in rows[0] if c not in base_cols)
    cols       = base_cols + other_cols

    os.makedirs(os.path.dirname(os.path.abspath(args.out_csv)) or ".", exist_ok=True)
    with open(args.out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    print(f"\nWrote {len(rows)} row(s) to: {args.out_csv}")

if __name__ == "__main__":
    main()
