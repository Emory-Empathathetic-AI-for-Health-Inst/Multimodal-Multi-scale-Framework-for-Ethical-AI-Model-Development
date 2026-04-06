#environment initilaziation
%env nnUNet_raw=/content/drive/MyDrive/combined_cpre/latest/nnUNet_raw
%env nnUNet_preprocessed=/content/drive/MyDrive/combined_cpre/latest/nnUNet_preprocessed
%env nnUNet_results=/content/drive/MyDrive/combined_cpre/latest/nnUNet_results

#plan and preprocessing

!nnUNetv2_plan_and_preprocess -d 001 --verify_dataset_integrity
