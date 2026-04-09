This is the code Repo for project "MuTriM: an end-to-end deep learning model integrating features of DCE-MRI and histomorphology for progression-free survival prediction in breast cancer"

Model checkpoint provided, for end to end fusion of DCE-MRI features with histopathology features from WSI for outcome prediction.

Steps:

1. For PyRadiomic feature extraction, First, install the PyRadiomics package and ensure the MRI images and corresponding tumor masks are stored in .nrrd format under the specified directory. Adjust the "data_path" variable to the folder containing the patient subdirectories with image and mask files. Finally the extracted features will be saved into the output file Tumor_feature.txt.
2. For pathology feature extraction, follow the steps in HIPT repo: https://github.com/mahmoodlab/HIPT
3. Make sure the clinical info sheet containing time to event is located in same directory as the feature files.
4. Load the checkpoint and run main_breast_km_curve_final.py
