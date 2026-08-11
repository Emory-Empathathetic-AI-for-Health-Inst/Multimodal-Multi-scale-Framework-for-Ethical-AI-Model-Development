import argparse
import os

import h5py
import numpy as np
import timm
import torch
from PIL import Image, UnidentifiedImageError
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser(description="UNI2-h Feature Extraction")
    parser.add_argument(
        "--token", type=str, default=None,
        help="Hugging Face token. If omitted, uses the HF_TOKEN environment variable.",
    )
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument(
        "--data_dir", required=True,
        help="Directory containing the normalized patches",
    )
    parser.add_argument("--output_path", required=True, help="Output H5 file")
    return parser.parse_args()


class PatchDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = sorted(
            os.path.join(root_dir, filename)
            for filename in os.listdir(root_dir)
            if filename.lower().endswith((".png", ".jpg", ".jpeg"))
        )

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert("RGB")
            if self.transform:
                image = self.transform(image)
            return {"image": image, "filename": os.path.basename(img_path)}
        except (UnidentifiedImageError, OSError, ValueError):
            return None


def collate_fn_safe(batch):
    batch = [item for item in batch if item is not None]
    if not batch:
        return None
    return torch.utils.data.dataloader.default_collate(batch)


def extract(args):
    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError("Provide --token or set the HF_TOKEN environment variable")
    os.environ["HF_TOKEN"] = token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading UNI2-h on {device}...")
    timm_kwargs = {
        "img_size": 224, "patch_size": 14, "depth": 24, "num_heads": 24,
        "init_values": 1e-5, "embed_dim": 1536, "mlp_ratio": 5.33334,
        "num_classes": 0, "no_embed_class": True,
        "mlp_layer": timm.layers.SwiGLUPacked,
        "act_layer": torch.nn.SiLU, "reg_tokens": 8,
        "dynamic_img_size": True,
    }
    model = timm.create_model(
        "hf-hub:MahmoodLab/UNI2-h", pretrained=True, **timm_kwargs
    )
    transform = create_transform(
        **resolve_data_config(model.pretrained_cfg, model=model)
    )
    model.eval().to(device)

    dataset = PatchDataset(args.data_dir, transform=transform)
    dataloader = DataLoader(
        dataset, batch_size=args.batch_size, shuffle=False, num_workers=4,
        collate_fn=collate_fn_safe,
    )

    all_embeddings = []
    all_filenames = []
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Extracting Features"):
            if batch is None:
                continue
            features = model(batch["image"].to(device))
            all_embeddings.append(features.cpu().numpy())
            all_filenames.extend(batch["filename"])

    if not all_embeddings:
        raise ValueError(f"No readable patch images found in {args.data_dir}")

    embeddings = np.concatenate(all_embeddings, axis=0)
    filenames = [name.encode("utf-8") for name in all_filenames]
    os.makedirs(os.path.dirname(os.path.abspath(args.output_path)), exist_ok=True)
    with h5py.File(args.output_path, "w") as output_h5:
        output_h5.create_dataset("embeddings", data=embeddings)
        output_h5.create_dataset("filenames", data=filenames)

    print(f"Successfully saved {len(all_filenames)} features to {args.output_path}")


if __name__ == "__main__":
    extract(get_args())
