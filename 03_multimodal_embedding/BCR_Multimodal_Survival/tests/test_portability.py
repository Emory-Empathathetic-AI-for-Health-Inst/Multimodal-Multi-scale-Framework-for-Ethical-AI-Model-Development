import importlib.util
import shutil
import unittest
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

import main
from src.pathology.filter_cancer import filter_cancer_embeddings
from src.postprocessing.full_wsi_heatmap import parse_coords
from src.preprocessing.extract_patches import get_wsi_files
from src.fusion.run_fusion import aggregate_pathology_to_patient


def load_mri_module():
    path = main.ROOT / "MRI_CORE_FEATURE_EXTRACTION/extract_features.py"
    spec = importlib.util.spec_from_file_location("mri_extract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Path(__file__).resolve().parent / "_runtime" / self._testMethodName
        shutil.rmtree(self.sandbox, ignore_errors=True)
        self.sandbox.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.sandbox, ignore_errors=True)

    def test_mixed_external_data_is_discovered(self):
        root = self.sandbox
        (root / "1003_1.tif").touch()
        case = root / "1003"
        case.mkdir()
        (case / "1003_t2w.mha").touch()
        self.assertTrue(main.contains_wsi(root))
        self.assertTrue(main.contains_mri_cases(root))

    def test_duplicate_slide_stems_are_rejected(self):
        root = self.sandbox
        (root / "same.tif").touch()
        (root / "same.svs").touch()
        with self.assertRaisesRegex(ValueError, "unique stems"):
            get_wsi_files(root)

    def test_sample_mha_names_are_supported(self):
        module = load_mri_module()
        names = ["1003_t2w.mha", "1003_adc.mha", "1003_hbv.mha", "1003_mask.mha"]
        self.assertTrue(all(name.lower().endswith(module.VOLUME_SUFFIXES) for name in names))

    def test_cancer_filter_uses_positive_probability(self):
        root = self.sandbox
        wsi_dir = root / "wsi"
        wsi_dir.mkdir()
        (wsi_dir / "1003_1.tif").touch()
        names = np.asarray(
            ["1003_1_0_0_None.png", "1003_1_224_0_None.png"], dtype=object
        )
        h5_path = root / "embeddings.h5"
        with h5py.File(h5_path, "w") as handle:
            handle["embeddings"] = np.zeros((2, 3), dtype=np.float32)
            handle.create_dataset(
                "filenames", data=names, dtype=h5py.string_dtype("utf-8")
            )
        csv_path = root / "predictions.csv"
        pd.DataFrame(
            {
                "filename": names,
                "prediction": [0, 1],
                "cancer_probability": [0.9, 0.1],
            }
        ).to_csv(csv_path, index=False)
        output = root / "cancer.h5"
        filter_cancer_embeddings(h5_path, csv_path, wsi_dir, output)
        with h5py.File(output) as handle:
            self.assertEqual(handle["embeddings"].shape, (1, 3))
            self.assertEqual(handle["patient_ids"][0].decode(), "1003_1")

    def test_heatmap_coordinate_parser_preserves_slide_id(self):
        self.assertEqual(
            parse_coords("1003_1_800_15328_None.png"), ("1003_1", 800, 15328)
        )

    def test_wsi_case_id_maps_to_mri_patient(self):
        vector = np.ones(3, dtype=np.float32)
        result = aggregate_pathology_to_patient({"1003_1": vector}, {"1003"})
        self.assertEqual(set(result), {"1003"})


if __name__ == "__main__":
    unittest.main()
