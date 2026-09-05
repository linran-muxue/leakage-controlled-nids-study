"""Generate additional evidence for the publication version.

This script keeps the locked CIC protocol for the main result and adds:
same-configuration RF feature ablation, explicit equal-weight comparison,
repeated stratified splits, feature-selection stability, class-level reports,
and confusion matrices.
"""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import MinMaxScaler
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment_components import WeightedRandomForest, compute_metrics

DATA = ROOT / "data_processed_audit_v4"
OUT = ROOT / "results_quality_upgrades"

def chi2_idx(X, y, k):
    s, _ = chi2(X, y); s = np.nan_to_num(s, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    return np.sort(np.argsort(-s, kind="stable")[:k])

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [pd.read_csv(DATA / f"{s}.csv", low_memory=False) for s in ["train", "validation", "test"]]
    frame = pd.concat(frames, ignore_index=True)
    names = [c for c in frame.columns if c != "target"]
    Xraw = frame[names].apply(pd.to_numeric, errors="raise").to_numpy(float); y = frame.target.to_numpy()
    labels = sorted(np.unique(y)); all_rows=[]; ablation=[]; stability=[]
    for split_seed in [42, 2024, 3407]:
        tr_idx, rest_idx = train_test_split(np.arange(len(y)), test_size=0.30, stratify=y, random_state=split_seed)
        va_idx, te_idx = train_test_split(rest_idx, test_size=0.50, stratify=y[rest_idx], random_state=split_seed)
        sc=MinMaxScaler(); Xtr=sc.fit_transform(Xraw[tr_idx]); Xv=sc.transform(Xraw[va_idx]); Xte=sc.transform(Xraw[te_idx]); ytr,yv,yte=y[tr_idx],y[va_idx],y[te_idx]
        idx=chi2_idx(Xtr,ytr,60)
        models={
            "rf_all": (RandomForestClassifier(n_estimators=100,min_samples_leaf=2,class_weight="balanced_subsample",n_jobs=-1,random_state=split_seed), np.arange(Xtr.shape[1])),
            "rf_chi2": (RandomForestClassifier(n_estimators=100,min_samples_leaf=2,class_weight="balanced_subsample",n_jobs=-1,random_state=split_seed), idx),
        }
        for name,(model,cols) in models.items():
            t=time.perf_counter(); model.fit(Xtr[:,cols],ytr); train_s=time.perf_counter()-t; t=time.perf_counter(); pred=model.predict(Xte[:,cols]); pred_s=time.perf_counter()-t
            all_rows.append({"split_seed":split_seed,"model":name,**compute_metrics(yte,pred),"train_seconds":train_s,"predict_seconds":pred_s,"feature_count":len(cols),"test_samples":len(yte)})
            pd.DataFrame({"y_true":yte,"y_pred":pred}).to_csv(OUT/f"predictions_{name}_split{split_seed}.csv",index=False,encoding="utf-8-sig")
            pd.DataFrame(classification_report(yte,pred,labels=labels,output_dict=True,zero_division=0)).T.to_csv(OUT/f"classification_report_{name}_split{split_seed}.csv",encoding="utf-8-sig")
            pd.DataFrame(confusion_matrix(yte,pred,labels=labels),index=labels,columns=labels).to_csv(OUT/f"confusion_matrix_{name}_split{split_seed}.csv",encoding="utf-8-sig")
        w=WeightedRandomForest(n_estimators=100,min_samples_leaf=2,random_state=split_seed,weight_metric="balanced_accuracy"); t=time.perf_counter(); w.fit(Xtr[:,idx],ytr,Xv[:,idx],yv); train_s=time.perf_counter()-t; t=time.perf_counter(); wp=w.predict(Xte[:,idx]); pred_s=time.perf_counter()-t
        all_rows.append({"split_seed":split_seed,"model":"weighted_rf_chi2",**compute_metrics(yte,wp),"train_seconds":train_s,"predict_seconds":pred_s,"feature_count":len(idx),"test_samples":len(yte)})
        pd.DataFrame({"y_true":yte,"y_pred":wp}).to_csv(OUT/f"predictions_weighted_rf_chi2_split{split_seed}.csv",index=False,encoding="utf-8-sig")
        pd.DataFrame(classification_report(yte,wp,labels=labels,output_dict=True,zero_division=0)).T.to_csv(OUT/f"classification_report_weighted_rf_chi2_split{split_seed}.csv",encoding="utf-8-sig")
        pd.DataFrame(confusion_matrix(yte,wp,labels=labels),index=labels,columns=labels).to_csv(OUT/f"confusion_matrix_weighted_rf_chi2_split{split_seed}.csv",encoding="utf-8-sig")
        # Explicit equal-weight baseline: standard RF probability averaging.
        equal_pred=models["rf_chi2"][0].predict(Xte[:,idx]); ablation.append({"split_seed":split_seed,"weight_strategy":"equal_weight",**compute_metrics(yte,equal_pred)})
        ablation.append({"split_seed":split_seed,"weight_strategy":"validation_balanced_accuracy",**compute_metrics(yte,wp)})
        # Feature stability across five training-only folds.
        fold_sets={10:[],20:[],60:[]}; skf=StratifiedKFold(n_splits=5,shuffle=True,random_state=split_seed)
        for fi,(fit,_) in enumerate(skf.split(Xtr,ytr)):
            for k in fold_sets: fold_sets[k].append(set(chi2_idx(Xtr[fit],ytr[fit],k).tolist()))
        for k,sets in fold_sets.items():
            vals=[]
            for i in range(len(sets)):
                for j in range(i+1,len(sets)):
                    vals.append(len(sets[i]&sets[j])/len(sets[i]|sets[j]))
            stability.append({"split_seed":split_seed,"k":k,"pair_count":len(vals),"jaccard_mean":float(np.mean(vals)),"jaccard_std":float(np.std(vals,ddof=1))})
    result=pd.DataFrame(all_rows); result.to_csv(OUT/"repeated_split_metrics.csv",index=False,encoding="utf-8-sig")
    result.groupby("model")[['accuracy','macro_precision','macro_recall','macro_f1','train_seconds','predict_seconds']].agg(['mean','std']).reset_index().to_csv(OUT/"repeated_split_summary.csv",index=False,encoding="utf-8-sig")
    abl=pd.DataFrame(ablation); abl.to_csv(OUT/"equal_weight_ablation.csv",index=False,encoding="utf-8-sig"); abl.groupby("weight_strategy")[['accuracy','macro_precision','macro_recall','macro_f1']].agg(['mean','std']).reset_index().to_csv(OUT/"equal_weight_ablation_summary.csv",index=False,encoding="utf-8-sig")
    st=pd.DataFrame(stability); st.to_csv(OUT/"feature_stability.csv",index=False,encoding="utf-8-sig"); st.groupby('k')[['jaccard_mean']].agg(['mean','std']).reset_index().to_csv(OUT/"feature_stability_summary.csv",index=False,encoding="utf-8-sig")
    (OUT/"protocol.json").write_text(json.dumps({"data":"data_processed_audit_v4","split_seeds":[42,2024,3407],"split":"70/15/15 stratified on the 3365-row deduplicated balanced frame","models":{"rf_all":{"features":78,"trees":100,"min_samples_leaf":2},"rf_chi2":{"features":60,"trees":100,"min_samples_leaf":2},"weighted_rf_chi2":{"features":60,"trees":100,"min_samples_leaf":2}},"feature_stability":"5-fold training-only chi2 top-k Jaccard"},ensure_ascii=False,indent=2),encoding="utf-8")
    print(result.to_string(index=False)); print(st.groupby('k').jaccard_mean.mean())
if __name__=='__main__': main()
