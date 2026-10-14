"""Create patch-grid probability heatmaps and binary segmentation masks."""

import argparse
import re
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm


def parse_coords(filename):
    match = re.search(r"(.+?)_(\d+)_(\d+)(?:_None)?\.(?:png|jpe?g)$", Path(filename).name, re.I)
    return (match.group(1), int(match.group(2)), int(match.group(3))) if match else (None, None, None)


def probability_grid(group):
    xs, ys = np.sort(group["x"].unique()), np.sort(group["y"].unique())
    x_index = {value: index for index, value in enumerate(xs)}
    y_index = {value: index for index, value in enumerate(ys)}
    grid = np.full((len(ys), len(xs)), np.nan, dtype=np.float32)
    for row in group.itertuples():
        grid[y_index[row.y], x_index[row.x]] = row.cancer_probability
    return grid


def save_outputs(grid, slide_id, output_dir):
    color_map = plt.colormaps["RdYlGn_r"].copy()
    color_map.set_bad(color="white")
    figure, axis = plt.subplots(figsize=(15, 10))
    image = axis.imshow(grid, cmap=color_map, interpolation="nearest", vmin=0, vmax=1)
    figure.colorbar(image, ax=axis, label="Cancer probability")
    axis.set_title(f"Full WSI cancer map: {slide_id}")
    axis.axis("off")
    figure.savefig(output_dir / f"{slide_id}_full_heatmap.png", bbox_inches="tight", dpi=300)
    plt.close(figure)

    binary = np.where(np.isfinite(grid) & (grid >= 0.5), 1, 0).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    Image.fromarray(closed * 255, mode="L").save(output_dir / f"{slide_id}_segmentation_mask.png")


def main(csv_path, output_dir):
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions = pd.read_csv(csv_path)
    required = {"filename"}
    if not required.issubset(predictions.columns):
        raise KeyError(f"Predictions CSV must contain {sorted(required)}")
    if "cancer_probability" not in predictions:
        if "probability_class0" not in predictions:
            raise KeyError("Predictions CSV has no cancer probability column")
        predictions["cancer_probability"] = predictions["probability_class0"]
    coordinates = predictions["filename"].map(parse_coords)
    predictions[["slide_id", "x", "y"]] = pd.DataFrame(coordinates.tolist(), index=predictions.index)
    predictions = predictions.dropna(subset=["slide_id"])
    if predictions.empty:
        raise ValueError("No patch coordinates could be parsed from prediction filenames")
    for slide_id, group in tqdm(predictions.groupby("slide_id"), desc="WSI heatmaps"):
        save_outputs(probability_grid(group), slide_id, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()
    main(arguments.csv, arguments.out)
