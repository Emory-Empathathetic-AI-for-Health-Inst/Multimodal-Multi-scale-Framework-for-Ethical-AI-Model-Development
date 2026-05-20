import pickle
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

pkl_file = "/storage/home/hcoda1/1/kozyoruk3/scratch/SMuRF_MultiModal_OPSCC_4_8/checkpoints_4slice2/chimere_bcr_4slice/fused_attention_grade_100_0.0001_raptomic_s4/independent_test_preds.pkl"
#"/storage/home/hcoda1/1/kozyoruk3/scratch/SMuRF_MultiModal_OPSCC_4_8/checkpoints_4slice/chimere_bcr_4slice/fused_attention_grade_100_0.0002_raptomic_s4/test_preds.pkl"

with open(pkl_file, "rb") as f:
    test_preds = pickle.load(f)

y_prob = test_preds[0].numpy()
y_true = test_preds[2].numpy()
ids = test_preds[5]

y_pred = (y_prob > 0.58).astype(int)

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

auc = roc_auc_score(y_true, y_prob)
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

print("TP:", tp)
print("TN:", tn)
print("FP:", fp)
print("FN:", fn)
print("AUC:", auc)
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)
print("Specificity:", specificity)