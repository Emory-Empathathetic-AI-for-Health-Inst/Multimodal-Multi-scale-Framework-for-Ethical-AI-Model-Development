import pandas as pd
import torch
from transformers import AutoTokenizer
import json
import warnings
warnings.filterwarnings("ignore")
import os
from model import BioLinkBERTClass
from free_gpu_selection import get_device
from utils import *
from custom_dataset import CustomDataset

## select the device
device = get_device()
model_dir = "./model_weights/"

## read config.json file
with open("param_config.json", 'r') as f1:
    config = json.load(f1)

## create an instance of the BioLinkBERT class that is defined in model.py
model = BioLinkBERTClass(model_dir=model_dir, dropout=config['dropout'], num_classes=config['num_classes'])
model.load_state_dict(torch.load(os.path.join(model_dir,"pytorch_model.bin")), strict=False)
model = model.to(device)

## load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_dir)

## read input csv file
df_recur = read_input(config["input_file_path"])
print("Number of rows to proccess: ", len(df_recur))

## read abbreaviations dictionary
with open("abbreviations_dict.json", 'r') as f2:
    mydict = json.load(f2)

for old, new in mydict.items():
    df_recur['text'] = df_recur['text'].str.replace(old, new, regex=False)

## create test dataset
test_dataset = CustomDataset(df_recur, tokenizer, config["MAX_LEN"])

## create test dataloader
test_data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=config["TEST_BATCH_SIZE"], shuffle=False, num_workers=config["num_workers"])

## get model predictions
preds = get_predictions(model, test_data_loader, device)
print(preds)

df_recur['Sites of Recurrence'] = ''

label_dict = config["label_dict"]  ## reading labels dictionary from config

for i in range(len(preds)):
    labs = assign_labels(preds[i, :], label_dict)
    df_recur.loc[i, "Sites of Recurrence"] = labs
    if i%100==0:
        df_recur.to_csv(os.path.join(config['output_folder'],'recurrent-sites.csv'), index=False)

df_recur.to_csv(os.path.join(config['output_folder'],'recurrent-sites.csv'), index=False)
