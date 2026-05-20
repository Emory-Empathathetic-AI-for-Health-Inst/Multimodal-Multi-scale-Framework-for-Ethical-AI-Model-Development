# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 13:28:40 2025
@author: zzha962
"""
import os
import time
import numpy as np
import torch
import openslide
from PIL import Image
import cv2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import argparse

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from Cancer_expert_model import *

# === Config ===
parser = argparse.ArgumentParser(description='PCa diagnosis MoE systerm')
parser.add_argument('--data_root', type=str, default='./VA2024/wsi', help='Directory to data root')
parser.add_argument('--level_10x', type=int, default=1, help='Magnification 10X level num')
parser.add_argument('--tile_size_10x', type=int, default=512, help='Running patch size under 10X')
parser.add_argument('--max_threads', type=int, default=16, help='Number of CPU thread')
parser.add_argument('--device', type=str, default='cuda:0', help='Cuda running')
opt = parser.parse_args()

stride_10x = opt.tile_size_10x // 8
selected_backbones = ['clip', 'conch', 'musk', 'densenet', 'resnet', 'vgg']
backbone_dims = {
    'clip': 512,
    'conch': 512,
    'musk': 1024,
    'densnet': 1024,
    'resnet': 512,
    'vgg': 4096,
}

# === Load model and feature extractors ===
model = MoEClassifier(backbone_dims).to(opt.device)
model.load_state_dict(torch.load('moe_patch_classifier.pth'))
model.eval()

extractors = {
    'resnet': get_resnet_feature_extractor(opt.device),
    'vgg': get_vgg_feature_extractor(opt.device),
    'densenet': get_densenet_feature_extractor(opt.device),
    'musk': get_musk_feature_extractor(opt.device),
    'conch': get_conch_feature_extractor(opt.device),
    'clip': CLIPFeatureExtractor(device=opt.device).extract_features,
}

def create_overlay(base, heatmap):
    norm = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-6)
    color = cv2.applyColorMap((norm * 255).astype(np.uint8), cv2.COLORMAP_JET)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    return (0.5 * base.astype(np.float32) + 0.5 * color.astype(np.float32)).astype(np.uint8)

def extract_features_batch(patches):
    feature_list = []
    for patch in patches:
        feat_vecs = []
        for b in selected_backbones:
            with torch.no_grad():
                feat = extractors[b](patch)
                if isinstance(feat, np.ndarray):
                    feat = torch.tensor(feat, dtype=torch.float32)
            feat_vecs.append(feat)
        full_feat = torch.cat(feat_vecs, dim=0)
        feature_list.append(full_feat)
    return torch.stack(feature_list).to(opt.device)

# === Process all WSIs ===
supported_exts = ('.svs', '.tif', '.tiff', '.ndpi', '.mrxs', '.scn')
wsi_files = [f for f in os.listdir(os.path.join(opt.data_root,'wsi')) if f.lower().endswith(supported_exts)]
results_log = []

for fname in tqdm(wsi_files, desc="Processing WSIs"):
    start_time = time.time()
    wsi_path = os.path.join(opt.data_root, 'wsi', fname)
    slide = openslide.OpenSlide(wsi_path)
    w, h = slide.level_dimensions[opt.level_10x]

    # Tiling
    def extract_patch(x, y):
        patch = slide.read_region((x * 4, y * 4), opt.level_10x, (opt.tile_size_10x, opt.tile_size_10x)).convert("RGB")
        if np.array(patch).mean() > 230:
            return None
        return (x, y, patch)

    tile_coords = [(x, y) for y in range(0, h - opt.tile_size_10x + 1, stride_10x)
                          for x in range(0, w - opt.tile_size_10x + 1, stride_10x)]
    
    patches = []
    with ThreadPoolExecutor(max_workers=opt.max_threads) as executor:
        for result in tqdm(executor.map(lambda xy: extract_patch(*xy), tile_coords), total=len(tile_coords), desc="Tiling"):
            if result:
                patches.append(result)
    print(f"✅ Extracted {len(patches)} valid patches.")

    heatmap = np.zeros((h, w), dtype=np.float32)
    count_map = np.ones_like(heatmap)
    visited_mask = np.zeros_like(heatmap, dtype=bool)
    expert_maps = {b: np.zeros_like(heatmap) for b in selected_backbones}
    patch_logits, patch_weights = [], []

    batch_size = 64
    # Run batches
    for i in tqdm(range(0, len(patches), batch_size), desc="Batch Classification"):
        batch = patches[i:i+batch_size]
        coords, images = zip(*[(p[0:2], p[2]) for p in batch])
        features = extract_features_batch(images)

        with torch.no_grad():
            split_feats = torch.split(features, model.backbone_dims_list, dim=1)
            expert_outputs = torch.cat([model.experts[name](f) for name, f in zip(model.backbones, split_feats)], dim=1)
            gate_weights = model.gate(features)
            logits = torch.sum(expert_outputs * gate_weights, dim=1)
            probs = torch.sigmoid(logits).cpu().numpy()
            per_expert_probs = torch.sigmoid(expert_outputs).cpu().numpy()
            max_weights = gate_weights.max(dim=1).values.cpu().numpy()

        for j, (x, y) in enumerate(coords):
            prob = probs[j]
            patch_logits.append(prob)
            patch_weights.append(max_weights[j])
            heatmap[y:y+opt.tile_size_10x, x:x+opt.tile_size_10x] += prob
            count_map[y:y+opt.tile_size_10x, x:x+opt.tile_size_10x] += 1
            visited_mask[y:y+opt.tile_size_10x, x:x+opt.tile_size_10x] = True
            for idx, b in enumerate(selected_backbones):
                expert_maps[b][y:y+opt.tile_size_10x, x:x+opt.tile_size_10x] += per_expert_probs[j, idx]

    # Normalize
    heatmap_final = heatmap / count_map
    for b in selected_backbones:
        expert_maps[b][visited_mask] /= count_map[visited_mask]

    # WSI score
    patch_logits = np.array(patch_logits)
    patch_weights = np.array(patch_weights)
    patch_weights /= (patch_weights.sum() + 1e-6)
    wsi_score = np.sum(patch_logits * patch_weights)

    # Output directory
    out_dir = os.path.join(opt.data_root, 'WSI_predictions', os.path.splitext(fname)[0])
    os.makedirs(out_dir, exist_ok=True)

    np.save(os.path.join(out_dir, 'heatmap.npy'), heatmap_final)
    np.save(os.path.join(out_dir, 'patch_scores.npy'), patch_logits * patch_weights)

    rgb_10x = np.array(slide.read_region((0, 0), opt.level_10x, (w, h)).convert("RGB"))
    overlay = create_overlay(rgb_10x, heatmap_final)
    H_, W_ = overlay.shape[:2]
    cv2.putText(overlay, f"WSI Cancer Risk Score: {wsi_score:.4f}", (int(W_*0.4), int(H_/2)),
                cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 0, 0), 20)
    Image.fromarray(overlay).save(os.path.join(out_dir, 'overlay_w_score.png'))

    # Expert overlays
    expert_dir = os.path.join(out_dir, "expert_heatmaps")
    os.makedirs(expert_dir, exist_ok=True)
    for idx, b in enumerate(selected_backbones):
        overlay_b = create_overlay(rgb_10x, expert_maps[b])
        Image.fromarray(overlay_b).save(os.path.join(expert_dir, f"{b}_overlay.png"))

    # Log
    time_elapsed = time.time() - start_time
    results_log.append({
        'WSI': fname,
        'RiskScore': round(wsi_score, 10),
        'Patches': len(patches),
        'TimeSeconds': round(time_elapsed, 2),
        'TimeMinutes': round(time_elapsed / 60, 3)
    })

# Save CSV log
log_df = pd.DataFrame(results_log)
log_df.to_csv(os.path.join(opt.data_root,'WSI_predictions','WSI_running_log.csv'), index=False)
print("✅ All WSIs processed. Log saved to WSI_running_log.csv")



