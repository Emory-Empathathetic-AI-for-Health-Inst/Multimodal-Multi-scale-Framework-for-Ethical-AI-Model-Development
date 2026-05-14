# pZVR Feature Extraction

This module provides extraction of the prostate zonal volumetric ratio (pZVR) from TZ/PZ segmentation masks.

The pZVR biomarker was originally developed and proposed by the laboratory of Dr. Anant Madabhushi at Emory University as part of prior published work on prostate MRI biomarkers.

## Definition

The feature is defined as:

pZVR = PZ volume / (TZ volume + PZ volume)

where:
- TZ = transition zone
- PZ = peripheral zone

Additional related measurements such as TZ/PZ ratio are also supported.

## Input

The script expects prostate zonal segmentation masks with:
- Label 1: TZ (or CZ/TZ depending on dataset convention)
- Label 2: PZ

Supported formats include:
- `.nii`
- `.nii.gz`
- `.mha`

## Citation

If you use this feature extraction module or derived biomarkers in your work, please cite:

Zhang Z, et al.
"A deep learning derived prostate zonal biomarker from T2-weighted MRI to distinguish between prostate cancer and benign prostatic hyperplasia."
Medical Physics. 2025.

PubMed:
https://pubmed.ncbi.nlm.nih.gov/40804780/

## Attribution

This biomarker and associated methodology originated from research conducted in the laboratory of Dr. Anant Madabhushi at Emory University.

This repository includes an implementation intended for research and collaborative academic use.

## Notes

Please ensure segmentation label conventions are consistent before running feature extraction.