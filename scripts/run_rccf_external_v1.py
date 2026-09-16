"""Independent native-label RCCF benchmarks for NSL-KDD and UNSW-NB15."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from src.rccf_forest import RCCFForest
from src.rccf_metrics import classification_metrics, selective_metrics

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def load_nsl(root):
    tr=pd.read_csv(root/"train.csv",low_memory=False); te=pd.read_csv(root/"test.csv",low_memory=False)
    return tr.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(float),tr.target.to_numpy(),te.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(float),te.target.to_numpy(),{"source":"NSL-KDD KDDTrain+/KDDTest+ processed native-label files","provider_url":"https://github.com/defcom17/NSL_KDD","access_date":"2026-09-12","version":"public KDDTrain+/KDDTest+ mirror snapshot","license":"not stated by mirror; no SPDX identifier asserted","split":"public KDDTrain+/KDDTest+ boundary","native_labels":sorted(map(str, np.unique(np.concatenate([tr.target.to_numpy(), te.target.to_numpy()])))),"files":[str(root/"train.csv"),str(root/"test.csv")]}

def load_unsw(root):
    tr=pd.read_csv(root/"UNSW-NB15_training-set.csv",low_memory=False); te=pd.read_csv(root/"UNSW-NB15_testing-set.csv",low_memory=False)
    label="attack_cat" if "attack_cat" in tr.columns else "label"; drop={"id","label","attack_cat"}; names=[c for c in tr.columns if c not in drop and c in te.columns]
    cats=[c for c in names if is_object_dtype(tr[c]) or is_string_dtype(tr[c])]
    a=pd.get_dummies(tr[names],columns=cats,dummy_na=True); b=pd.get_dummies(te[names],columns=cats,dummy_na=True).reindex(columns=a.columns,fill_value=0)
    ytr=tr[label].fillna("Normal").astype(str).str.strip().to_numpy(); yte=te[label].fillna("Normal").astype(str).str.strip().to_numpy()
    return a.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float),ytr,b.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float),yte,{"source":"official UNSW-NB15 training/testing CSV","provider_url":"https://research.unsw.edu.au/projects/unsw-nb15-dataset","access_date":"2026-09-12","version":"official UNSW-NB15 training/testing CSV snapshot","license":"provider terms apply; no SPDX identifier asserted","split":"official UNSW-NB15 training/testing boundary","native_labels":sorted(map(str, np.unique(np.concatenate([ytr, yte])))),"files":[str(root/"UNSW-NB15_training-set.csv"),str(root/"UNSW-NB15_testing-set.csv")]}

def run(dataset, loader, root, out, seeds, n_estimators, cv, alpha, k):
    Xtr,ytr,Xte,yte,source=loader(root); all_rows=[]; out.mkdir(parents=True,exist_ok=True)
    for seed in seeds:
        tr_idx,cal_idx=train_test_split(np.arange(len(ytr)),test_size=.15,stratify=ytr,random_state=seed)
        m=RCCFForest(n_estimators=n_estimators,feature_k=k,cv=cv,random_state=seed,alpha=alpha,n_jobs=-1)
        s=time.perf_counter(); m.fit(Xtr[tr_idx],ytr[tr_idx],Xtr[cal_idx],ytr[cal_idx]); train_s=time.perf_counter()-s
        s=time.perf_counter(); p=m.predict_proba(Xte); pred=m.classes_[p.argmax(1)]; labels,rejected=m.predict_selective(Xte); pred_s=time.perf_counter()-s
        met={**classification_metrics(yte,p,m.classes_),**selective_metrics(yte,p,m.classes_),"dataset":dataset,"model":"rccf","seed":seed,"train_seconds":train_s,"predict_seconds":pred_s,"test_samples":len(yte),"coverage":float(1-rejected.mean()),"rejected_count":int(rejected.sum())}
        all_rows.append(met)
        payload={"row_id":np.arange(len(yte)),"true_label":yte,"predicted_label":pred,"selective_label":labels,"rejected":rejected,"max_probability":p.max(1)}
        payload.update({f"prob_{c}":p[:,i] for i,c in enumerate(m.classes_)})
        pd.DataFrame(payload).to_csv(out/f"predictions_seed{seed}.csv",index=False,encoding="utf-8-sig")
        pd.DataFrame([met]).to_csv(out/f"metrics_seed{seed}.csv",index=False,encoding="utf-8-sig")
        pd.DataFrame({"class":m.classes_,"true_count":pd.Series(yte).value_counts().reindex(m.classes_,fill_value=0).to_numpy(),"predicted_count":pd.Series(pred).value_counts().reindex(m.classes_,fill_value=0).to_numpy()}).to_csv(out/f"class_counts_seed{seed}.csv",index=False,encoding="utf-8-sig")
        report=pd.DataFrame(classification_report(yte,pred,labels=m.classes_,output_dict=True,zero_division=0)).T
        report.to_csv(out/f"classification_report_seed{seed}.csv",encoding="utf-8-sig")
        pd.DataFrame(confusion_matrix(yte,pred,labels=m.classes_),index=m.classes_,columns=m.classes_).to_csv(out/f"confusion_matrix_seed{seed}.csv",encoding="utf-8-sig")
        (out/f"calibration_parameters_seed{seed}.json").write_text(json.dumps({"temperature":m.temperature_,"alpha":alpha,"calibration_rows":len(cal_idx),"classes":m.classes_.tolist()},ensure_ascii=False,indent=2),encoding="utf-8")
    frame=pd.DataFrame(all_rows); means={"dataset":dataset,"model":"rccf"}
    for c in frame.columns:
        if c in {"dataset","model","seed"}: continue
        means[f"{c}_mean"]=float(frame[c].mean()); means[f"{c}_std"]=float(frame[c].std(ddof=1))
    frame.to_csv(out/"metrics_by_seed.csv",index=False,encoding="utf-8-sig"); pd.DataFrame([means]).to_csv(out/"metrics_aggregate.csv",index=False,encoding="utf-8-sig")
    protocol={"dataset":dataset,"independent_native_label_benchmark":True,"cross_dataset_transfer":False,"seeds":list(map(int,seeds)),"n_estimators":n_estimators,"feature_k":k,"cv":cv,"alpha":alpha,"calibration_source":"15% stratified calibration split drawn from official training side only","training_rows":int(len(ytr)),"test_rows":int(len(yte)),"calibration_rows_per_seed":int(round(len(ytr)*.15)),"native_labels":sorted(map(str,np.unique(np.concatenate([ytr,yte])))),"training_label_counts":{str(k):int(v) for k,v in pd.Series(ytr).value_counts().sort_index().items()},"test_label_counts":{str(k):int(v) for k,v in pd.Series(yte).value_counts().sort_index().items()},"test_labels_used_for_fitting":False,"source":source,"file_sha256":{Path(f).name:sha256(Path(f)) for f in source["files"]}}
    (out/"run_manifest.json").write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding="utf-8"); print(frame[["dataset","seed","macro_f1","balanced_accuracy","aurc","log_loss","coverage"]].to_string(index=False))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dataset",choices=["nsl","unsw"],required=True); ap.add_argument("--data-dir",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--seeds",type=int,nargs="+",default=[42,2024,3407]); ap.add_argument("--n-estimators",type=int,default=100); ap.add_argument("--feature-k",type=int,default=60); ap.add_argument("--cv",type=int,default=5); ap.add_argument("--alpha",type=float,default=.1); a=ap.parse_args()
    run(a.dataset,load_nsl if a.dataset=="nsl" else load_unsw,a.data_dir,a.output_dir,a.seeds,a.n_estimators,a.cv,a.alpha,a.feature_k)
if __name__=="__main__": main()
