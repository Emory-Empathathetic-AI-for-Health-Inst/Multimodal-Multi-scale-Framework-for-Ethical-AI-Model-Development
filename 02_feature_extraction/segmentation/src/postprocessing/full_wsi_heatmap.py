import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import argparse
from tqdm import tqdm

def parse_coords(filename):
    """
    Matches your specific reference format: 
    'CASE_100-1-A-1-H&E_100352_14848_None.png'
    """
    base = os.path.basename(filename)
    # Pattern: [CaseID]_[X]_[Y]_None.png
    match = re.search(r'(.+?)_(\d+)_(\d+)_None\.png$', base)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    return None, None, None

def generate_full_heatmap(df_slide, slide_id, output_dir):
    # 1. Map coordinates to a zero-indexed grid
    # We find all unique X and Y coordinates to determine the 'pixel' in our heatmap
    unique_x = np.sort(df_slide['x'].unique())
    unique_y = np.sort(df_slide['y'].unique())
    
    x_map = {val: i for i, val in enumerate(unique_x)}
    y_map = {val: i for i, val in enumerate(unique_y)}
    
    # 2. Initialize the Grid
    # Rows = Unique Ys, Cols = Unique Xs
    heatmap_grid = np.full((len(unique_y), len(unique_x)), np.nan)

    # 3. Fill the Grid with Probability (Class 0)
    for _, row in df_slide.iterrows():
        grid_x = x_map[row['x']]
        grid_y = y_map[row['y']]
        heatmap_grid[grid_y, grid_x] = row['probability_class0']

    # 4. Plotting the Heatmap
    # RdYlGn_r: Red (High Prob/Cancer) -> Yellow -> Green (Low Prob/Normal)
    plt.figure(figsize=(15, 10))
    current_cmap = plt.cm.get_cmap('RdYlGn_r').copy()
    current_cmap.set_bad(color='white') # Missing patches (background) will be white

    im = plt.imshow(heatmap_grid, cmap=current_cmap, interpolation='nearest', vmin=0, vmax=1)
    
    cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
    cbar.set_label('Cancer Probability (Red = Cancer, Green = Normal)', rotation=270, labelpad=15)
    
    plt.title(f"Full WSI Cancer Map: {slide_id}", fontsize=16)
    plt.axis('off')
    
    # Save high-res PNG
    out_path = os.path.join(output_dir, f"{slide_id}_full_heatmap.png")
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()

def main(csv_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_path)
    print(f"📊 Processing {len(df)} patch predictions...")

    # Parse coordinates
    coords = df['filename'].apply(parse_coords)
    df[['slide_id', 'x', 'y']] = pd.DataFrame(coords.tolist(), index=df.index)
    
    # Drop failed parses
    df = df.dropna(subset=['slide_id'])
    
    slide_groups = df.groupby('slide_id')
    print(f"🧵 Stitching {len(slide_groups)} Full WSI Heatmaps...")

    for slide_id, group in tqdm(slide_groups):
        generate_full_heatmap(group, slide_id, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True)
    parser.add_argument("--out", type=str, default="results/full_wsi_heatmaps")
    args = parser.parse_args()
    main(args.csv, args.out)
