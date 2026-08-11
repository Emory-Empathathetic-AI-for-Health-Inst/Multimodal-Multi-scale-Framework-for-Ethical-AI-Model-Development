# WSI Segmentation using UNI2

Computational pathology pipeline for prostate cancer feature extraction and cancer segmentation on whole-slide images (WSIs) using the UNI2-h foundation model.

The pipeline:

1. Users provide the directory where their WSIs already exist; slides are not copied or linked into the project.
2. Patches from every WSI are saved directly into one user-selected directory; a separate flattening step is not needed.

## Pipeline

```text
WSI directory
    -> flat patch directory
    -> stain normalization
    -> UNI2-h embeddings
    -> patch predictions
    -> WSI heatmaps
```

## 1. Installation

If you already have the main repository, enter the segmentation directory:

```bash
cd 02_feature_extraction/segmentation
```

Otherwise, clone the main repository and then enter the segmentation directory:

```bash
git clone https://github.com/Emory-Empathathetic-AI-for-Health-Inst/Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development.git
cd Multimodal-Multi-scale-Framework-for-Ethical-AI-Model-Development/02_feature_extraction/segmentation
```

On Linux, macOS, WSL, or Git Bash, run:

```bash
bash setup.sh
```

The setup script installs the Python requirements and places both external repositories inside this project:

```text
segmentation/
├── WSITools/
└── UNI/
```

On a platform without Bash, run the equivalent commands:

```text
python -m pip install -r requirements.txt
git clone https://github.com/smujiang/WSITools.git WSITools
python -m pip install -e WSITools
git clone https://github.com/mahmoodlab/UNI.git UNI
python -m pip install -e UNI
```

Request access to the gated [MahmoodLab/UNI2-h](https://huggingface.co/MahmoodLab/UNI2-h) model before feature extraction.

## 2. Choose your data locations

The project does not require a particular data layout. You only need:

- `WSI_DIR`: the existing directory containing `.svs`, `.ndpi`, `.tif`, or `.tiff` slides.
- `PATCH_DIR`: one directory where all extracted and normalized patches will be stored.
- `OUTPUT_DIR`: a directory for embeddings, predictions, and heatmaps.

Example:

```text
/path/to/raw_wsis/
/path/to/processed/patches/
/path/to/processed/results/
```

The output directories are created automatically when needed. WSI files remain in their original location.

## 3. Extract tissue patches

```bash
python src/preprocessing/extract_patches.py \
  --wsi-dir "/path/to/raw_wsis" \
  --output-dir "/path/to/processed/patches"
```

This extracts non-overlapping 224 × 224 tissue patches from every supported WSI in `--wsi-dir`. All PNG patches are written directly into the same `--output-dir`.

Patch filenames include the slide stem and coordinates, preventing patches from different slides from being mixed up. WSI filename stems must therefore be unique.

For a small test before extracting everything:

```bash
python src/preprocessing/extract_patches.py \
  --wsi-dir "/path/to/raw_wsis" \
  --output-dir "/path/to/processed/patches" \
```

Important extraction options:

- `--sample-count -1`: extract every qualifying patch; this is the default.
- `--processes`: number of parallel WSI workers; default is 4.
- `--patch-size`: patch width and height; default is 224.
- `--stride`: distance between patch locations; default is 224.
- `--tissue-threshold`: LAB tissue-detection threshold; default is 85.
- `--min-tissue-area`: minimum tissue fraction per patch; default is 0.5.

## 4. Normalize stains

Normalization is performed in place in the same flat patch directory:

```bash
python src/preprocessing/normalize_stains.py \
  --data-dir "/path/to/processed/patches" \
  --reference-patch "data/ref_patch/reference-patch.png"
```

## 5. Extract UNI2-h features

Provide a Hugging Face token either with `--token` or through the `HF_TOKEN` environment variable:

```bash
python src/inference/extract_features.py \
  --token "YOUR_HF_TOKEN" \
  --data_dir "/path/to/processed/patches" \
  --output_path "/path/to/processed/results/patch_embeddings.h5"
```

The default inference batch size is 64. Reduce it if GPU memory is insufficient:

```bash
python src/inference/extract_features.py \
  --token "YOUR_HF_TOKEN" \
  --batch_size 64 \
  --data_dir "/path/to/processed/patches" \
  --output_path "/path/to/processed/results/patch_embeddings.h5"
```

## 6. Classify patches

```bash
python src/inference/classify_h5.py \
  --h5 "/path/to/processed/results/patch_embeddings.h5" \
  --model "models/prostate_uni2_model.joblib" \
  --output "/path/to/processed/results/patch_predictions.csv"
```

## 7. Reconstruct WSI heatmaps and segmentation masks

```bash
python src/postprocessing/full_wsi_heatmap.py \
  --csv "/path/to/processed/results/patch_predictions.csv" \
  --out "/path/to/processed/results/WSI_Heatmaps"
```

For each slide, this produces:

- `<slide_id>_full_heatmap.png`: the probability heatmap.
- `<slide_id>_segmentation_mask.png`: a patch-grid-resolution binary mask created by thresholding `probability_class0` at 0.5 and then applying one morphological closing operation with a 10 × 10 elliptical kernel.

The threshold and kernel size are fixed internally; they are not command-line arguments. The mask is saved as an 8-bit grayscale PNG with background `0` and foreground `255`. No erosion, dilation, opening, or other morphology is applied separately.

## Project structure

```text
.
├── data/
│   └── ref_patch/
│       └── reference-patch.png
├── models/
│   └── prostate_uni2_model.joblib
├── src/
│   ├── preprocessing/
│   │   ├── extract_patches.py
│   │   └── normalize_stains.py
│   ├── inference/
│   │   ├── extract_features.py
│   │   ├── classify_h5.py
│   │   └── predict.py
│   └── postprocessing/
│       └── full_wsi_heatmap.py
├── requirements.txt
├── setup.sh
└── README.md
```

`WSITools/` and `UNI/` appear inside the project after installation. Raw WSIs and processed outputs can remain anywhere selected by the user.
