"""Model-wise nested CV: every baseline is tuned and evaluated on each outer fold."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import chi2
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nested_evaluation import filter_candidate_specs
from src.sci_baselines import evaluate_predictions


def load_data(path):
    frames = [pd.read_csv(path / f"{s}.csv", low_memory=False) for s in ("train", "validation")]
    names = [c for c in frames[0].columns if c != "target"]
    x = pd.concat([f[names] for f in frames], ignore_index=True).apply(pd.to_numeric, errors="raise").to_numpy(float)
    y = pd.concat([f["target"] for f in frames], ignore_index=True).to_numpy()
    return x, y, names


def select_idx(x, y, k):
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    return np.sort(np.argsort(-scores, kind="stable")[:k])


def transform(x_fit, x_eval, y_fit, mode, k):
    scaler = MinMaxScaler(); a = scaler.fit_transform(x_fit); b = scaler.transform(x_eval)
    idx = select_idx(a, y_fit, k) if mode == "chi2" else np.arange(a.shape[1])
    return a[:, idx], b[:, idx], idx


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--processed-dir", type=Path, required=True); ap.add_argument("--output-dir", type=Path, required=True); ap.add_argument("--outer-splits", type=int, default=3); ap.add_argument("--inner-splits", type=int, default=3); ap.add_argument("--k-values", type=int, nargs="+", default=[20, 40, 60]); ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    x, y, names = load_data(args.processed_dir); enc = LabelEncoder().fit(y); outer = StratifiedKFold(n_splits=args.outer_splits, shuffle=True, random_state=args.seed)
    rows=[]; tune_rows=[]; pred_dir=args.output_dir/"predictions"; pred_dir.mkdir(exist_ok=True)
    for fold, (outer_train, outer_test) in enumerate(outer.split(x, y), 1):
        inner = StratifiedKFold(n_splits=args.inner_splits, shuffle=True, random_state=args.seed+fold)
        for family in ("random_forest", "extra_trees", "xgboost"):
            candidates = filter_candidate_specs(family, seed=args.seed+fold, n_classes=len(enc.classes_), k_values=args.k_values)
            scored=[]
            for cand in candidates:
                fs=[]
                for fit_rel, val_rel in inner.split(outer_train, y[outer_train]):
                    fit_idx, val_idx = outer_train[fit_rel], outer_train[val_rel]
                    a,b,_ = transform(x[fit_idx], x[val_idx], y[fit_idx], cand["mode"], cand["k"])
                    cand["estimator"].fit(a, enc.transform(y[fit_idx])); p=enc.inverse_transform(cand["estimator"].predict(b).astype(int)); fs.append(f1_score(y[val_idx],p,average="macro",zero_division=0))
                scored.append({"config":cand["config"],"model":family,"mode":cand["mode"],"k":cand["k"],"inner_macro_f1":float(np.mean(fs))})
            best=sorted(scored,key=lambda r:(-r["inner_macro_f1"],r["config"]))[0]; tune_rows.extend([{"fold":fold,**r} for r in scored])
            cand={c["config"]:c for c in candidates}[best["config"]]; a,b,idx=transform(x[outer_train],x[outer_test],y[outer_train],cand["mode"],cand["k"]); start=time.perf_counter(); cand["estimator"].fit(a,enc.transform(y[outer_train])); train_s=time.perf_counter()-start; start=time.perf_counter(); pred=enc.inverse_transform(cand["estimator"].predict(b).astype(int)); proba=cand["estimator"].predict_proba(b); pred_s=time.perf_counter()-start; m=evaluate_predictions(y[outer_test],pred,proba,enc.classes_); rows.append({"fold":fold,"model":family,"selected_config":best["config"],"k":best["k"] or x.shape[1],"feature_count":len(idx),"inner_macro_f1":best["inner_macro_f1"],"train_seconds":train_s,"predict_seconds":pred_s,"test_samples":len(outer_test),**m}); out=pd.DataFrame({"row_index":outer_test,"y_true":y[outer_test],"y_pred":pred}); [out.__setitem__(f"proba_{label}",proba[:,j]) for j,label in enumerate(enc.classes_)]; out.to_csv(pred_dir/f"{family}_fold{fold}.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(rows).to_csv(args.output_dir/"outer_modelwise_metrics.csv",index=False,encoding="utf-8-sig"); pd.DataFrame(tune_rows).to_csv(args.output_dir/"inner_modelwise_tuning.csv",index=False,encoding="utf-8-sig"); pd.DataFrame(rows).groupby("model")[["accuracy","balanced_accuracy","macro_f1","log_loss","brier_macro","ece"]].agg(["mean","std"]).reset_index().to_csv(args.output_dir/"outer_modelwise_summary.csv",index=False,encoding="utf-8-sig"); (args.output_dir/"protocol.json").write_text(json.dumps({"development_pool":"data_processed_audit_v4/train.csv + validation.csv","untouched_final_test":"data_processed_audit_v4/test.csv","outer_splits":args.outer_splits,"inner_splits":args.inner_splits,"k_values":args.k_values,"modelwise_tuning":True},ensure_ascii=False,indent=2),encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__": main()
