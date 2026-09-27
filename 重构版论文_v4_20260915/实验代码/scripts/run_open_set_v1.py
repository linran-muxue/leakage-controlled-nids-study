"""Known-five-class classification with held-out unknown CIC attack families."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_pipeline import map_attack_label
from src.open_set import open_set_scores, reject_by_threshold


KNOWN = {"Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot"}
UNKNOWN_RAW = {"PortScan", "Infiltration", "Heartbleed"}


def collect_raw(raw_dir, per_group=2000, seed=42):
    known=[]; unknown=[]; rng=np.random.default_rng(seed)
    for path in sorted(Path(raw_dir).rglob("*.csv")):
        for chunk in pd.read_csv(path, chunksize=100000, low_memory=False, encoding_errors="replace"):
            chunk.columns=[str(c).strip() for c in chunk.columns]
            label_col=next(c for c in chunk.columns if c.lower()=="label")
            mapped=chunk[label_col].map(lambda x: map_attack_label(x, include_other=False))
            raw=chunk[label_col].astype(str).str.strip()
            names=[c for c in chunk.columns if c not in {label_col,"Flow ID","Timestamp"}]
            values=chunk[names].apply(pd.to_numeric, errors="coerce").replace([np.inf,-np.inf],np.nan)
            good=values.notna().all(axis=1)
            frame=values.loc[good].copy(); frame["target"]=mapped.loc[good].to_numpy(); frame["raw_label"]=raw.loc[good].to_numpy(); frame["source_file"]=path.name
            known.append(frame[frame.target.isin(KNOWN)]); unknown.append(frame[frame.raw_label.isin(UNKNOWN_RAW)])
    k=pd.concat(known,ignore_index=True); u=pd.concat(unknown,ignore_index=True)
    k=pd.concat([g.sample(min(len(g), per_group), random_state=seed) for _, g in k.groupby("target")], ignore_index=True)
    u=pd.concat([g.sample(min(len(g), per_group), random_state=seed) for _, g in u.groupby("raw_label")], ignore_index=True)
    return k,u


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--raw-dir",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--per-group",type=int,default=2000); ap.add_argument("--seed",type=int,default=42); args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    known, unknown=collect_raw(args.raw_dir,args.per_group,args.seed)
    features=[c for c in known.columns if c not in {"target","raw_label","source_file"}]
    k_train, k_valid = train_test_split(known, test_size=.2, stratify=known.target, random_state=args.seed)
    k_train=k_train.reset_index(drop=True); k_valid=k_valid.reset_index(drop=True)
    k_train[features]=k_train[features].astype(float); k_valid[features]=k_valid[features].astype(float); unknown[features]=unknown[features].astype(float)
    scaler=MinMaxScaler(); X=scaler.fit_transform(k_train[features]); Xv=scaler.transform(k_valid[features]); Xu=scaler.transform(unknown[features]);
    scores,_=chi2(X,k_train.target); idx=np.sort(np.argsort(-np.nan_to_num(scores,nan=0.0))[:60]); clf=RandomForestClassifier(n_estimators=100,min_samples_leaf=2,class_weight="balanced_subsample",n_jobs=-1,random_state=args.seed); clf.fit(X[:,idx],k_train.target)
    labels=clf.classes_; valid_conf=clf.predict_proba(Xv[:,idx]).max(axis=1); threshold=float(np.quantile(valid_conf,.05)); p_known=clf.predict_proba(Xv[:,idx]); p_unknown=clf.predict_proba(Xu[:,idx]); pred_known=reject_by_threshold(p_known,labels,threshold); pred_unknown=reject_by_threshold(p_unknown,labels,threshold)
    y_eval=np.concatenate([k_valid.target.to_numpy(), np.array(["unknown"]*len(unknown))]); p_eval=np.vstack([p_known,p_unknown]); pred_eval=np.concatenate([pred_known,pred_unknown]); metrics=open_set_scores(y_eval,p_eval,labels,threshold); metrics["known_macro_f1"]=float(f1_score(k_valid.target,pred_known,average="macro",zero_division=0));
    out=unknown[["raw_label","source_file"]].copy(); out["max_known_probability"]=p_unknown.max(axis=1); out["predicted_label"]=pred_unknown; out.to_csv(args.output_dir/"unknown_predictions.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame([{"known_train_samples":len(k_train),"known_validation_samples":len(k_valid),"unknown_samples":len(unknown),"threshold":threshold,**metrics}]).to_csv(args.output_dir/"open_set_metrics.csv",index=False,encoding="utf-8-sig")
    (args.output_dir/"protocol.json").write_text(json.dumps({"known_labels":sorted(KNOWN),"unknown_raw_labels":sorted(UNKNOWN_RAW),"unknown_used_for_training":False,"threshold_fit":"5th percentile of known validation confidence","per_group_cap":args.per_group},ensure_ascii=False,indent=2),encoding="utf-8")
    print(pd.DataFrame([metrics]).to_string(index=False))

if __name__=="__main__": main()
