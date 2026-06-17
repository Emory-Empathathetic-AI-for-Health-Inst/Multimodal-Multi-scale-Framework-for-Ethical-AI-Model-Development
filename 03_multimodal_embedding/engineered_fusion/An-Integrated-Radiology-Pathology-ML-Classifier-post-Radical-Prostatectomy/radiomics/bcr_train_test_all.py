"""
BCR prediction - BEST model (late fusion, cross-validated AUC ~0.83 on GIFU).

Late fusion of three per-block pipelines (each: median-impute -> variance filter ->
z-score -> ANOVA-F SelectKBest -> linear classifier), averaging predicted probabilities:
    * TZ-radiomics      -> Logistic Regression (L2),  k=12
    * Clinical          -> linear SVM (calibrated),   k=12
    * PPF L-R fat gap   -> Logistic Regression (L2),  k=2

Two evaluations are provided:
  (A) Repeated stratified 5-fold CV  -> the honest estimate (reports ~0.83).
  (B) A single stratified train/test split -> illustrative only; unstable at n=44.

Requires: pip install numpy pandas scikit-learn
Edit DATA_DIR to point at the folder with the three CSVs.
"""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, train_test_split
from sklearn.metrics import (roc_auc_score, average_precision_score, balanced_accuracy_score,
                             recall_score, confusion_matrix)

DATA_DIR = "."   # folder containing the three CSVs below
F_CLIN = os.path.join(DATA_DIR, "clinical_table_with_valid_pzvr_pv.csv")
F_TZ   = os.path.join(DATA_DIR, "pyradiomics_features_tz.csv")
F_PPF  = os.path.join(DATA_DIR, "ppf_features.csv")
LABEL  = "PSA recurrence (>0.2)"

# ----------------------------------------------------------------------------- #
# 1. Load + build the three feature blocks (indexed by patient id), and label
# ----------------------------------------------------------------------------- #
def num(s):
    return pd.to_numeric(s.astype(str).str.replace("<","",regex=False).str.replace("≥","",regex=False).str.strip(),
                         errors="coerce")
STAGE = {"1c":1,"2":2,"2a":2.3,"2b":2.6,"2c":2.9,"3":3,"3a":3.3,"3b":3.6,"4":4,"0":0}
def stg(s):
    s = (s.astype(str).str.strip().str.lower().str.replace("ａ","a").str.replace("ｂ","b").str.replace("ｃ","c"))
    return s.map(STAGE)

clin = pd.read_csv(F_CLIN)
clin = clin[clin["patient_id"].notna()].copy(); clin["pid"] = clin["patient_id"].astype(int)
clin = clin[clin[LABEL].isin([0,1])].copy()
ylab = clin.set_index("pid")[LABEL].astype(int)

cf = pd.DataFrame(index=clin["pid"].values)
cf["age"]=clin["Age (at surgery)"].values; cf["bmi"]=clin["BMI"].values
cf["psa"]=clin["Pre-biopsy PSA (ng/ml)"].values; cf["prostate_vol"]=num(clin["Prostate volume (cc)"]).values
cf["pct_pos_cores"]=num(clin["Percentage of positive cores (%)"]).values
cf["bx_gg"]=clin["Gleason Grade Group"].values; cf["gs_primary"]=clin["GS primary"].values
cf["gs_secondary"]=clin["GS secondary"].values; cf["cT"]=stg(clin["cTstage"]).values
cf["cN"]=clin["cN"].values; cf["nccn_risk"]=clin["Risk group (NCCN classification)"].values
cf["pirads"]=clin["MRI PIRADS"].values; cf["mri_size"]=clin["MRI index lesion maximum tumor size (mm)"].values
cf["hb"]=clin["Hemoglobin (Hb)"].values; cf["crp"]=num(clin["C-reactive protein (CRP)"]).values
neu=clin["Neutrophil count"].astype(float); lym=clin["Lymphocyte count"].astype(float); plt_=clin["Platelet count"].astype(float)
cf["nlr"]=(neu/lym).values; cf["plr"]=(plt_/lym).values
cf["path_pT"]=stg(clin["Pathological T stage (pT)"]).values; cf["path_pN"]=clin["Pathological N stage (pN)"].values
cf["path_gg"]=clin["Grade group"].values; cf["tumor_size"]=clin["Tumor size (mm)"].values
cf["margin"]=clin["Resection margin (RM)"].values; cf["ece"]=num(clin["Extracapsular extension (ECE)"]).values
cf["pni"]=clin["Perineural invasion (pn)"].values; cf["vi"]=clin["Vascular invasion (v)"].values
cf["li"]=clin["Lymphatic invasion (ly)"].values; cf["nerve_sparing"]=clin["Nerve sparing"].values
cf["lnd"]=clin["Lymph node dissection"].values
cf = cf.loc[:, cf.nunique(dropna=True) > 1]

def load_block(path, idcol, cols=None, prefix=""):
    d = pd.read_csv(path); d[idcol] = pd.to_numeric(d[idcol], errors="coerce")
    d = d[d[idcol].notna()].copy(); d["pid"] = d[idcol].astype(int); d = d.drop_duplicates("pid").set_index("pid")
    keep = cols if cols else [c for c in d.columns if d[c].dtype != object and c not in (idcol,"pid")]
    d = d[keep]; d.columns = [prefix+c for c in d.columns]
    return d

tz = load_block(F_TZ, "pid", prefix="tz__")
ppf = load_block(F_PPF, "case_id", cols=["ppf_thick_lr_gap_mean_mm","ppf_thick_lr_gap_p90_mm"], prefix="ppf__")

common = sorted(set(tz.index) & set(cf.index) & set(ppf.index) & set(ylab.index))
y = ylab.loc[common].values
TZ, CF, PPF = tz.loc[common], cf.loc[common], ppf.loc[common]
print(f"n={len(common)}  BCR+={int(y.sum())}  | TZ feats={TZ.shape[1]}  clinical={CF.shape[1]}  ppf-gap={PPF.shape[1]}")

# ----------------------------------------------------------------------------- #
# 2. Per-block pipeline + late-fusion estimator (averages probabilities)
# ----------------------------------------------------------------------------- #
def block_pipe(clf, k):
    return Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("var", VarianceThreshold(0.0)),
                     ("scale", StandardScaler()),
                     ("select", SelectKBest(f_classif, k=k)),
                     ("clf", clf)])

class LateFusion(BaseEstimator, ClassifierMixin):
    """Average predict_proba of several (pipeline, X-block) experts."""
    def __init__(self, experts):           # experts: list of (name, pipeline, Xframe)
        self.experts = experts
    def fit(self, idx, y):
        self.fitted_ = [(n, clone(p).fit(X.loc[idx], y), X) for n,p,X in self.experts]
        self.classes_ = np.array([0,1]); return self
    def predict_proba(self, idx):
        P = np.mean([p.predict_proba(X.loc[idx])[:,1] for _,p,X in self.fitted_], axis=0)
        return np.c_[1-P, P]
    def predict(self, idx): return (self.predict_proba(idx)[:,1] >= 0.5).astype(int)

def make_model():
    return LateFusion([
        ("TZ",  block_pipe(LogisticRegression(penalty="l2", C=1.0, class_weight="balanced", max_iter=5000), 12), TZ),
        ("CL",  block_pipe(SVC(kernel="linear", C=1.0, class_weight="balanced", probability=True, random_state=0), 12), CF),
        ("PPF", block_pipe(LogisticRegression(penalty="l2", C=1.0, class_weight="balanced", max_iter=5000), 2), PPF),
    ])

idx_all = np.array(common)
def metrics(yt, yp, thr=0.5):
    yh = (yp>=thr).astype(int); tn,fp,fn,tp = confusion_matrix(yt,yh,labels=[0,1]).ravel()
    return dict(AUC=roc_auc_score(yt,yp), AUPRC=average_precision_score(yt,yp),
                BalAcc=balanced_accuracy_score(yt,yh),
                Sens=tp/(tp+fn) if tp+fn else np.nan, Spec=tn/(tn+fp) if tn+fp else np.nan)

# ----------------------------------------------------------------------------- #
# 3A. Repeated stratified CV  (the reported ~0.83 estimate)
# ----------------------------------------------------------------------------- #
N_SPLITS, N_REPEATS = 5, 20
aucs=[]; per=[]
for rep in range(N_REPEATS):
    skf = StratifiedKFold(N_SPLITS, shuffle=True, random_state=rep)
    oof = np.full(len(y), np.nan)
    for tr, te in skf.split(idx_all, y):
        mdl = make_model().fit(idx_all[tr], y[tr])
        oof[te] = mdl.predict_proba(idx_all[te])[:,1]
    m = metrics(y, oof); aucs.append(m["AUC"]); per.append(m)
A = np.array(aucs)
print("\n[A] Repeated stratified 5-fold CV (20 repeats):")
print(f"  AUC   = {A.mean():.3f}  (95% interval {np.percentile(A,2.5):.2f}-{np.percentile(A,97.5):.2f})")
for k in ["AUPRC","BalAcc","Sens","Spec"]:
    print(f"  {k:6s}= {np.mean([p[k] for p in per]):.3f}")

# ----------------------------------------------------------------------------- #
# 3B. Single stratified train/test split (illustrative; unstable at this n)
# ----------------------------------------------------------------------------- #
tr_i, te_i = train_test_split(np.arange(len(y)), test_size=0.30, stratify=y, random_state=42)
mdl = make_model().fit(idx_all[tr_i], y[tr_i])
yp = mdl.predict_proba(idx_all[te_i])[:,1]
m = metrics(y[te_i], yp)
print(f"\n[B] Single 70/30 hold-out (n_test={len(te_i)}, illustrative only):")
print("  " + "  ".join(f"{k}={v:.3f}" for k,v in m.items()))

# Fit a final model on ALL data for deployment / SHAP / external testing:
final_model = make_model().fit(idx_all, y)
print("\nFinal model trained on all", len(y), "patients (ready for external validation).")
