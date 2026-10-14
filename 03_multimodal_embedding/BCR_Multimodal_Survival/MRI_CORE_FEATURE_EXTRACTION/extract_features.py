"""Extract prostate MRI features.



Supports NIfTI (.nii/.nii.gz), MetaImage (.mha/.mhd), and DICOM input.

"""



from __future__ import annotations



import argparse

import csv

import sys

import tempfile

import warnings

from pathlib import Path

from types import SimpleNamespace



import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import numpy as np

import SimpleITK as sitk

import torch

import torch.nn.functional as F

from scipy import ndimage

from tqdm import tqdm



from monai.inferers import sliding_window_inference

from monai.networks.nets import UNet

from monai.transforms import (

    Compose,

    EnsureChannelFirstd,

    EnsureTyped,

    LoadImaged,

    NormalizeIntensityd,

    Orientationd,

    ScaleIntensityd,

    Spacingd,

)



HERE = Path(__file__).resolve().parent

MRI_CORE_DIR = HERE / "mri_foundation"

sys.path.insert(0, str(MRI_CORE_DIR))



from models.sam import sam_model_registry





VOLUME_SUFFIXES = (".nii", ".nii.gz", ".mha", ".mhd")

GLAND_SPACING = (0.5, 0.5, 0.5)

GLAND_ROI_SIZE = (96, 96, 96)

GLAND_SW_BATCH_SIZE = 4

GLAND_OVERLAP = 0.5



warnings.filterwarnings("ignore")





def parse_args(argv=None):

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--data-dir", required=True, type=Path)

    parser.add_argument("--output-dir", required=True, type=Path)

    parser.add_argument(

        "--checkpoint",

        type=Path,

        default=HERE / "weights" / "mri_foundation.pth",

    )

    parser.add_argument(

        "--gland-checkpoint",

        type=Path,

        default=HERE / "Gland_model" / "Finetuneglandmodel.pt",

    )

    parser.add_argument(

        "--sam-checkpoint",

        type=Path,

        default=HERE / "weights" / "sam_vit_b_01ec64.pth",

    )

    parser.add_argument("--image-size", type=int, default=256)

    parser.add_argument("--gland-threshold", type=float, default=0.50)

    parser.add_argument("--bbox-margin-mm", type=float, default=3.0)

    parser.add_argument("--overwrite", action="store_true")

    return parser.parse_args(argv)





def is_volume(path: Path) -> bool:

    name = path.name.lower()

    return path.is_file() and any(name.endswith(ext) for ext in VOLUME_SUFFIXES)





def classify_volume_name(name: str):

    name = name.lower()



    derived_tokens = ("mask", "seg", "label", "box", "tumor", "lesion", "cspca")

    if any(token in name for token in derived_tokens):

        return None



    if (

        "adc_registered" in name

        or "adc_reg" in name

        or ("adc" in name and "registered" in name)

        or ("adc" in name and "regis" in name)

    ):

        return "adc_reg"



    if "adc" in name:

        return "adc"



    if (

        "hbv" in name

        or "highb" in name

        or "high_b" in name

        or "b1400" in name

        or "b1500" in name

        or "b2000" in name

    ):

        return "hbv"



    if (

        "t2w" in name

        or "_t2" in name

        or name.startswith("t2")

        or "t2_" in name

    ):

        return "t2"



    return None





def source_score(path: Path, modality: str) -> tuple:

    name = path.name.lower()

    score = 0



    if modality == "t2":

        score += 10 if "t2w" in name else 0

        score += 4 if any(x in name for x in ("ax", "axial", "tra", "trans")) else 0

        score -= 6 if any(x in name for x in ("sag", "cor", "localizer", "scout")) else 0



    elif modality == "adc_reg":

        score += 12 if "registered" in name or "adc_reg" in name else 0



    elif modality == "hbv":

        score += 8 if "hbv" in name else 0

        score += 4 if any(x in name for x in ("b1400", "b1500", "b2000")) else 0



    return (score, path.name.lower())





def discover_existing_volumes(case_dir: Path):

    discovered = {"t2": [], "adc_reg": [], "adc": [], "hbv": []}



    for path in case_dir.rglob("*"):

        if path.name.startswith("._") or not is_volume(path):

            continue



        modality = classify_volume_name(path.name)

        if modality:

            discovered[modality].append(path)



    return discovered





def dicom_series_in_directory(directory: Path):

    try:

        series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(str(directory))

    except Exception:

        return []



    if not series_ids:

        return []



    results = []

    for series_id in series_ids:

        try:

            files = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(

                str(directory), series_id

            )

            if not files:

                continue



            reader = sitk.ImageFileReader()

            reader.SetFileName(files[0])

            reader.LoadPrivateTagsOn()

            reader.ReadImageInformation()



            description = (

                reader.GetMetaData("0008|103e")

                if reader.HasMetaDataKey("0008|103e")

                else ""

            )

            protocol = (

                reader.GetMetaData("0018|1030")

                if reader.HasMetaDataKey("0018|1030")

                else ""

            )



            text = f"{description} {protocol}".strip()

            modality = classify_volume_name(text)



            results.append(

                {

                    "series_id": series_id,

                    "files": files,

                    "description": description,

                    "protocol": protocol,

                    "modality": modality,

                    "directory": directory,

                }

            )

        except Exception:

            continue



    return results





def discover_dicom_series(case_dir: Path):

    all_series = []

    directories = [case_dir]

    directories.extend(p for p in case_dir.rglob("*") if p.is_dir())



    for directory in directories:

        all_series.extend(dicom_series_in_directory(directory))



    return all_series





def dicom_score(series, modality: str):

    text = f"{series['description']} {series['protocol']}".lower()

    score = len(series["files"])



    if modality == "t2":

        score += 1000 if "t2" in text else 0

        score += 500 if any(x in text for x in ("ax", "axial", "tra", "trans")) else 0

        score -= 800 if any(x in text for x in ("sag", "cor", "localizer", "scout")) else 0



    elif modality == "adc_reg":

        score += 1000 if "registered" in text or "reg" in text else 0



    elif modality == "adc":

        score += 1000 if "adc" in text else 0



    elif modality == "hbv":

        score += 1000 if "hbv" in text else 0

        score += 500 if any(x in text for x in ("b1400", "b1500", "b2000")) else 0



    return score





def has_volume_recursive(directory: Path) -> bool:

    return any(is_volume(path) for path in directory.rglob("*"))





def has_dicom_recursive(directory: Path) -> bool:

    if dicom_series_in_directory(directory):

        return True

    for subdir in directory.rglob("*"):

        if subdir.is_dir() and dicom_series_in_directory(subdir):

            return True

    return False





def discover_cases(data_dir: Path):

    direct_volumes = any(is_volume(path) for path in data_dir.iterdir() if path.is_file())

    direct_dicom = bool(dicom_series_in_directory(data_dir))



    if direct_volumes or direct_dicom:

        return [data_dir]



    case_dirs = []

    for child in sorted(data_dir.iterdir()):

        if not child.is_dir() or child.name.startswith("."):

            continue

        if has_volume_recursive(child) or has_dicom_recursive(child):

            case_dirs.append(child)



    return case_dirs





def write_nifti(image, path: Path):

    path.parent.mkdir(parents=True, exist_ok=True)

    sitk.WriteImage(image, str(path))

    return path





def convert_volume_to_nifti(source: Path, destination: Path):

    image = sitk.ReadImage(str(source))

    if image.GetDimension() != 3:

        raise ValueError(f"Expected 3D image, got {image.GetDimension()}D: {source}")

    return write_nifti(image, destination)





def dicom_to_nifti(series, destination: Path):

    reader = sitk.ImageSeriesReader()

    reader.SetFileNames(series["files"])

    image = reader.Execute()



    if image.GetDimension() != 3:

        raise ValueError(f"DICOM series is not 3D: {series['description']}")



    return write_nifti(image, destination)





def choose_best_existing(discovered):

    selected = {}



    if discovered["t2"]:

        selected["t2"] = max(

            discovered["t2"], key=lambda p: source_score(p, "t2")

        )



    if discovered["adc_reg"]:

        selected["adc_reg"] = max(

            discovered["adc_reg"], key=lambda p: source_score(p, "adc_reg")

        )

    elif discovered["adc"]:

        selected["adc"] = max(

            discovered["adc"], key=lambda p: source_score(p, "adc")

        )



    if discovered["hbv"]:

        selected["hbv"] = max(

            discovered["hbv"], key=lambda p: source_score(p, "hbv")

        )



    return selected





def standardize_case(case_dir: Path, output_dir: Path):

    output_dir.mkdir(parents=True, exist_ok=True)



    existing = discover_existing_volumes(case_dir)

    chosen = choose_best_existing(existing)

    standardized = {}



    output_names = {

        "t2": "t2w.nii.gz",

        "adc_reg": "adc_registered.nii.gz",

        "adc": "adc.nii.gz",

        "hbv": "hbv.nii.gz",

    }



    for modality, source in chosen.items():

        destination = output_dir / output_names[modality]

        convert_volume_to_nifti(source, destination)

        standardized[modality] = destination

        print(f"  {modality:8s} <- {source}")



    needed = {"t2", "hbv"}

    if "adc_reg" not in standardized and "adc" not in standardized:

        needed.add("adc")



    missing = [key for key in needed if key not in standardized]



    if missing:

        dicom_series = discover_dicom_series(case_dir)



        def best_dicom(modality):

            candidates = [s for s in dicom_series if s["modality"] == modality]

            if not candidates:

                return None

            return max(candidates, key=lambda s: dicom_score(s, modality))



        if "t2" not in standardized:

            series = best_dicom("t2")

            if series:

                destination = output_dir / output_names["t2"]

                dicom_to_nifti(series, destination)

                standardized["t2"] = destination

                print(f"  {'t2':8s} <- DICOM {series['description']}")



        if "adc_reg" not in standardized and "adc" not in standardized:

            series = best_dicom("adc_reg")

            modality = "adc_reg"

            if series is None:

                series = best_dicom("adc")

                modality = "adc"

            if series:

                destination = output_dir / output_names[modality]

                dicom_to_nifti(series, destination)

                standardized[modality] = destination

                print(f"  {modality:8s} <- DICOM {series['description']}")



        if "hbv" not in standardized:

            series = best_dicom("hbv")

            if series:

                destination = output_dir / output_names["hbv"]

                dicom_to_nifti(series, destination)

                standardized["hbv"] = destination

                print(f"  {'hbv':8s} <- DICOM {series['description']}")



    if "t2" not in standardized:

        raise RuntimeError("Could not identify a T2-weighted MRI.")



    return standardized





def resample_spacing(image, new_spacing, interpolator=sitk.sitkBSpline):

    original_spacing = image.GetSpacing()

    original_size = image.GetSize()



    new_size = [

        int(round(original_size[i] * original_spacing[i] / new_spacing[i]))

        for i in range(3)

    ]



    resampler = sitk.ResampleImageFilter()

    resampler.SetInterpolator(interpolator)

    resampler.SetOutputSpacing(new_spacing)

    resampler.SetSize(new_size)

    resampler.SetOutputDirection(image.GetDirection())

    resampler.SetOutputOrigin(image.GetOrigin())

    resampler.SetDefaultPixelValue(0)



    return resampler.Execute(image)





def pad_image(image, minimum_size=GLAND_ROI_SIZE):

    size = image.GetSize()

    lower = [max((minimum_size[i] - size[i]) // 2, 0) for i in range(3)]

    upper = [

        max(minimum_size[i] - size[i] - lower[i], 0)

        for i in range(3)

    ]

    return sitk.ConstantPad(image, lower, upper, constant=0)





def prepare_t2_for_gland(t2_path: Path, output_path: Path):

    image = sitk.ReadImage(str(t2_path))

    image = sitk.DICOMOrient(image, "RAS")

    image = resample_spacing(image, GLAND_SPACING, sitk.sitkBSpline)

    image = pad_image(image, GLAND_ROI_SIZE)

    return write_nifti(image, output_path)





def build_gland_model(checkpoint: Path, device):

    if not checkpoint.is_file():

        raise FileNotFoundError(f"Gland checkpoint not found: {checkpoint}")



    model = UNet(

        spatial_dims=3,

        in_channels=1,

        out_channels=3,

        channels=(16, 32, 64, 128, 256, 512),

        strides=(2, 2, 2, 2, 2),

        num_res_units=4,

        norm="BATCH",

        act="PRELU",

        dropout=0.15,

    ).to(device)



    state = torch.load(checkpoint, map_location=device)

    if isinstance(state, dict) and "state_dict" in state:

        state = state["state_dict"]



    state = {

        (key[7:] if key.startswith("module.") else key): value

        for key, value in state.items()

    }



    model.load_state_dict(state, strict=True)

    return model.eval()





GLAND_TRANSFORM = Compose(

    [

        LoadImaged(keys=["image"], reader="NibabelReader"),

        EnsureChannelFirstd(keys=["image"]),

        Orientationd(keys=["image"], axcodes="RAS"),

        Spacingd(keys=["image"], pixdim=GLAND_SPACING, mode=("bilinear",)),

        ScaleIntensityd(keys="image", minv=0, maxv=1),

        NormalizeIntensityd(keys="image"),

        EnsureTyped(keys=["image"]),

    ]

)





def predict_gland_probability(preprocessed_t2_path: Path, model, device):

    sample = GLAND_TRANSFORM({"image": str(preprocessed_t2_path)})

    image = sample["image"]



    if image.ndim == 4:

        image = image.unsqueeze(0)



    image = image.to(device=device, dtype=torch.float32)



    with torch.inference_mode():

        logits = sliding_window_inference(

            image,

            roi_size=GLAND_ROI_SIZE,

            sw_batch_size=GLAND_SW_BATCH_SIZE,

            predictor=model,

            overlap=GLAND_OVERLAP,

        )

        probability = torch.sigmoid(logits[:, 1:2])



    return probability[0, 0].detach().cpu().numpy().astype(np.float32)





def save_array_using_reference(array_xyz, reference_path: Path, output_path: Path):

    reference = sitk.ReadImage(str(reference_path))

    reference_size = reference.GetSize()



    if tuple(array_xyz.shape) == tuple(reference_size):

        array_zyx = np.transpose(array_xyz, (2, 1, 0))

    elif tuple(array_xyz.shape) == tuple(reversed(reference_size)):

        array_zyx = array_xyz

    else:

        raise RuntimeError(

            f"Prediction shape {array_xyz.shape} does not match reference "

            f"size {reference_size}."

        )



    image = sitk.GetImageFromArray(array_zyx)

    image.CopyInformation(reference)

    return write_nifti(image, output_path)





def largest_connected_component(mask):

    labels, count = ndimage.label(mask)



    if count == 0:

        return np.zeros_like(mask, dtype=bool)



    sizes = ndimage.sum(mask, labels, range(1, count + 1))

    label = int(np.argmax(sizes)) + 1

    return labels == label





def clean_gland_probability(probability, threshold):

    mask = probability >= threshold



    if not mask.any():

        raise RuntimeError(

            f"Gland prediction is empty at threshold {threshold:.3f}."

        )



    mask = largest_connected_component(mask)

    mask = ndimage.binary_fill_holes(mask)



    structure = ndimage.generate_binary_structure(3, 1)

    mask = ndimage.binary_closing(mask, structure=structure, iterations=2)



    mask = ndimage.binary_fill_holes(mask)

    mask = largest_connected_component(mask)



    if not mask.any():

        raise RuntimeError("Gland prediction became empty after post-processing.")



    return mask.astype(np.uint8)





def resample_mask_to_reference(mask_path: Path, reference_path: Path, output_path: Path):

    mask = sitk.ReadImage(str(mask_path))

    reference = sitk.ReadImage(str(reference_path))



    resampler = sitk.ResampleImageFilter()

    resampler.SetReferenceImage(reference)

    resampler.SetInterpolator(sitk.sitkNearestNeighbor)

    resampler.SetTransform(sitk.Transform())

    resampler.SetDefaultPixelValue(0)



    mapped = resampler.Execute(mask)

    mapped = sitk.Cast(mapped > 0, sitk.sitkUInt8)



    return write_nifti(mapped, output_path)





def clean_mask_image(mask_path: Path, output_path: Path):

    image = sitk.ReadImage(str(mask_path))

    array = sitk.GetArrayFromImage(image) > 0



    array = largest_connected_component(array)

    array = ndimage.binary_fill_holes(array).astype(np.uint8)



    if not array.any():

        raise RuntimeError("Mapped gland mask is empty.")



    cleaned = sitk.GetImageFromArray(array)

    cleaned.CopyInformation(image)



    return write_nifti(cleaned, output_path)





def make_bbox_mask(gland_mask_path: Path, output_path: Path, margin_mm: float):

    image = sitk.ReadImage(str(gland_mask_path))

    mask = sitk.GetArrayFromImage(image) > 0

    coords = np.argwhere(mask)



    if coords.size == 0:

        raise RuntimeError("Cannot create gland bounding box from empty mask.")



    minimum = coords.min(axis=0)

    maximum = coords.max(axis=0)



    spacing_xyz = np.asarray(image.GetSpacing(), dtype=float)

    spacing_zyx = spacing_xyz[[2, 1, 0]]

    margin_voxels = np.ceil(margin_mm / spacing_zyx).astype(int)



    minimum = np.maximum(minimum - margin_voxels, 0)

    maximum = np.minimum(maximum + margin_voxels, np.asarray(mask.shape) - 1)



    z0, y0, x0 = minimum

    z1, y1, x1 = maximum



    box = np.zeros_like(mask, dtype=np.uint8)

    box[z0:z1 + 1, y0:y1 + 1, x0:x1 + 1] = 1



    box_image = sitk.GetImageFromArray(box)

    box_image.CopyInformation(image)

    write_nifti(box_image, output_path)



    return {

        "path": output_path,

        "xyz_bounds": {

            "x": [int(x0), int(x1)],

            "y": [int(y0), int(y1)],

            "z": [int(z0), int(z1)],

        },

    }





def norm01(array):

    low, high = np.percentile(array, [1, 99])

    if high <= low:

        return np.zeros_like(array, dtype=np.float32)

    return np.clip((array - low) / (high - low), 0, 1)





def pick_mask_slices(mask, count=12):

    indices = np.where(mask.sum(axis=(1, 2)) > 0)[0]



    if len(indices) <= count:

        return indices



    positions = np.linspace(0, len(indices) - 1, count, dtype=int)

    return indices[positions]





def save_qc(t2_path: Path, gland_path: Path, box_path: Path, output_dir: Path, case_id: str):

    output_dir.mkdir(parents=True, exist_ok=True)



    t2 = sitk.GetArrayFromImage(sitk.ReadImage(str(t2_path)))

    gland = sitk.GetArrayFromImage(sitk.ReadImage(str(gland_path))) > 0

    box = sitk.GetArrayFromImage(sitk.ReadImage(str(box_path))) > 0



    slice_ids = pick_mask_slices(gland, 12)



    if len(slice_ids) == 0:

        raise RuntimeError("Cannot create QC image because gland mask is empty.")



    montage_path = output_dir / f"{case_id}_gland_qc.png"



    cols = 4

    rows = int(np.ceil(len(slice_ids) / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), dpi=160)

    axes = np.atleast_1d(axes).ravel()



    for ax in axes[len(slice_ids):]:

        ax.axis("off")



    for index, z in enumerate(slice_ids):

        ax = axes[index]

        ax.imshow(norm01(t2[z]), cmap="gray", origin="lower")

        ax.contour(

            gland[z].astype(float),

            levels=[0.5],

            colors="red",

            linewidths=1.8,

            origin="lower",

        )

        if box[z].any():

            ax.contour(

                box[z].astype(float),

                levels=[0.5],

                colors="yellow",

                linewidths=1.2,

                origin="lower",

            )

        ax.set_title(f"{case_id} | z={z}", fontsize=9)

        ax.axis("off")



    plt.tight_layout()

    fig.savefig(montage_path, bbox_inches="tight")

    plt.close(fig)



    return montage_path





def process_gland_case(

    case_dir: Path,

    case_output: Path,

    gland_model,

    device,

    threshold: float,

    margin_mm: float,

):

    standard_dir = case_output / "standardized"

    work_dir = case_output / "gland_work"

    qc_dir = case_output / "qc"



    standard_dir.mkdir(parents=True, exist_ok=True)

    work_dir.mkdir(parents=True, exist_ok=True)

    qc_dir.mkdir(parents=True, exist_ok=True)



    standardized = standardize_case(case_dir, standard_dir)



    preprocessed = work_dir / "t2_gland_preprocessed.nii.gz"

    probability_path = work_dir / "gland_probability.nii.gz"

    cleaned_preprocessed = work_dir / "gland_clean_preprocessed.nii.gz"

    mapped_path = work_dir / "gland_mapped_to_t2.nii.gz"



    final_gland = standard_dir / "generated_gland_mask.nii.gz"

    final_box = standard_dir / "generated_gland_box.nii.gz"



    prepare_t2_for_gland(standardized["t2"], preprocessed)



    probability = predict_gland_probability(preprocessed, gland_model, device)

    save_array_using_reference(probability, preprocessed, probability_path)



    clean = clean_gland_probability(probability, threshold)

    save_array_using_reference(clean, preprocessed, cleaned_preprocessed)



    resample_mask_to_reference(cleaned_preprocessed, standardized["t2"], mapped_path)

    clean_mask_image(mapped_path, final_gland)



    box_info = make_bbox_mask(final_gland, final_box, margin_mm)

    qc_path = save_qc(

        standardized["t2"],

        final_gland,

        final_box,

        qc_dir,

        case_dir.name,

    )



    return {

        "case_id": case_dir.name,

        "case_dir": case_dir,

        "case_output": case_output,

        "standardized": standardized,

        "gland_path": final_gland,

        "box_path": final_box,

        "box_bounds": box_info["xyz_bounds"],

        "qc_path": qc_path,

    }





def model_args():

    return SimpleNamespace(

        arch="vit_b",

        if_encoder_adapter=True,

        encoder_adapter_depths=[0, 1, 10, 11],

        if_mask_decoder_adapter=True,

        decoder_adapt_depth=2,

    )





def build_mri_model(checkpoint: Path, sam_checkpoint: Path, image_size: int, device):

    if not checkpoint.is_file():

        raise FileNotFoundError(f"MRI foundation checkpoint not found: {checkpoint}")

    if not sam_checkpoint.is_file():

        raise FileNotFoundError(f"SAM checkpoint not found: {sam_checkpoint}")



    original_torch_load = torch.load



    def redirected_torch_load(file, *args, **kwargs):

        try:

            requested = Path(str(file))

        except Exception:

            requested = None



        if (

            requested is not None

            and requested.name == "sam_vit_b_01ec64.pth"

            and not requested.is_file()

        ):

            file = str(sam_checkpoint)



        return original_torch_load(file, *args, **kwargs)



    torch.load = redirected_torch_load

    try:

        model = sam_model_registry["vit_b"](

            model_args(),

            checkpoint=str(checkpoint),

            num_classes=1,

            image_size=image_size,

            pretrained_sam=True,

        )

    finally:

        torch.load = original_torch_load



    return model.to(device).eval()





def same_geometry(a: sitk.Image, b: sitk.Image, tol=1e-5):

    return (

        a.GetSize() == b.GetSize()

        and np.allclose(a.GetSpacing(), b.GetSpacing(), atol=tol)

        and np.allclose(a.GetOrigin(), b.GetOrigin(), atol=tol)

        and np.allclose(a.GetDirection(), b.GetDirection(), atol=tol)

    )





def resample_to_reference(image, reference, is_mask=False):

    if same_geometry(image, reference):

        return image



    resampler = sitk.ResampleImageFilter()

    resampler.SetReferenceImage(reference)

    resampler.SetTransform(sitk.Transform())

    resampler.SetInterpolator(

        sitk.sitkNearestNeighbor if is_mask else sitk.sitkBSpline

    )

    resampler.SetDefaultPixelValue(0)

    return resampler.Execute(image)





def sitk_to_yxz(image, normalize=False):

    array = sitk.GetArrayFromImage(image).astype(np.float32)

    if array.ndim != 3:

        raise ValueError(f"Expected 3D volume, got {array.shape}")



    volume = np.transpose(array, (1, 2, 0))



    if normalize:

        for z in range(volume.shape[2]):

            section = volume[..., z]

            low = float(section.min())

            high = float(section.max())

            volume[..., z] = (

                (section - low) / (high - low)

                if high > low

                else 0

            )



    return volume





def choose_feature_modalities(standardized):

    selected = [("t2", standardized["t2"])]



    if "adc_reg" in standardized:

        selected.append(("adc_reg", standardized["adc_reg"]))

    elif "adc" in standardized:

        selected.append(("adc", standardized["adc"]))



    if "hbv" in standardized:

        selected.append(("hbv", standardized["hbv"]))



    if len(selected) == 1:

        selected *= 3

    elif len(selected) == 2:

        selected.append(selected[0])



    return selected[:3]





def crop_bounds(mask):

    coordinates = np.argwhere(mask > 0)



    if coordinates.size == 0:

        raise ValueError("Generated gland bounding box is empty.")



    minimum = coordinates.min(axis=0)

    maximum = coordinates.max(axis=0)



    return tuple(

        (int(minimum[i]), int(maximum[i]))

        for i in range(3)

    )





def extract_mri_features(record, model, image_size, device):

    standardized = record["standardized"]

    selected = choose_feature_modalities(standardized)



    t2_image = sitk.ReadImage(str(standardized["t2"]))



    volumes = []

    modality_names = []



    for name, path in selected:

        image = sitk.ReadImage(str(path))

        image = resample_to_reference(image, t2_image, is_mask=False)

        volumes.append(sitk_to_yxz(image, normalize=True))

        modality_names.append(name)



    box_image = sitk.ReadImage(str(record["box_path"]))

    box_image = resample_to_reference(box_image, t2_image, is_mask=True)

    box = sitk_to_yxz(box_image, normalize=False)



    (y0, y1), (x0, x1), (z0, z1) = crop_bounds(box)



    features = []



    with torch.inference_mode():

        for z in range(z0, z1 + 1):

            slices = [

                volume[y0:y1 + 1, x0:x1 + 1, z]

                for volume in volumes

            ]



            if any(section.size == 0 for section in slices):

                continue



            image = torch.as_tensor(

                np.stack(slices),

                dtype=torch.float32,

            )[None].to(device)



            image = F.interpolate(

                image,

                size=(image_size, image_size),

                mode="bilinear",

                align_corners=False,

            )



            encoded = model.image_encoder(image).mean(dim=(2, 3))

            features.append(encoded.cpu().numpy())



    if not features:

        raise RuntimeError("No valid MRI slices were available inside the gland ROI.")



    features = np.vstack(features)

    return features, features.mean(axis=0), modality_names





def save_case_features(output_dir: Path, case_id: str, features, mean_feature, modalities):

    output_dir.mkdir(parents=True, exist_ok=True)



    slice_path = output_dir / f"{case_id}_slice_features.npy"

    mean_path = output_dir / f"{case_id}_case_mean_feature.npy"



    np.save(slice_path, features)

    np.save(mean_path, mean_feature)



    return {

        "case": case_id,

        "roi_type": "box",

        "modalities": modalities,

        "num_slices": int(features.shape[0]),

        "feature_dim": int(features.shape[1]),

    }





def write_cohort_summary(output_dir: Path, rows):

    path = output_dir / "feature_extraction_summary.csv"



    fieldnames = [

        "case",

        "roi_type",

        "modalities",

        "num_slices",

        "feature_dim",

    ]



    with path.open("w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:

            writer.writerow({key: row.get(key, "") for key in fieldnames})



    return path





def main(argv=None):

    args = parse_args(argv)



    data_dir = args.data_dir.expanduser().resolve()

    output_dir = args.output_dir.expanduser().resolve()

    mri_checkpoint = args.checkpoint.expanduser().resolve()

    gland_checkpoint = args.gland_checkpoint.expanduser().resolve()

    sam_checkpoint = args.sam_checkpoint.expanduser().resolve()



    if not data_dir.is_dir():

        raise NotADirectoryError(f"MRI data directory does not exist: {data_dir}")



    case_dirs = discover_cases(data_dir)



    if not case_dirs:

        raise FileNotFoundError(

            f"No MRI cases containing supported volumes or DICOM series were found in {data_dir}"

        )



    output_dir.mkdir(parents=True, exist_ok=True)



    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Device: {device}")

    if device.type == "cuda":

        print(f"GPU: {torch.cuda.get_device_name(0)}")



    print(f"Found {len(case_dirs)} case(s).")



    rows = []

    completed = 0

    failed = 0

    skipped = 0

    failed_cases = []



    with tempfile.TemporaryDirectory(prefix=".mri_work_", dir=output_dir) as temp_dir:

        work_root = Path(temp_dir)

        gland_model = build_gland_model(gland_checkpoint, device)

        prepared = []



        for case_dir in tqdm(case_dirs, desc="Gland preprocessing"):

            mean_path = output_dir / f"{case_dir.name}_case_mean_feature.npy"



            if mean_path.exists() and not args.overwrite:

                print(f"[skip] {case_dir.name}: already complete")

                skipped += 1

                continue



            try:

                print(f"\n[{case_dir.name}]")

                case_output = work_root / case_dir.name

                record = process_gland_case(

                    case_dir=case_dir,

                    case_output=case_output,

                    gland_model=gland_model,

                    device=device,

                    threshold=args.gland_threshold,

                    margin_mm=args.bbox_margin_mm,

                )

                prepared.append(record)

            except Exception as exc:

                print(f"[failed gland] {case_dir.name}: {exc}")

                failed += 1

                failed_cases.append((case_dir.name, f"gland: {exc}"))



        del gland_model

        if torch.cuda.is_available():

            torch.cuda.empty_cache()



        if prepared:

            mri_model = build_mri_model(

                mri_checkpoint,

                sam_checkpoint,

                args.image_size,

                device,

            )



            for record in tqdm(prepared, desc="MRI feature extraction"):

                try:

                    features, mean_feature, modalities = extract_mri_features(

                        record,

                        mri_model,

                        args.image_size,

                        device,

                    )



                    summary = save_case_features(

                        output_dir,

                        record["case_id"],

                        features,

                        mean_feature,

                        modalities,

                    )



                    rows.append(

                        {

                            "case": record["case_id"],

                            "roi_type": "box",

                            "modalities": "|".join(modalities),

                            "num_slices": summary["num_slices"],

                            "feature_dim": summary["feature_dim"],

                        }

                    )

                    completed += 1



                    print(

                        f"{record['case_id']}: ROI=box, mods={modalities}, "

                        f"features={features.shape}"

                    )



                except Exception as exc:

                    print(f"[failed features] {record['case_id']}: {exc}")

                    failed += 1

                    failed_cases.append((record["case_id"], f"features: {exc}"))



    summary_path = write_cohort_summary(output_dir, rows)



    print("\nDone.")

    print(f"Complete: {completed}")

    print(f"Skipped:  {skipped}")

    print(f"Failed:   {failed}")

    print(f"Summary:  {summary_path}")



    if failed_cases:

        print("\nFailed cases:")

        for case_id, error in failed_cases:

            print(f"  {case_id}: {error}")





if __name__ == "__main__":

    main()
