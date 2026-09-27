"""Run the locked RCCF CIC experiment and write auditable artifacts."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from src.rccf_forest import RCCFForest
from src.rccf_metrics import classification_metrics, selective_metrics

def load(path):
    f=pd.read_csv(path, low_memory=False); return f.drop(columns=["target"]).apply(pd.to_numeric), f["target"].to_numpy()

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def run(seed, Xtr, ytr, Xcal, ycal, Xte, yte, out, n_estimators, cv, alpha):
    model=RCCFForest(n_estimators=n_estimators, cv=cv, random_state=seed, alpha=alpha, n_jobs=-1)
    start=time.perf_counter(); model.fit(Xtr, ytr, Xcal, ycal); train=time.perf_counter()-start
    start=time.perf_counter(); p=model.predict_proba(Xte); pred=model.classes_[p.argmax(1)]; predict=time.perf_counter()-start
    labels,rejected=model.predict_selective(Xte)
    classes=np.asarray(model.classes_)
    metrics={**classification_metrics(yte,p,classes), **selective_metrics(yte,p,classes),
             "model":"rccf","seed":seed,"train_seconds":train,"predict_seconds":predict,
             "test_samples":len(yte),"rejected_count":int(rejected.sum()),"coverage":float(1-rejected.mean())}
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame({"row_id":np.arange(len(yte)),"true_label":yte,"predicted_label":pred,"selective_label":labels,"rejected":rejected,"max_probability":p.max(1),**{f"prob_{c}":p[:,i] for i,c in enumerate(classes)}}).to_csv(out/f"predictions_seed{seed}.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame([metrics]).to_csv(out/f"metrics_seed{seed}.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(classification_report(yte,pred,labels=classes,output_dict=True,zero_division=0)).T.to_csv(out/f"classification_report_seed{seed}.csv",encoding="utf-8-sig")
    pd.DataFrame(confusion_matrix(yte,pred,labels=classes),index=classes,columns=classes).to_csv(out/f"confusion_matrix_seed{seed}.csv",encoding="utf-8-sig")
    (out/f"calibration_parameters_seed{seed}.json").write_text(json.dumps({"temperature":model.temperature_,"alpha":alpha,"classes":classes.tolist(),"calibration_rows":model.calibration_rows_},ensure_ascii=False,indent=2),encoding="utf-8")
    return metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--processed-dir",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--seeds",type=int,nargs="+",default=[42,2024,3407]); ap.add_argument("--n-estimators",type=int,default=100); ap.add_argument("--cv",type=int,default=5); ap.add_argument("--alpha",type=float,default=.1); a=ap.parse_args()
    Xtr,ytr=load(a.processed_dir/"train.csv"); Xcal,ycal=load(a.processed_dir/"validation.csv"); Xte,yte=load(a.processed_dir/"test.csv")
    allm=[]
    for seed in a.seeds: allm.append(run(seed,Xtr.to_numpy(),ytr,Xcal.to_numpy(),ycal,Xte.to_numpy(),yte,a.output_dir,a.n_estimators,a.cv,a.alpha))
    pd.DataFrame(allm).to_csv(a.output_dir/"metrics_by_seed.csv",index=False,encoding="utf-8-sig")
    numeric=[c for c in pd.DataFrame(allm).columns if c not in {"model","seed"}]
    agg=pd.DataFrame([{ "model":"rccf", **{f"{c}_mean":float(pd.DataFrame(allm)[c].mean()) for c in numeric}, **{f"{c}_std":float(pd.DataFrame(allm)[c].std(ddof=1)) for c in numeric}}])
    agg.to_csv(a.output_dir/"metrics_aggregate.csv",index=False,encoding="utf-8-sig")
    labels = sorted(map(str, np.unique(np.concatenate([ytr, ycal, yte]))))
    class_counts = {
        split: {label: int((values == label).sum()) for label in labels}
        for split, values in (("train", ytr), ("validation", ycal), ("test", yte))
    }
    manifest={
        "dataset":"CIC-IDS2017",
        "protocol_name":"deduplicated capped observed-prior population",
        "observed_prior_population_rows": int(len(ytr) + len(ycal) + len(yte)),
        "train_rows": int(len(ytr)), "validation_rows": int(len(ycal)),
        "test_rows": int(len(yte)), "calibration_rows": int(len(ycal)),
        "class_counts": class_counts, "native_labels": labels,
        "feature_count_before_selection": int(Xtr.shape[1]),
        "feature_count_after_selection": int(min(60, Xtr.shape[1])),
        "deduplication_before_split": True,
        "deduplication_audit": str(a.processed_dir / "dedup_audit.json"),
        "split_rule": "fixed stratified 70/15/15 split; seed-specific model fitting",
        "seeds": a.seeds, "n_estimators": a.n_estimators, "cv": a.cv, "alpha": a.alpha,
        "feature_selection_fit_on":"training partition only",
        "risk_fit_on":"training cross-fitted predictions only",
        "calibration_fit_on":"validation partition only",
        "test_labels_used_for_fitting":False, "cross_dataset_transfer":False,
        "processed_hashes":{name:sha256(a.processed_dir/f"{name}.csv") for name in ("train","validation","test")}
    }
    (a.output_dir/"run_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(pd.DataFrame(allm)[["model","seed","macro_f1","aurc","risk_at_90","log_loss","coverage"]].to_string(index=False))
if __name__=="__main__": main()
