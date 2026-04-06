import os, json

raw_data_dir = ""

num_train = len(os.listdir(os.path.join(raw_data_dir, "labelsTr")))
num_test  = len(os.listdir(os.path.join(raw_data_dir, "labelsTs")))

dataset = {
    "channel_names": {
        "0": "T2",
        "1": "ADC",
        "2": "BoxMask"
    },
    "labels": {
        "background": 0,
        "tumor": 1
    },
    "numTraining": num_train,
    "numTest": num_test,
    "file_ending": ".nii.gz",
    "modality": {
        "0": "MRI",
        "1": "MRI",
        "2": "MRI"
    },
    "dataset_name": "Prostate158_Rebuttal",
    "description": "Tumor-only supervision with gland-based cropping prior (csPCa + ciPCa).",
    "license": "CC-BY-4.0"
}

with open(os.path.join(raw_data_dir, "dataset.json"), "w") as f:
    json.dump(dataset, f, indent=4)

print(" dataset.json written correctly")
