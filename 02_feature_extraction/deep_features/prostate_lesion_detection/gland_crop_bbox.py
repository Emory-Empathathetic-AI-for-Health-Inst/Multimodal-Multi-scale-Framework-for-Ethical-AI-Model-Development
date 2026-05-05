import os


os.makedirs("/content/nnUNet/nnunetv2/preprocessing", exist_ok=True)
crop_func_path = "/content/nnUNet/nnunetv2/preprocessing/gland_crop_utils.py"
=
# nnUNet v2–COMPATIBLE CROP FUNCTION
# - gland / box based


crop_func_code = '''
import numpy as np
from acvl_utils.cropping_and_padding.bounding_boxes import (
    get_bbox_from_mask,
    bounding_box_to_slice
)

def box_mask_crop(data, seg, box_channel=2, threshold=0.5):
    """
    nnUNet v2 compatible gland-based hard box cropping.
    Uses BoxMask channel only (NOT tumor).
    Safe for csPCa + ciPCa.
    """

    box_mask = data[box_channel] > threshold


    if np.sum(box_mask) == 0:
        bbox = [[0, s] for s in data.shape[1:]]
        return data, seg, bbox

   
    # Compute bbox from gland box
    
    bbox = get_bbox_from_mask(box_mask)
    slicer = bounding_box_to_slice(bbox)

#Apply crop

    data_cropped = data[(slice(None),) + slicer]
    seg_cropped  = seg[(slice(None),) + slicer]

    return (
        np.ascontiguousarray(data_cropped),
        np.ascontiguousarray(seg_cropped),
        bbox
    )
'''


with open(crop_func_path, "w") as f:
    f.write(crop_func_code)

print("Done")
