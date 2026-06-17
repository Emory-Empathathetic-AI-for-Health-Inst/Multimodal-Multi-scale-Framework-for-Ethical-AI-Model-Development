"""Fit the final 0.83 fusion on ALL patients and export its exact linear parameters
to bcr_fusion_model.json (portable; scored with numpy only via predict_bcr.py)."""
import warnings, json; warnings.filterwarnings("ignore")
import numpy as np, bcr_benchmark as B
from ml_numpy import Preprocessor, LogisticGD, LinearSVM

y=B.y_all; PPFG=["ppfgeo__ppf_thick_lr_gap_mean_mm","ppfgeo__ppf_thick_lr_gap_p90_mm"]
common=[i for i in B.rad_tz.index.intersection(B.cf.index).intersection(B.geo_all.index).intersection(y.index) if y.loc[i] in (0,1)]
yv=y.loc[common].astype(int).values

def export(Xdf, ctor, k, squash):
    cols=np.array(Xdf.columns)
    pre=Preprocessor(k=min(k,Xdf.shape[1])).fit(Xdf.values, yv)
    Z=pre.transform(Xdf.values); m=ctor().fit(Z, yv)
    origidx=np.where(pre.nzv_)[0][pre.sel_]
    feats=[]
    for j,oi in enumerate(origidx):
        feats.append(dict(name=str(cols[oi]), median=float(pre.med_[oi]),
                          mean=float(pre.mean_[oi]), std=float(pre.std_[oi]),
                          weight=float(m.w[j])))
    return dict(bias=float(m.b), squash=squash, features=feats)

model={
 "name":"BCR late-fusion (TZ-radiomics + Clinical + PPF L-R gap)",
 "cv_auc":0.83, "n_train":len(yv), "n_pos":int(yv.sum()), "threshold":0.5,
 "fusion":"mean of block probabilities",
 "blocks":{
   "TZ":  export(B.rad_tz.loc[common],          lambda: LogisticGD(l2=0.05,n_iter=800), 12, "sigmoid"),
   "CL":  export(B.cf.loc[common],              lambda: LinearSVM(C=1.0,n_iter=800),    12, "sigmoid"),
   "PPF": export(B.geo_all.loc[common,PPFG],     lambda: LogisticGD(l2=0.05,n_iter=800),  2, "sigmoid"),
 }}
with open("/sessions/compassionate-bold-planck/mnt/outputs/bcr_fusion_model.json","w") as f:
    json.dump(model,f,indent=1)
print("saved bcr_fusion_model.json")
print("blocks/feature counts:", {k:len(v['features']) for k,v in model['blocks'].items()})
print("TZ selected:", [f['name'].replace('rad_tz__','') for f in model['blocks']['TZ']['features'][:3]],"...")
print("CL selected:", [f['name'] for f in model['blocks']['CL']['features']])
print("PPF selected:", [f['name'].replace('ppfgeo__','') for f in model['blocks']['PPF']['features']])
