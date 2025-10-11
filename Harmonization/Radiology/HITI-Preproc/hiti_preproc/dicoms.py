"""
hiti_preproc.dicoms: Functions for preprocessing general DICOMs and mammograms.
"""

import pydicom
import numpy as np
from typing import Literal, Union, overload
import cv2


def preprocess_pixel_array(dicom: pydicom.FileDataset) -> np.ndarray:
    """Preprocesses a dicom pixel array by applying the VOI LUT
    transformation indicated in the DICOM and normalizing to uint16

    Args:
        dicom (pydicom.FileDataset): DICOM to preprocess

    Returns:
        np.ndarray: Preprocessed DICOM pixel array
    """
    # extract the pixel array and apply the VOI LUT transformation
    image = pydicom.pixels.apply_voi_lut(dicom.pixel_array, dicom, index=0)

    # cast to float32, then normalize and cast to uint16
    image = image.astype(np.float32)
    image = (65535 * ((image - image.min()) / np.ptp(image))).astype(np.uint16)
    return image


def normalize_mammogram_alignment(
    image: np.ndarray, target_side: Literal["L", "R"] = "L"
) -> np.ndarray:
    """Normalizes the alignment of a mammogram to the target side

    Args:
        image (np.ndarray): 2D image to normalize alignment for.
        target_side (str, optional): Image side to align pixels to.
        Defaults to left ("L").

    Returns:
        np.ndarray: Input image with normalized alignment
    """
    # TODO: func assumes image is 2D, generalize for 3D
    # determine which image alignment requires intervention
    intervention_side: Literal["L", "R"] = "R" if target_side == "L" else "L"

    # measure the side of the current image
    image_side: Literal["L", "R", "E"] = check_mammogram_alignment(image)

    if image_side == intervention_side:
        return image[:, ::-1]
    else:
        return image


def check_mammogram_alignment(
    image: np.ndarray, slice_width: int = 20
) -> Literal["L", "R", "E"]:
    """Determines whether a mammogram (either a PNG or DICOM) is
    aligned to the left or right side by comparing the number of background
    pixels on either edge of the image.

    Args:
        image (np.ndarray): 2D Image to check alignment for.
        slice_width (int, optional): Width of the left and right edge slices.
        Defaults to 20 pixels.

    Returns:
        Literal["L", "R", "E"]: A string indicating if the pixels are aligned
        to the left ("L"), right ("R"), or if alignment could not be
        determined ("E").
    """
    # take slices of the image on the left and right sides of the image
    slice_L: np.ndarray = image[:, :slice_width]
    slice_R: np.ndarray = image[:, -slice_width:]

    # get the background threshold by offsetting the minimum value of the image
    # by a small proportion of the pixel range
    bg_threshold: float = np.ptp(image) * 0.0005 + image.min()

    # count number of background pixels on each side
    num_bg_L = (np.array(slice_L) <= bg_threshold).sum()
    num_bg_R = (np.array(slice_R) <= bg_threshold).sum()

    # if there are fewer background pixels on the left than the right
    # laterality is left
    if num_bg_L < num_bg_R:
        return "L"

    # if there are fewer background pixels on the right than the left
    # laterality is right
    elif num_bg_R < num_bg_L:
        return "R"

    # if num background pixels is equal, laterality can't be determined
    else:
        print("Error: Laterality could not be determined!")
        return "E"


def get_mammogram_foreground_mask(
    image: np.ndarray, connectivity: int = 8, min_area_prop: float = 0.05
) -> np.ndarray:
    """Function to get a mask of the foreground pixels in a mammogram to exclude.

    Args:
        image (np.ndarray): 2D Image to build the foreground mask for.
        connectivity (int, optional): Connectivity parameter for
            cv2.connectedComponentsWithStats. Defaults to 8.
        min_area_prop (float, optional): Minimum area needed for pixel islands to
            be included in the output mask. Defaults to 0.05.

    Returns:
        np.ndarray: Binary mask of the image where the foreground pixels are 1
        and the background pixels are 0.
    """
    # TODO: func assumes the image is 2D, generalize for 3D
    # calculate the min. area by getting min_area_prop of the overall image area
    min_area = ((image.shape[0]) * (image.shape[1])) * min_area_prop

    # get a mask of pixels that are between the lower bound and the max pixel value
    _, binary_mask = cv2.threshold(
        image, np.ptp(image) * 0.0005 + image.min(), image.max(), cv2.THRESH_BINARY
    )

    # find connected islands of pixels
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary_mask.astype(np.uint8), connectivity=connectivity
    )

    foreground_mask = np.zeros_like(binary_mask)

    # filter out small pixel islands
    # iterate over connected components (excluding the background -- label 0)
    # if the label area >= the min area, add it to the island mask
    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area >= min_area:
            foreground_mask[labels == label] = 1

    return foreground_mask


# overload 1: default case called with no return_mask argument
@overload
def preprocess_mammo_dicom(dicom: pydicom.FileDataset) -> np.ndarray: ...


# overload 2: If return_mask is explicitly False, the return type is a single array
@overload
def preprocess_mammo_dicom(
    dicom: pydicom.FileDataset, return_mask: Literal[False]
) -> np.ndarray: ...


# overload 3: If return_mask is explicitly True, the return type is a tuple of arrays
@overload
def preprocess_mammo_dicom(
    dicom: pydicom.FileDataset, return_mask: Literal[True]
) -> tuple[np.ndarray, np.ndarray]: ...


def preprocess_mammo_dicom(
    dicom: pydicom.FileDataset, return_mask: bool = False
) -> Union[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    """Preprocesses a mammogram by applying VOI LUT, normalizing to uint16,
    then isolating the foreground of the image.

    Args:
        dicom (pydicom.FileDataset): DICOM to preprocess
        return_mask (bool, optional): Whether to return the foreground mask
        generated by get_mammogram_foreground_mask(). Defaults to False.

    Returns:
        Union[np.ndarray, tuple[np.ndarray, np.ndarray]]: The preprocessed
        pixel array alone, or the preprocessed pixel array and its foreground
        mask if return_mask == True.
    """
    # preprocess the pixel array
    image: np.ndarray = preprocess_pixel_array(dicom)

    # ensure the image is aligned to the left
    image: np.ndarray = normalize_mammogram_alignment(image)

    # get the largest connect island in the image and apply it as a mask
    # to isolate the breast tissue
    foreground_mask: np.ndarray = get_mammogram_foreground_mask(image)
    masked_image: np.ndarray = image * foreground_mask

    if return_mask:
        return masked_image, foreground_mask
    else:
        return masked_image
