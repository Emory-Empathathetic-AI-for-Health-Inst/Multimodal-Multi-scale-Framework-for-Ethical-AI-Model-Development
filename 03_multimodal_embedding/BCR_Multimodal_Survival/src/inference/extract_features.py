"""Extract UNI2-h patch embeddings with bounded memory and resume support."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import h5py
import numpy as np
import timm
import torch
from PIL import Image, UnidentifiedImageError
from huggingface_hub import try_to_load_from_cache
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def get_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--token", default=None,
        help="Hugging Face token. Prefer the HF_TOKEN environment variable.",
    )
    parser.add_argument("--batch-size", "--batch_size", dest="batch_size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--torch-threads", type=int, default=None)
    parser.add_argument("--precision", choices=("float32", "float16"), default="float32")
    parser.add_argument("--data-dir", "--data_dir", dest="data_dir", required=True, type=Path)
    parser.add_argument(
        "--output-path", "--output_path", dest="output_path", required=True, type=Path
    )
    parser.add_argument(
        "--checkpoint", type=Path, default=None,
        help="Optional local UNI2-h state dict; allows offline inference.",
    )
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


class PatchDataset(Dataset):
    def __init__(self, paths, transform=None):
        self.image_paths = list(paths)
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        path = self.image_paths[idx]
        try:
            with Image.open(path) as source:
                image = source.convert("RGB")
            if self.transform:
                image = self.transform(image)
            return {"image": image, "filename": path.name}
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            print(f"Skipping unreadable patch {path}: {exc}")
            return None


def collate_fn_safe(batch):
    valid = [item for item in batch if item is not None]
    return torch.utils.data.dataloader.default_collate(valid) if valid else None


def model_kwargs():
    return {
        "img_size": 224,
        "patch_size": 14,
        "depth": 24,
        "num_heads": 24,
        "init_values": 1e-5,
        "embed_dim": 1536,
        "mlp_ratio": 5.33334,
        "num_classes": 0,
        "no_embed_class": True,
        "mlp_layer": timm.layers.SwiGLUPacked,
        "act_layer": torch.nn.SiLU,
        "reg_tokens": 8,
        "dynamic_img_size": True,
    }


def unwrap_state_dict(obj):
    if isinstance(obj, dict):
        for key in ("state_dict", "model_state_dict", "model", "weights"):
            if isinstance(obj.get(key), dict):
                return obj[key]
    return obj


def load_model(checkpoint: Path | None):
    if checkpoint:
        checkpoint = checkpoint.expanduser().resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(f"UNI2-h checkpoint not found: {checkpoint}")
        model = timm.create_model("vit_giant_patch14_224", pretrained=False, **model_kwargs())
        state = unwrap_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=False))
        model.load_state_dict(state, strict=True)
        return model
    cached = try_to_load_from_cache("MahmoodLab/UNI2-h", "pytorch_model.bin")
    if isinstance(cached, str) and Path(cached).is_file():
        print(f"Using cached UNI2-h weights: {cached}")
        return load_model(Path(cached))
    try:
        return timm.create_model(
            "hf-hub:MahmoodLab/UNI2-h", pretrained=True, **model_kwargs()
        )
    except Exception as exc:
        raise RuntimeError(
            "UNI2-h could not be loaded. Request model access, set HF_TOKEN, or "
            "use --checkpoint with a local state dict."
        ) from exc


def existing_filenames(output_path: Path) -> set[str]:
    if not output_path.is_file():
        return set()
    with h5py.File(output_path, "r") as handle:
        if not {"embeddings", "filenames"}.issubset(handle.keys()):
            raise ValueError(f"Cannot resume: incompatible H5 file {output_path}")
        if len(handle["embeddings"]) != len(handle["filenames"]):
            raise ValueError(f"Cannot resume: dataset lengths differ in {output_path}")
        return {
            value.decode("utf-8") if isinstance(value, bytes) else str(value)
            for value in handle["filenames"][:]
        }


def append_batch(handle, embeddings: np.ndarray, filenames: list[str]):
    if "embeddings" not in handle:
        handle.create_dataset(
            "embeddings", data=embeddings, maxshape=(None, embeddings.shape[1]), chunks=True
        )
        string_type = h5py.string_dtype(encoding="utf-8")
        handle.create_dataset(
            "filenames", data=np.asarray(filenames, dtype=object), dtype=string_type,
            maxshape=(None,), chunks=True,
        )
        return
    start = len(handle["filenames"])
    stop = start + len(filenames)
    handle["embeddings"].resize(stop, axis=0)
    handle["embeddings"][start:stop] = embeddings
    handle["filenames"].resize(stop, axis=0)
    handle["filenames"][start:stop] = filenames


def extract(args):
    if args.token:
        os.environ["HF_TOKEN"] = args.token
    if args.batch_size < 1 or args.num_workers < 0:
        raise ValueError("batch size must be positive and worker count cannot be negative")
    if args.torch_threads:
        torch.set_num_threads(args.torch_threads)

    data_dir = args.data_dir.expanduser().resolve()
    output_path = args.output_path.expanduser().resolve()
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Patch directory does not exist: {data_dir}")
    all_paths = sorted(path for path in data_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
    completed = existing_filenames(output_path) if args.resume else set()
    paths = [path for path in all_paths if path.name not in completed]
    if not paths:
        if completed:
            print(f"All {len(completed)} patch embeddings already exist; nothing to do.")
            return
        raise FileNotFoundError(f"No patch images found in {data_dir}")
    if output_path.exists() and not args.resume:
        output_path.unlink()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if args.precision == "float16" and device.type != "cuda":
        raise ValueError("float16 inference requires CUDA; use --precision float32 on CPU")
    print(f"Loading UNI2-h on {device}; {len(paths)} patch(es) remain.")
    model = load_model(args.checkpoint)
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))
    model.eval().to(device)
    loader = DataLoader(
        PatchDataset(paths, transform), batch_size=args.batch_size, shuffle=False,
        num_workers=args.num_workers, collate_fn=collate_fn_safe,
        pin_memory=device.type == "cuda",
    )

    with h5py.File(output_path, "a") as handle, torch.inference_mode():
        for batch in tqdm(loader, desc="Extracting features"):
            if batch is None:
                continue
            images = batch["image"].to(device, non_blocking=True)
            with torch.autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=args.precision == "float16",
            ):
                features = model(images)
            append_batch(handle, features.float().cpu().numpy(), list(batch["filename"]))
            handle.flush()
    print(f"Saved embeddings to {output_path}")


if __name__ == "__main__":
    extract(get_args())
