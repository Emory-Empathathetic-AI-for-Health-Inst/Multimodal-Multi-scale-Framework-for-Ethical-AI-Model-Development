import nibabel as nib
import numpy as np
import os
from tqdm import tqdm
import json

# PATHS

base_dir = ""
raw = f"{base_dir}/nnUNet_raw/Dataset001_Prostate"

train_dir = "/content/drive/MyDrive/Rebuttal_data/Combined_all_cpre"

os.makedirs(f"{raw}/imagesTr", exist_ok=True)
os.makedirs(f"{raw}/labelsTr", exist_ok=True)


# GLAND-BASED HARD BOX (INPUT ONLY)
def generate_adaptive_hard_box_mask(gland, spacing, margin_mm=(3, 3, 3)):
    if np.sum(gland) == 0:
        raise ValueError("Empty gland mask")

    nonzero = np.argwhere(gland > 0)
    min_coords = nonzero.min(axis=0)
    max_coords = nonzero.max(axis=0)

    spacing = np.array(spacing[:3])
    margin_vox = np.round(np.array(margin_mm) / spacing).astype(int)

    min_corner = np.maximum(min_coords - margin_vox, 0)
    max_corner = np.minimum(max_coords + margin_vox, gland.shape)

    box = np.zeros_like(gland, dtype=np.float32)
    box[
        min_corner[0]:max_corner[0],
        min_corner[1]:max_corner[1],
        min_corner[2]:max_corner[2],
    ] = 1.0

    return box

# CONVERT TRAIN ONLY in nnunet format

def convert_train(split_dir, img_out, lbl_out, start_idx=0):
    case_map = {}
    idx = start_idx

    cases = sorted(os.listdir(split_dir))

    for case in tqdm(cases, desc="Processing TRAIN"):
        case_path = os.path.join(split_dir, case)

        t2_path     = os.path.join(case_path, f"{case}_t2w.nii.gz")
        adc_path    = os.path.join(case_path, f"{case}_adc_reg.nii.gz")
        gland_path  = os.path.join(case_path, f"{case}_gland.nii.gz")
        tumor_path  = os.path.join(case_path, f"{case}_tumor.nii.gz")

        if not all(os.path.exists(p) for p in [t2_path, adc_path, gland_path, tumor_path]):
            continue

        t2 = nib.load(t2_path)
        adc = nib.load(adc_path)

        gland = nib.load(gland_path).get_fdata()
        tumor = nib.load(tumor_path).get_fdata()

        if np.sum(gland) == 0:
            continue

        box = generate_adaptive_hard_box_mask(
            gland,
            t2.header.get_zooms()
        )

        label = (tumor > 0).astype(np.uint8)

        nib.save(t2,  f"{img_out}/case_{idx:04d}_0000.nii.gz")
        nib.save(adc, f"{img_out}/case_{idx:04d}_0001.nii.gz")
        nib.save(
            nib.Nifti1Image(box.astype(np.float32), affine=t2.affine),
            f"{img_out}/case_{idx:04d}_0002.nii.gz"
        )
        nib.save(
            nib.Nifti1Image(label, affine=t2.affine),
            f"{lbl_out}/case_{idx:04d}.nii.gz"
        )

        case_map[f"case_{idx:04d}"] = case
        idx += 1

    return case_map


train_map = convert_train(
    train_dir,
    f"{raw}/imagesTr",
    f"{raw}/labelsTr",
    start_idx=0
)

with open(f"{raw}/train_mapping.json", "w") as f:
    json.dump(train_map, f, indent=4)

print("Done")
