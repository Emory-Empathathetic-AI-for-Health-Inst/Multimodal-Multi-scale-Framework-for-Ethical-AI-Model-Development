"""Run the complete BCR multimodal survival pipeline with one command."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGES = ("extract", "normalize", "embed", "classify", "heatmap", "filter", "mil", "mri", "fusion", "evaluate")
WSI_EXTENSIONS = {".svs", ".ndpi", ".tif", ".tiff"}
MRI_EXTENSIONS = (".nii", ".nii.gz", ".mha", ".mhd")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir", required=True, type=Path,
        help="Existing folder containing WSI files and/or MRI patient folders.",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "run")
    parser.add_argument("--wsi-dir", type=Path, default=None)
    parser.add_argument("--mri-dir", type=Path, default=None)
    parser.add_argument("--clinical-csv", type=Path, default=None)
    parser.add_argument("--hf-token", default=None, help="Prefer setting HF_TOKEN.")
    parser.add_argument("--uni-checkpoint", type=Path, default=None)
    parser.add_argument(
        "--classifier", type=Path,
        default=ROOT / "checkpoints/pathology/prostate_uni2_model.joblib",
    )
    parser.add_argument(
        "--mil-checkpoint", type=Path,
        default=ROOT / "checkpoints/pathology/best_mil_chimera_surv.pth",
    )
    parser.add_argument(
        "--mri-checkpoint", type=Path,
        default=ROOT / "MRI_CORE_FEATURE_EXTRACTION/weights/mri_foundation.pth",
    )
    parser.add_argument(
        "--fusion-checkpoint", type=Path,
        default=ROOT / "checkpoints/fusion/best_fusion_chimera_surv.pth",
    )
    parser.add_argument(
        "--reference-patch", type=Path,
        default=ROOT / "data/reference/reference-patch.png",
    )
    parser.add_argument("--processes", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--threads-per-process", type=int, default=2)
    parser.add_argument("--sample-count", type=int, default=-1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--precision", choices=("float32", "float16"), default="float32")
    parser.add_argument("--start-at", choices=STAGES, default="extract")
    parser.add_argument("--stop-after", choices=STAGES, default="fusion")
    parser.add_argument("--force", action="store_true", help="Rerun selected completed stages.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and show work only.")
    return parser.parse_args(argv)


def now():
    return datetime.now(timezone.utc).isoformat()


def contains_wsi(directory: Path) -> bool:
    return directory.is_dir() and any(
        path.is_file() and path.suffix.lower() in WSI_EXTENSIONS for path in directory.iterdir()
    )


def contains_mri_cases(directory: Path) -> bool:
    if not directory.is_dir():
        return False
    return any(
        child.is_dir()
        and any(path.is_file() and path.name.lower().endswith(MRI_EXTENSIONS) for path in child.iterdir())
        for child in directory.iterdir()
    )


def save_manifest(path, manifest):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(path)


def output_exists(stage, paths):
    target = paths[stage]
    if stage in {"extract", "heatmap", "mri"}:
        extensions = {"extract": ".png", "heatmap": ".png", "mri": ".npy"}
        return target.is_dir() and any(target.glob(f"*{extensions[stage]}"))
    return target.is_file() and target.stat().st_size > 0


def run_stage(stage, command, env, log_dir, manifest, manifest_path):
    stdout_path = log_dir / f"{stage}.stdout.log"
    stderr_path = log_dir / f"{stage}.stderr.log"
    manifest["stages"][stage] = {"status": "running", "started_at": now()}
    save_manifest(manifest_path, manifest)
    print(f"\n[{stage}] starting")
    with stdout_path.open("a", encoding="utf-8") as stdout, stderr_path.open("a", encoding="utf-8") as stderr:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    if result.returncode:
        manifest["stages"][stage].update(status="failed", finished_at=now(), exit_code=result.returncode)
        save_manifest(manifest_path, manifest)
        tail = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()[-12:]
        details = "\n".join(tail)
        raise RuntimeError(f"Stage '{stage}' failed. See {stderr_path}\n{details}")
    manifest["stages"][stage].update(status="complete", finished_at=now())
    save_manifest(manifest_path, manifest)
    print(f"[{stage}] complete")


def main(argv=None):
    args = parse_args(argv)
    first, last = STAGES.index(args.start_at), STAGES.index(args.stop_after)
    if first > last:
        raise ValueError("--start-at must not come after --stop-after")
    data_dir = args.data_dir.expanduser().resolve()
    wsi_dir = (args.wsi_dir or data_dir).expanduser().resolve()
    mri_dir = (args.mri_dir or data_dir).expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Data directory does not exist: {data_dir}")

    selected = STAGES[first:last + 1]
    if any(stage in selected for stage in STAGES[:7]) and not contains_wsi(wsi_dir):
        raise FileNotFoundError(f"No supported WSI files found directly in {wsi_dir}")
    if any(stage in selected for stage in ("mri", "fusion")) and not contains_mri_cases(mri_dir):
        raise FileNotFoundError(f"No MRI patient folders found directly in {mri_dir}")
    if "evaluate" in selected and not args.clinical_csv:
        raise ValueError("--clinical-csv is required when evaluation is selected")
    required_files = {}
    if "normalize" in selected:
        required_files["reference patch"] = args.reference_patch
    if "classify" in selected:
        required_files["pathology classifier"] = args.classifier
    if "mil" in selected:
        required_files["pathology MIL checkpoint"] = args.mil_checkpoint
    if "mri" in selected:
        required_files["MRI foundation checkpoint"] = args.mri_checkpoint
        required_files["SAM checkpoint"] = ROOT / "MRI_CORE_FEATURE_EXTRACTION/weights/sam_vit_b_01ec64.pth"
    if "fusion" in selected:
        required_files["fusion checkpoint"] = args.fusion_checkpoint
    if args.uni_checkpoint and "embed" in selected:
        required_files["local UNI2-h checkpoint"] = args.uni_checkpoint
    if args.clinical_csv and "evaluate" in selected:
        required_files["clinical CSV"] = args.clinical_csv
    for label, path in required_files.items():
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Missing {label}: {resolved}")

    patch_dir = output_dir / "patches"
    pathology_dir = output_dir / "pathology"
    mri_output = output_dir / "mri"
    fusion_dir = output_dir / "fusion"
    heatmap_dir = output_dir / "heatmaps"
    log_dir = output_dir / "logs"
    embeddings = pathology_dir / "patch_embeddings.h5"
    predictions = pathology_dir / "patch_predictions.csv"
    cancer_embeddings = pathology_dir / "cancer_embeddings.h5"
    pathology_vectors = pathology_dir / "pathology_vectors.pt"
    evaluation_metrics = fusion_dir / "evaluation/metrics.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(exist_ok=True)
    paths = {
        "extract": patch_dir, "normalize": output_dir / ".normalization_complete",
        "embed": embeddings, "classify": predictions, "heatmap": heatmap_dir,
        "filter": cancer_embeddings, "mil": pathology_vectors, "mri": mri_output,
        "fusion": fusion_dir / "fusion_predictions.csv", "evaluate": evaluation_metrics,
    }

    python = sys.executable
    commands = {
        "extract": [python, str(ROOT / "src/preprocessing/extract_patches.py"), "--wsi-dir", str(wsi_dir), "--output-dir", str(patch_dir), "--processes", str(args.processes), "--threads-per-process", str(args.threads_per_process), "--sample-count", str(args.sample_count)],
        "normalize": [python, str(ROOT / "src/preprocessing/normalize_stains.py"), "--data-dir", str(patch_dir), "--reference-patch", str(args.reference_patch.expanduser().resolve())],
        "embed": [python, str(ROOT / "src/inference/extract_features.py"), "--data-dir", str(patch_dir), "--output-path", str(embeddings), "--batch-size", str(args.batch_size), "--num-workers", str(args.num_workers), "--precision", args.precision, "--resume"],
        "classify": [python, str(ROOT / "src/inference/classify_h5.py"), "--h5", str(embeddings), "--model", str(args.classifier.expanduser().resolve()), "--output", str(predictions)],
        "heatmap": [python, str(ROOT / "src/postprocessing/full_wsi_heatmap.py"), "--csv", str(predictions), "--out", str(heatmap_dir)],
        "filter": [python, str(ROOT / "src/pathology/filter_cancer.py"), "--h5", str(embeddings), "--predictions", str(predictions), "--wsi_dir", str(wsi_dir), "--output", str(cancer_embeddings)],
        "mil": [python, str(ROOT / "src/pathology/mil_inference.py"), "--h5", str(cancer_embeddings), "--ckpt", str(args.mil_checkpoint.expanduser().resolve()), "--output", str(pathology_vectors)],
        "mri": [python, str(ROOT / "MRI_CORE_FEATURE_EXTRACTION/extract_features.py"), "--data-dir", str(mri_dir), "--output-dir", str(mri_output), "--checkpoint", str(args.mri_checkpoint.expanduser().resolve())],
        "fusion": [python, str(ROOT / "src/fusion/run_fusion.py"), "--pathology_vectors", str(pathology_vectors), "--mri_dir", str(mri_output), "--checkpoint", str(args.fusion_checkpoint.expanduser().resolve()), "--output_dir", str(fusion_dir)],
        "evaluate": [python, str(ROOT / "src/evaluation/evaluate_survival.py"), "--predictions", str(fusion_dir / "fusion_predictions.csv"), "--clinical_csv", str(args.clinical_csv.expanduser().resolve()) if args.clinical_csv else "", "--output_dir", str(fusion_dir / "evaluation"), "--save_km_plot"],
    }
    if args.uni_checkpoint:
        commands["embed"].extend(["--checkpoint", str(args.uni_checkpoint.expanduser().resolve())])

    manifest_path = output_dir / "pipeline_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "created_at": now(), "data_dir": str(data_dir), "wsi_dir": str(wsi_dir),
        "mri_dir": str(mri_dir), "output_dir": str(output_dir), "stages": {},
    }
    for key, value in (("data_dir", data_dir), ("wsi_dir", wsi_dir), ("mri_dir", mri_dir)):
        previous = manifest.get(key)
        if previous and Path(previous) != value and not args.force:
            raise ValueError(
                f"This output directory was used with a different {key}: {previous}. "
                "Choose another --output-dir, or use --force intentionally."
            )
    env = os.environ.copy()
    if args.hf_token:
        env["HF_TOKEN"] = args.hf_token

    print(f"Data stays at: {data_dir}")
    print(f"Outputs go to: {output_dir}")
    print(f"Selected stages: {', '.join(selected)}")
    if args.dry_run:
        print("Dry run successful: inputs were discovered and no processing was started.")
        return
    for stage in selected:
        previous_complete = manifest.get("stages", {}).get(stage, {}).get("status") == "complete"
        if not args.force and previous_complete and output_exists(stage, paths):
            print(f"[{stage}] already complete; skipping")
            continue
        run_stage(stage, commands[stage], env, log_dir, manifest, manifest_path)
        if stage == "normalize":
            paths[stage].write_text(now(), encoding="utf-8")
    manifest.update(status="complete", finished_at=now())
    save_manifest(manifest_path, manifest)
    print(f"\nPipeline complete. Results: {output_dir}")


if __name__ == "__main__":
    main()
