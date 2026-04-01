import os
import nibabel as nib
import numpy as np
from glob import glob
from tqdm import tqdm

def binarize_labels(label_dir, threshold=0.5):
    """
    Binarize all .nii.gz label files in a directory.
    Set values > threshold to 1, else 0.
    """
    if not os.path.exists(label_dir):
        print(f" Label directory not found: {label_dir}")
        return

    label_files = sorted(glob(os.path.join(label_dir, "*.nii.gz")))
    print(f"\n Found {len(label_files)} label files in: {label_dir}")

    for file_path in tqdm(label_files, desc=f"Binarizing {os.path.basename(label_dir)}"):
        try:
            img = nib.load(file_path)
            data = img.get_fdata()
            original_vals = np.unique(data)

            # Binarization
            binary = (data > threshold).astype(np.uint8)

            nib.save(nib.Nifti1Image(binary, img.affine, img.header), file_path)

            print(f"   {os.path.basename(file_path)} | {original_vals} → {np.unique(binary)}")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")



if __name__ == "__main__":
    base_dir = "/content/drive/MyDrive/combined_cpre/latest/nnUNet_raw/Dataset001_Prostate"

    labelsTr = os.path.join(base_dir, "labelsTr")
    labelsTs = os.path.join(base_dir, "labelsTs")

    print("Starting label binarization...")

    binarize_labels(labelsTr)
    binarize_labels(labelsTs)

    print("\ Done! ALL labelsTr + labelsTs are now clean binary masks.")
