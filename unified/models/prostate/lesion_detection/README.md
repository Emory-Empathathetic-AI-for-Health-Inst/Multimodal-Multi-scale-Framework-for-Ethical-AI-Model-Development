nnUNet Prostate Cancer Lesion Detection

This repository contains the codebase and processing pipeline for prostate cancer lesion detection using an nnU-Net–based framework.

The models were developed at Indiana University, Indianapolis (Shiradkar Lab) and trained on publicly available datasets.

📌 Overview
🧾 Task: Prostate cancer lesion detection
⚙️ Framework: nnU-Net (customized pipeline)
🗂️ Datasets Used:
PI-CAI
Prostate-158

This repository includes all necessary steps to:

📥 Prepare data
🔄 Convert to nnU-Net format
🧠 Train the model
✅ Validate dataset integrity

📂 Key Files
nnunet_dataformat_conversion.py
→ Converts raw data into nnU-Net compatible format
gland_crop_bbox.py
→ Performs gland-based cropping for focused training
label_binarization.py
→ Converts labels into required format
dataset_integrity_check_Preprocessing.py
→ Ensures dataset consistency before training
customized_trainer.py
→ Custom nnU-Net trainer implementation
nnunet_dataset.py
→ Dataset handling and loading logic
Steps_to_run_inference
→ Instructions to run inference using the trained model


📦 Model Weights

Model weights are not publicly hosted.

📩 To request access, please contact the authors.

📊 Notes
⚠️ The pipeline is intended for research purposes only
🔁 Ensure consistent preprocessing across datasets
🎯 Cropping and label handling are critical for optimal performance


🙏 Acknowledgements
nnU-Net framework
PI-CAI Challenge
Prostate-158 Dataset
