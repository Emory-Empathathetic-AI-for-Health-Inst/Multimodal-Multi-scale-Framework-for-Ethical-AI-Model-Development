"""Run the complete WSI segmentation pipeline from one command."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGES = ("extract", "normalize", "embed", "classify", "heatmap")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wsi-dir", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument(
        "--hf-token", default=None,
        help="Hugging Face token; prefer setting HF_TOKEN instead.",
    )
    parser.add_argument(
        "--model", type=Path,
        default=ROOT / "models" / "prostate_uni2_model.joblib",
    )
    parser.add_argument(
        "--reference-patch", type=Path,
        default=ROOT / "data" / "ref_patch" / "reference-patch.png",
    )
    parser.add_argument("--processes", type=int, default=4)
    parser.add_argument("--patch-size", type=int, default=224)
    parser.add_argument("--stride", type=int, default=224)
    parser.add_argument("--tissue-threshold", type=int, default=85)
    parser.add_argument("--min-tissue-area", type=float, default=0.5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--torch-threads", type=int, default=None)
    parser.add_argument("--precision", choices=("float32", "float16"), default="float32")
    parser.add_argument(
        "--checkpoint", type=Path, default=None,
        help="Optional local UNI2-h state dict for offline/low-memory runs.",
    )
    parser.add_argument("--start-at", choices=STAGES, default="extract")
    parser.add_argument("--stop-after", choices=STAGES, default="heatmap")
    parser.add_argument(
        "--delete-patches-after-embedding", action="store_true",
        help="Delete patch PNGs only after embeddings are verified.",
    )
    return parser.parse_args()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def save_manifest(path, manifest):
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def run_stage(name, command, env, log_dir, manifest, manifest_path):
    stdout_path = log_dir / f"{name}.stdout.log"
    stderr_path = log_dir / f"{name}.stderr.log"
    manifest["stages"][name] = {"status": "running", "started_at": utc_now()}
    save_manifest(manifest_path, manifest)
    print(f"\n[{name}] {' '.join(map(str, command))}")
    with stdout_path.open("a", encoding="utf-8") as stdout, stderr_path.open(
        "a", encoding="utf-8"
    ) as stderr:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    if result.returncode:
        manifest["stages"][name].update(
            status="failed", finished_at=utc_now(), exit_code=result.returncode
        )
        save_manifest(manifest_path, manifest)
        raise RuntimeError(
            f"Stage '{name}' failed. See {stdout_path} and {stderr_path}"
        )
    manifest["stages"][name].update(status="complete", finished_at=utc_now())
    save_manifest(manifest_path, manifest)
    print(f"[{name}] complete")


def remove_patch_pngs(patch_dir):
    removed = 0
    for extension in ("*.png", "*.jpg", "*.jpeg"):
        for path in patch_dir.glob(extension):
            path.unlink()
            removed += 1
    return removed


def main():
    args = parse_args()
    start_index = STAGES.index(args.start_at)
    stop_index = STAGES.index(args.stop_after)
    if start_index > stop_index:
        raise ValueError("--start-at must not come after --stop-after")

    wsi_dir = args.wsi_dir.expanduser().resolve()
    run_dir = args.run_dir.expanduser().resolve()
    model = args.model.expanduser().resolve()
    reference = args.reference_patch.expanduser().resolve()
    checkpoint = args.checkpoint.expanduser().resolve() if args.checkpoint else None
    if not wsi_dir.is_dir():
        raise NotADirectoryError(wsi_dir)
    if not model.is_file():
        raise FileNotFoundError(model)
    if not reference.is_file():
        raise FileNotFoundError(reference)
    if checkpoint and not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)

    patch_dir = run_dir / "patches"
    log_dir = run_dir / "logs"
    heatmap_dir = run_dir / "heatmaps"
    embeddings = run_dir / "patch_embeddings.h5"
    predictions = run_dir / "patch_predictions.csv"
    normalization_marker = run_dir / ".normalization_complete"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(exist_ok=True)

    manifest_path = run_dir / "pipeline_manifest.json"
    manifest = {
        "created_at": utc_now(),
        "wsi_dir": str(wsi_dir),
        "run_dir": str(run_dir),
        "stages": {},
    }
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    env = os.environ.copy()
    if args.hf_token:
        env["HF_TOKEN"] = args.hf_token
    python = sys.executable
    commands = {
        "extract": [
            python, str(ROOT / "src/preprocessing/extract_patches.py"),
            "--wsi-dir", str(wsi_dir), "--output-dir", str(patch_dir),
            "--processes", str(args.processes), "--patch-size", str(args.patch_size),
            "--stride", str(args.stride), "--tissue-threshold", str(args.tissue_threshold),
            "--min-tissue-area", str(args.min_tissue_area), "--sample-count", "-1",
        ],
        "normalize": [
            python, str(ROOT / "src/preprocessing/normalize_stains.py"),
            "--data-dir", str(patch_dir), "--reference-patch", str(reference),
        ],
        "embed": [
            python, str(ROOT / "src/inference/extract_features.py"),
            "--data-dir", str(patch_dir), "--output-path", str(embeddings),
            "--batch_size", str(args.batch_size), "--num-workers", str(args.num_workers),
            "--precision", args.precision, "--resume",
        ],
        "classify": [
            python, str(ROOT / "src/inference/classify_h5.py"),
            "--h5", str(embeddings), "--model", str(model), "--output", str(predictions),
        ],
        "heatmap": [
            python, str(ROOT / "src/postprocessing/full_wsi_heatmap.py"),
            "--csv", str(predictions), "--out", str(heatmap_dir),
        ],
    }
    if args.torch_threads is not None:
        commands["embed"].extend(["--torch-threads", str(args.torch_threads)])
    if checkpoint:
        commands["embed"].extend(["--checkpoint", str(checkpoint)])

    selected = STAGES[start_index:stop_index + 1]
    for stage in selected:
        if stage == "normalize" and normalization_marker.exists():
            print("[normalize] already complete; skipping to prevent double normalization")
            continue
        run_stage(stage, commands[stage], env, log_dir, manifest, manifest_path)
        if stage == "normalize":
            normalization_marker.write_text(utc_now(), encoding="utf-8")
        if stage == "embed" and args.delete_patches_after_embedding:
            removed = remove_patch_pngs(patch_dir)
            print(f"[cleanup] removed {removed} patch image(s) after embedding")

    manifest["status"] = "complete" if args.stop_after == "heatmap" else "stopped"
    manifest["finished_at"] = utc_now()
    save_manifest(manifest_path, manifest)
    print(f"\nPipeline finished. Outputs: {run_dir}")


if __name__ == "__main__":
    main()
