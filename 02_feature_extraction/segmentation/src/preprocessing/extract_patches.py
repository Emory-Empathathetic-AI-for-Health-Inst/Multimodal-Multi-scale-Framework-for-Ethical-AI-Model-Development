import argparse
import multiprocessing
import os
from pathlib import Path

from wsitools.patch_extraction.patch_extractor import ExtractorParameters, PatchExtractor
from wsitools.tissue_detection.tissue_detector import TissueDetector


WSI_EXTENSIONS = {".svs", ".ndpi", ".tif", ".tiff"}


class FlatPatchExtractor(PatchExtractor):
    """Save patches directly in one directory instead of per-slide folders."""

    def generate_patch_fn(self, case_info, patch_loc, label_text=None):
        x, y = (int(patch_loc[0]), int(patch_loc[1]))
        if label_text is None:
            filename = f"{case_info['fn_str']}_{x}_{y}{self.save_format}"
        else:
            filename = f"{case_info['fn_str']}_{x}_{y}_{label_text}{self.save_format}"
        return os.path.join(self.save_dir, filename)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract tissue patches from WSIs into one flat output directory."
    )
    parser.add_argument(
        "--wsi-dir",
        required=True,
        help="Directory containing the source .svs/.ndpi/.tif/.tiff slides.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory in which all extracted PNG patches will be saved.",
    )
    parser.add_argument("--processes", type=int, default=4)
    parser.add_argument("--patch-size", type=int, default=224)
    parser.add_argument("--stride", type=int, default=224)
    parser.add_argument(
        "--sample-count",
        type=int,
        default=-1,
        help="Maximum patches per WSI; -1 extracts every qualifying patch (default).",
    )
    parser.add_argument("--tissue-threshold", type=int, default=85)
    parser.add_argument("--min-tissue-area", type=float, default=0.5)
    return parser.parse_args()


def get_wsi_files(directory):
    wsi_dir = Path(directory).expanduser().resolve()
    if not wsi_dir.is_dir():
        raise NotADirectoryError(f"WSI directory does not exist: {wsi_dir}")

    wsi_files = sorted(
        str(path) for path in wsi_dir.iterdir()
        if path.is_file() and path.suffix.lower() in WSI_EXTENSIONS
    )

    # Patch filenames start with the slide stem, so duplicate stems would overwrite.
    stems = [Path(path).stem for path in wsi_files]
    duplicates = sorted({stem for stem in stems if stems.count(stem) > 1})
    if duplicates:
        raise ValueError(
            "WSI filenames must have unique stems. Duplicate stem(s): "
            + ", ".join(duplicates)
        )
    return wsi_files


def main():
    args = parse_args()
    if args.processes < 1:
        raise ValueError("--processes must be at least 1")
    if args.sample_count == 0 or args.sample_count < -1:
        raise ValueError("--sample-count must be -1 or a positive integer")
    if not 0 <= args.min_tissue_area <= 1:
        raise ValueError("--min-tissue-area must be between 0 and 1")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

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
    )
    extractor = FlatPatchExtractor(
        TissueDetector("LAB_Threshold", threshold=args.tissue_threshold),
        parameters,
    )

    wsi_files = get_wsi_files(args.wsi_dir)
    print(f"Found {len(wsi_files)} WSI(s) in {Path(args.wsi_dir).resolve()}")
    if not wsi_files:
        print("No supported WSIs found; nothing to extract.")
        return

    print(
        f"Extracting with {args.processes} process(es); "
        f"all patches will be written directly to {output_dir}"
    )
    with multiprocessing.Pool(processes=args.processes) as pool:
        patch_counts = pool.map(extractor.extract, wsi_files)

    print(f"Patch extraction completed: {sum(patch_counts)} patch(es) written.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
