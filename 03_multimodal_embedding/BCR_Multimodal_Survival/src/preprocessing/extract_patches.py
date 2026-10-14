"""Extract tissue patches directly from an existing WSI directory.

The source slides are opened in place. They are never copied, moved, or linked
into the repository.
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VENDORED_WSITOOLS = ROOT / "WSITools"
if VENDORED_WSITOOLS.is_dir():
    sys.path.insert(0, str(VENDORED_WSITOOLS))

from wsitools.patch_extraction.patch_extractor import ExtractorParameters, PatchExtractor
from wsitools.tissue_detection.tissue_detector import TissueDetector


WSI_EXTENSIONS = {".svs", ".ndpi", ".tif", ".tiff"}


class FlatPatchExtractor(PatchExtractor):
    """Save all patches in one directory with collision-safe names."""

    def generate_patch_fn(self, case_info, patch_loc, label_text=None):
        x, y = int(patch_loc[0]), int(patch_loc[1])
        suffix = "" if label_text is None else f"_{label_text}"
        filename = f"{case_info['fn_str']}_{x}_{y}{suffix}{self.save_format}"
        return os.path.join(self.save_dir, filename)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wsi-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--processes", type=int, default=4)
    parser.add_argument("--threads-per-process", type=int, default=2)
    parser.add_argument("--patch-size", type=int, default=224)
    parser.add_argument("--stride", type=int, default=224)
    parser.add_argument("--sample-count", type=int, default=-1)
    parser.add_argument("--tissue-threshold", type=int, default=85)
    parser.add_argument("--min-tissue-area", type=float, default=0.5)
    return parser.parse_args(argv)


def get_wsi_files(directory: Path) -> list[Path]:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"WSI directory does not exist: {directory}")
    files = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in WSI_EXTENSIONS
    )
    counts = Counter(path.stem.casefold() for path in files)
    duplicates = sorted(stem for stem, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(
            "WSI filenames must have unique stems because patch names use the stem. "
            f"Duplicates: {', '.join(duplicates)}"
        )
    return files


def validate_args(args):
    if args.processes < 1 or args.threads_per_process < 1:
        raise ValueError("process and thread counts must be at least 1")
    if args.patch_size < 1 or args.stride < 1:
        raise ValueError("patch size and stride must be positive")
    if args.sample_count == 0 or args.sample_count < -1:
        raise ValueError("--sample-count must be -1 or a positive integer")
    if not 0 <= args.min_tissue_area <= 1:
        raise ValueError("--min-tissue-area must be between 0 and 1")


def main(argv=None):
    args = parse_args(argv)
    validate_args(args)
    slides = get_wsi_files(args.wsi_dir)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(slides)} WSI(s) in {args.wsi_dir.expanduser().resolve()}")
    if not slides:
        raise FileNotFoundError(
            f"No supported WSI files ({', '.join(sorted(WSI_EXTENSIONS))}) were found"
        )

    effective_processes = min(args.processes, len(slides))
    parameters = ExtractorParameters(
        save_dir=str(output_dir),
        log_dir=str(output_dir / "_extraction_logs"),
        save_format=".png",
        sample_cnt=args.sample_count,
        patch_size=args.patch_size,
        patch_filter_by_area=args.min_tissue_area,
        with_anno=False,
        extract_layer=0,
        stride=args.stride,
        threads=args.threads_per_process,
    )
    extractor = FlatPatchExtractor(
        TissueDetector("LAB_Threshold", threshold=args.tissue_threshold), parameters
    )
    print(
        f"Writing flat patches to {output_dir} with {effective_processes} "
        f"slide process(es); source slides stay in place."
    )
    slide_paths = [str(path) for path in slides]
    if effective_processes == 1:
        # Avoid process-spawn permissions and pickling overhead for small runs.
        counts = [extractor.extract(path) for path in slide_paths]
    else:
        with multiprocessing.Pool(processes=effective_processes) as pool:
            counts = pool.map(extractor.extract, slide_paths)
    print(f"Patch extraction complete: {sum(counts)} patch(es) written.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
