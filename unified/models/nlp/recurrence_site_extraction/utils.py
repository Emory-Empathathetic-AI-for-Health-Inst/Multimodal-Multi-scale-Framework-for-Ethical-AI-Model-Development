import pandas as pd
import torch
from tqdm import tqdm

def cleaning(txt):
    '''
    cleaning function to remove LLM specific wrong indexed outputs
    '''
    for ch in ["<break>", '</paragraph>', '<paragraph>', "<title>", "</title>", "<text>", "/>diagnosis</title>", "/>impression / report / plan</title>", "\\\\par", "</section>", "</component>","<section>", "<component>", "\\b0", "\\b", "\\ul", "\\highlight0", "\\f2","\\fs20","\\ql", "\\n", "\\"]:
        txt = txt.replace(ch, "")
    return txt

def filtering(txt):
    if len(txt)==0:
        txt = None
    return txt

def read_input(input_file_path):
    try:
        if input_file_path.endswith(".csv"):
            df_pred = pd.read_csv(input_file_path)
        elif input_file_path.endswith(".xlsx"):
            df_pred = pd.read_excel(input_file_path)
    except:
        raise ValueError("Input file must be in either .csv or .xlsx format")

    if 'Prediction' in df_pred.columns:
        df_recur = df_pred[df_pred['Prediction']=='Recurrence']
    else:
        df_recur = df_pred
    df_recur['text'] = df_recur['text'].apply(cleaning)
    df_recur['text'] = df_recur['text'].apply(filtering)
    df_recur = df_recur.dropna(subset=['text'])
    df_recur.reset_index(drop=True, inplace=True)
    ## dropping unnecessary columns from df_recur
    # df_recur = df_recur.drop(['SENT', 'UN_SENT', 'DOC_TEXT', 'Prediction', 'label'], axis=1)

    return df_recur

def get_predictions(model, data_loader, device):
    model = model.eval()
    predictions = []
    all_preds = []
    with torch.no_grad():
      for data in tqdm(data_loader,  desc="Inference"):
        title = data["title"]
        ids = data["input_ids"].to(device, dtype = torch.long)
        mask = data["attention_mask"].to(device, dtype = torch.long)
        outputs = model(ids, mask)
        outputs = torch.sigmoid(outputs).detach().cpu()
        preds = outputs.round()
        all_preds.append(preds)
    predictions = torch.cat(all_preds, dim=0)
    return predictions

def assign_labels(preds, label_dict):
    labs = ''
    for j in range(1, len(preds)):
        if int(preds[j])==1:
            if labs == '':
                labs = labs + label_dict[str(j)]
            else:
                labs = labs + ', '+ label_dict[str(j)]
    return labs