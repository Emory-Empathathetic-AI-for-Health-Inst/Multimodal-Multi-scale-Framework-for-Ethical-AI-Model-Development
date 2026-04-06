"""
hiti_preproc: A WIP Python package for preprocessing DICOMs and medical images.

This package provides tools for preparing medical images for downstream use. Code
is based on internal workflows used in the HITI Lab at Emory University and currently
focuses on preprocessing mammograms from the Emory Breast Imaging Dataset (EMBED).

Modules:
    - `dicoms`: Functions for preprocessing general DICOMs and mammograms.
    - `rois`: Functions for padding patches generated from EMBED ROIs.

"""

from .dicoms import *
from .rois import *
