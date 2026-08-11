import argparse
import os
import re

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm


def parse_coords(filename):
    """Return the slide ID and patch coordinates encoded in a patch filename."""
    base = os.path.basename(filename)
    match = re.search(r"(.+?)_(\d+)_(\d+)(?:_None)?\.png$", base)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    return None, None, None


def build_probability_grid(df_slide):
    """Build the patch-level probability grid for one slide."""
    unique_x = np.sort(df_slide["x"].unique())
    unique_y = np.sort(df_slide["y"].unique())
    x_map = {value: index for index, value in enumerate(unique_x)}
    y_map = {value: index for index, value in enumerate(unique_y)}
    grid = np.full((len(unique_y), len(unique_x)), np.nan, dtype=np.float32)
    for _, row in df_slide.iterrows():
        grid[y_map[row["y"]], x_map[row["x"]]] = row["probability_class0"]
    return grid


def save_heatmap(probability_grid, slide_id, output_dir):
    """Save the original probability heatmap."""
    plt.figure(figsize=(15, 10))
    current_cmap = plt.colormaps["RdYlGn_r"].copy()
    current_cmap.set_bad(color="white")
    image = plt.imshow(
        probability_grid, cmap=current_cmap, interpolation="nearest", vmin=0, vmax=1
    )
    colorbar = plt.colorbar(image, fraction=0.046, pad=0.04)
    colorbar.set_label(
        "Cancer Probability (Red = Cancer, Green = Normal)",
        rotation=270,
        labelpad=15,
    )
    plt.title(f"Full WSI Cancer Map: {slide_id}", fontsize=16)
    plt.axis("off")
    output_path = os.path.join(output_dir, f"{slide_id}_full_heatmap.png")
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()


def save_segmentation_mask(probability_grid, slide_id, output_dir):
    """Threshold probabilities and apply one morphological closing operation."""
    threshold = 0.5
    closing_kernel = 10
    binary_mask = np.where(
        np.isfinite(probability_grid) & (probability_grid >= threshold), 1, 0
    ).astype(np.uint8)
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (closing_kernel, closing_kernel)
    )
    closed_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    output_path = os.path.join(output_dir, f"{slide_id}_segmentation_mask.png")
    Image.fromarray(closed_mask * 255, mode="L").save(output_path)


def main(csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    predictions = pd.read_csv(csv_path)
    print(f"Processing {len(predictions)} patch predictions...")
    coordinates = predictions["filename"].apply(parse_coords)
    predictions[["slide_id", "x", "y"]] = pd.DataFrame(
        coordinates.tolist(), index=predictions.index
    )
    predictions = predictions.dropna(subset=["slide_id"])
    slide_groups = predictions.groupby("slide_id")
    print(f"Generating heatmaps and segmentation masks for {len(slide_groups)} WSI(s)...")
    for slide_id, group in tqdm(slide_groups):
        probability_grid = build_probability_grid(group)
        save_heatmap(probability_grid, slide_id, output_dir)
        save_segmentation_mask(
            probability_grid, slide_id, output_dir
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate WSI probability heatmaps and binary segmentation masks."
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default="results/WSI_Heatmaps")
    arguments = parser.parse_args()
    main(arguments.csv, arguments.out)
