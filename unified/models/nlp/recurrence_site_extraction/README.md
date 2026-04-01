This GitHub repository extracts the sites of distant recurrence for breast cancer patients from the free-text notes (clinical/radiology/pathology notes) using task specific fine-tuned BioLinkBERT model. This model was fine-tuned with recurrence relevant text from notes curated for every 1 month. 

# Inference
Create conda environment using the following command:
>conda create -f environment.yml

Activate the conda environment using the following command:
>conda activate PE

To make your notes suitable for using this repository, run the BreastRecurrence_Transformer GitHub repository (given below) first on your notes and use `pred_recur` generated output file.

>https://github.com/imonban/BreastRecurrence_Transformer

The above repository curates the text for every 1 month and predicts whether a patient has recurrence during that interval. The main columns of `pred_recur` file are: `PATIENT_ID,START_DATE, END_DATE, text, Prediction`.
The `text` column is used in our repository to extract the sites of distant recurrence. 

Now set two fields in the `config.json` file:

- input_file_path (path of pred_recur file)
- output_folder

Send an email to `mbsikha@gmail.com` requesting the link for downloading the model weights. After downloading the model weights, keep them in the `model_weights` folder.

For inference, run the following command:
>python inference.py
