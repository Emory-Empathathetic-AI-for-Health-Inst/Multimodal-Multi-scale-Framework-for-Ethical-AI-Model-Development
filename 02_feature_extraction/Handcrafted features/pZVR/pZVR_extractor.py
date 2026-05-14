# -*- coding: utf-8 -*-
"""
Created on Thu May 11 16:43:07 2023
@author: zzha962
"""
import argparse
from pathlib import Path

import SimpleITK as sitk
import numpy as np
import pandas as pd
from tqdm import tqdm


def calculate_pzvr_from_mask(mask_path, tz_label=1, pz_label=2):
    """
    Calculate pZVR from TZ/PZ segmentation mask.

    pZVR = PZ_volume / (TZ_volume + PZ_volume)
    TZ/PZ = TZ_volume / PZ_volume
    """
    img = sitk.ReadImage(str(mask_path))
    arr = sitk.GetArrayFromImage(img)

    tz_volume = int(np.sum(arr == tz_label))
    pz_volume = int(np.sum(arr == pz_label))
    prostate_volume = tz_volume + pz_volume

    if prostate_volume == 0:
        pzvr = np.nan
    else:
        pzvr = pz_volume / prostate_volume

    if pz_volume == 0:
        tz_pz_ratio = np.nan
    else:
        tz_pz_ratio = tz_volume / pz_volume

    return {
        "CaseName": mask_path.stem,
        "TZ_volume": tz_volume,
        "PZ_volume": pz_volume,
        "Prostate_volume": prostate_volume,
        "pZVR": pzvr,
        "TZ_PZ_ratio": tz_pz_ratio,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate pZVR from TZ/PZ segmentation masks.")
    parser.add_argument("--mask_dir",type=str,required=True,help="Folder containing TZ/PZ segmentation masks.")
    parser.add_argument("--output_csv",type=str,default="pzvr_results.csv",help="Output CSV file path.")
    parser.add_argument("--tz_label",type=int,default=1,help="Label value for TZ/CZ. Default: 1")
    parser.add_argument("--pz_label",type=int,default=2,help="Label value for PZ. Default: 2")
    parser.add_argument("--ext",type=str,default=".nii",help="Mask file extension, e.g. .nii, .nii.gz, .mha. Default: .nii")

    args = parser.parse_args()

    mask_dir = Path(args.mask_dir)
    mask_files = sorted(mask_dir.glob(f"*{args.ext}"))

    if len(mask_files) == 0:
        raise FileNotFoundError(f"No mask files found in {mask_dir} with extension {args.ext}")

    results = []

    for mask_path in tqdm(mask_files, desc="Calculating pZVR"):
        result = calculate_pzvr_from_mask(
            mask_path,
            tz_label=args.tz_label,
            pz_label=args.pz_label
        )
        results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(args.output_csv, index=False)

    print(f"Done. Results saved to: {args.output_csv}")


if __name__ == "__main__":
    main()