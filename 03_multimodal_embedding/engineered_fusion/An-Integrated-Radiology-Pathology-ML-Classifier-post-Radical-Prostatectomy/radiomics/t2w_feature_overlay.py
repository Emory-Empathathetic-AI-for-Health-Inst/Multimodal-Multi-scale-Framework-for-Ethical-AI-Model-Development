"""
T2W + TZ feature-overlay figures for representative BCR cases.
Outputs TWO figures next to your images:
  * fig_t2w_TP_TN.png  -> True Positive (175) + True Negative (357)   [black value boxes]
  * fig_t2w_FP_FN.png  -> False Positive (246) + False Negative (292) [terminal/green value boxes]

Robust image/segmentation loading:
  - nibabel as_closest_canonical() so T2W and mask share a consistent (RAS) orientation,
  - if the mask grid differs from the T2W (shape or affine), the mask is RESAMPLED onto the
    T2W grid with nearest-neighbour (label-preserving),
  - 4D / singleton dims squeezed,
  - axial slice taken along the through-plane (superior-inferior) axis,
  - only the transition-zone label (TZ_LABEL) kept; PZ ignored.

RUN LOCALLY where the .nii files live:
    pip install nibabel numpy matplotlib scipy
    python overlay_t2w_full.py
"""
import os
import numpy as np
import nibabel as nib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy.ndimage import uniform_filter
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False
try:
    from nibabel.processing import resample_from_to     # needs scipy
    HAVE_RESAMPLE = True
except Exception:
    HAVE_RESAMPLE = False

# ------------------------- PATHS (Linux) -------------------------
BASE     = "/home/kozyoru/emory_ts/personal_space/KOZYORU/Prostate_Age_02172026/GIFU"
T2W_DIR  = os.path.join(BASE, "t2w", "csPCA")     # .../GIFU/t2w/csPCA/<id>.nii
MASK_DIR = os.path.join(BASE, "tzpz", "csPCA")    # .../GIFU/tzpz/csPCA  (combined TZ+PZ)
TZ_LABEL = 1            # transition-zone voxel value in the tzpz mask. PZ ignored.
                       # Script prints the labels found -- if TZ is actually 2, change this.
MODE         = "texture"   # "texture" (heatmap inside TZ) or "mask" (contour only)
ZOOM_PAD     = 0.6         # crop each panel to the TZ ROI; padding = fraction of ROI size
RADIOLOGICAL = True        # True = patient-left on viewer's right (radiology convention)

META = {   # pid -> (true_label, fused_risk, role)
    175: (1, 0.77, "TP · BCR+ correctly flagged"),
    357: (0, 0.19, "TN · BCR- correctly cleared"),
    246: (0, 0.72, "FP · BCR- over-called"),
    292: (1, 0.21, "FN · BCR+ missed"),
}
GROUPS = [   # (case pair, output filename, value-box style)
    ([175, 357], "fig_t2w_TP_TN.png", "black"),     # correct cases
    ([246, 292], "fig_t2w_FP_FN.png", "terminal"),  # error cases
]
STYLES = {
    "black":    dict(fc="#111111", tc="#f5f5f5", ec="#555555"),   # black background effect
    "terminal": dict(fc="#000000", tc="#39FF14", ec="#39FF14"),   # green-on-black console look
}
CASE_Z = {
    175: [("TZ wav-HHL glrlm LongRunLowGra", +4.4), ("TZ wav-LHL glszm SmallAreaEmph", -3.1),
          ("TZ wav-LLH gldm DependenceNonU", +2.9), ("TZ wav-LHL glszm SizeZoneNonUn", -2.5),
          ("TZ wav-HLL glszm SizeZoneNonUn", -2.4)],
    357: [("cT stage", -3.4), ("TZ wav-LHL glszm SizeZoneNonUn", +3.1),
          ("TZ wav-HLL glszm SizeZoneNonUn", +3.1), ("TZ wav-LHL glszm SmallAreaEmph", +2.8),
          ("TZ wav-HLL glcm Correlation", -1.9)],
    246: [("PNI (perineural inv.)", +1.2), ("TZ wav-LLH gldm DependenceNonU", +1.2),
          ("TZ wav-HLL glcm Correlation", +1.2), ("PSA", -0.7),
          ("TZ wav-LHL glszm SizeZoneNonUn", -0.6)],
    292: [("Biopsy grade group", +1.0), ("TZ wav-LLH gldm DependenceNonU", -0.9),
          ("PNI (perineural inv.)", -0.8), ("TZ wav-HLL glcm Correlation", -0.4),
          ("% positive cores", -0.4)],
}
# --------------------------------------------------------------------------

def _resolve(folder, pid):
    for ext in (".nii.gz", ".nii"):
        p = os.path.join(folder, f"{pid}{ext}")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"no .nii/.nii.gz for {pid} in {folder}")

def _canon(path):
    return nib.as_closest_canonical(nib.load(path))

def load_pair(pid):
    """Return (t2_array, mask_array, labels) on a SHARED grid, canonical orientation."""
    t2i = _canon(_resolve(T2W_DIR, pid))
    mki = _canon(_resolve(MASK_DIR, pid))
    same = (mki.shape[:3] == t2i.shape[:3]) and np.allclose(mki.affine, t2i.affine, atol=1e-3)
    if not same:
        if not HAVE_RESAMPLE:
            raise RuntimeError("mask/image grids differ and scipy is missing for resampling")
        mki = resample_from_to(mki, (t2i.shape[:3], t2i.affine), order=0)  # nearest-neighbour
    t2 = np.squeeze(np.asarray(t2i.dataobj, dtype=np.float32))
    mk = np.squeeze(np.asarray(mki.dataobj, dtype=np.float32))
    if t2.ndim == 4: t2 = t2[..., 0]
    if mk.ndim == 4: mk = mk[..., 0]
    labs = sorted(int(v) for v in np.unique(np.rint(mk)) if v != 0)
    return t2, mk, labs

def best_slice(mask3d):
    return int(np.argmax(mask3d.sum(axis=(0, 1))))        # through-plane = axis 2 (S-I)

def window(img, lo=1, hi=99):
    a, b = np.percentile(img, [lo, hi])
    return np.clip((img - a) / (b - a + 1e-6), 0, 1)

def local_heterogeneity(slice2d, mask2d, size=5):
    if not HAVE_SCIPY:
        return None
    m = uniform_filter(slice2d, size); sq = uniform_filter(slice2d**2, size)
    std = np.sqrt(np.maximum(sq - m**2, 0)) * mask2d
    if mask2d.sum() > 0:
        v = std[mask2d > 0]; std = (std - v.min()) / (np.ptp(v) + 1e-6) * mask2d
    return std

def draw_panel(ax, pid, style):
    label, risk, role = META[pid]
    try:
        t2, mkv, labs = load_pair(pid)
        mk = np.rint(mkv) == TZ_LABEL
        print(f"pt {pid}: t2{t2.shape} mask{mkv.shape} labels {labs} "
              f"-> TZ_LABEL={TZ_LABEL} ({int(mk.sum())} voxels)")
        if mk.sum() == 0:
            print(f"  !! no voxels == TZ_LABEL={TZ_LABEL}; check which label is TZ")
        z = best_slice(mk)
        sl = window(t2[:, :, z]); msl = mk[:, :, z].astype(float)
        ax.imshow(sl.T, cmap="gray", origin="lower")
        if MODE == "texture":
            het = local_heterogeneity(sl, msl)
            if het is not None:
                ax.imshow(np.where(msl.T > 0, het.T, np.nan), cmap="inferno", alpha=0.55, origin="lower")
        ax.contour(msl.T, levels=[0.5], colors="#39FF14", linewidths=1.6)
        xs = np.where(msl.sum(axis=1) > 0)[0]; ys = np.where(msl.sum(axis=0) > 0)[0]
        if len(xs) and len(ys):
            px = max(8, int(ZOOM_PAD * (xs.max() - xs.min() + 1)))
            py = max(8, int(ZOOM_PAD * (ys.max() - ys.min() + 1)))
            lo_x, hi_x = xs.min() - px, xs.max() + px
            ax.set_xlim((hi_x, lo_x) if RADIOLOGICAL else (lo_x, hi_x))
            ax.set_ylim(ys.min() - py, ys.max() + py)
    except Exception as e:
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.add_patch(plt.Rectangle((0, 0), 10, 10, color="#2b2b2b"))
        ax.text(5, 5, f"pt {pid}: could not load\n{e}", color="#bbb", ha="center", va="center", fontsize=8)

    correct = (label == 1 and risk >= 0.5) or (label == 0 and risk < 0.5)
    ax.set_title(f"pt {pid} · {role}", color="white", fontsize=12,
                 backgroundcolor="#1e8449" if correct else "#c0392b")
    lines = [f"fused P(BCR) = {risk:.2f}   (true BCR = {label})", ""]
    for feat, zsc in CASE_Z.get(pid, []):
        lines.append(f"{'▲' if zsc > 0 else '▼'} {feat:31s} z={zsc:+.1f}")
    st = STYLES[style]
    ax.text(0.0, -0.04, "\n".join(lines), transform=ax.transAxes, color=st["tc"],
            fontsize=9, family="monospace", va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.5", fc=st["fc"], ec=st["ec"], lw=1.2))
    ax.text(0.98, 0.97, "TZ ROI", transform=ax.transAxes, color="#39FF14",
            fontsize=9, ha="right", va="top")
    ax.set_xticks([]); ax.set_yticks([])

def render(group, out, style):
    fig, axes = plt.subplots(1, 2, figsize=(13, 8.8), gridspec_kw={"wspace": 0.06})
    for ax, pid in zip(axes, group):
        draw_panel(ax, pid, style)
    if MODE == "texture":
        sm = plt.cm.ScalarMappable(cmap="inferno"); sm.set_array([])
        cb = fig.colorbar(sm, ax=axes, shrink=0.6, pad=0.02)
        cb.set_label("local T2W heterogeneity inside TZ (texture proxy: low to high)")
    tag = "correct cases" if style == "black" else "error cases"
    fig.suptitle(f"T2W + TZ feature overlay -- {tag}\n"
                 "green contour = TZ ROI | green header = correct, red = error",
                 fontsize=13, y=1.0)
    path = os.path.join(BASE, out)
    plt.savefig(path, dpi=160, bbox_inches="tight"); plt.close()
    print("saved", path)

def main():
    for group, out, style in GROUPS:
        render(group, out, style)

if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# Exact per-voxel PyRadiomics feature map (true "feature overlay"), TZ only:
#   from radiomics import featureextractor; import SimpleITK as sitk
#   ex = featureextractor.RadiomicsFeatureExtractor(); ex.enableImageTypeByName('Wavelet')
#   res = ex.execute(_resolve(T2W_DIR,pid), _resolve(MASK_DIR,pid), label=TZ_LABEL, voxelBased=True)
#   fmap = sitk.GetArrayFromImage(res['wavelet-HLL_glcm_Correlation'])   # [z,y,x]
# ---------------------------------------------------------------------------
