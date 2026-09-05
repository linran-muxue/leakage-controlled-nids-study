"""Run an independent native-label UNSW-NB15 benchmark after audit."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors


def file_hash(path: Path, block=1024 * 1024):
    import hashlib
    md5 = hashlib.md5(); sha = hashlib.sha256(); size = 0
    with path.open("rb") as fh:
        while True:
            data = fh.read(block)
            if not data:
                break
            size += len(data); md5.update(data); sha.update(data)
    return {"bytes": size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def probability_metrics(y_true, probabilities, classes):
    y = np.asarray(y_true); p = np.clip(np.asarray(probabilities, dtype=float), 1e-15, 1.0); p = p / p.sum(axis=1, keepdims=True); labels = np.asarray(classes)
    return {"log_loss": float(log_loss(y, p, labels=labels)), "brier_macro": float(np.mean([brier_score_loss((y == label).astype(int), p[:, i]) for i, label in enumerate(labels)])), "ece": float(calibration_errors(y, p, class_labels=labels)["ece"])}


def fit_label_encoder(y_train: np.ndarray, y_test: np.ndarray) -> LabelEncoder:
    """Fit labels on training only and reject unseen test classes explicitly."""
    encoder = LabelEncoder().fit(np.asarray(y_train))
    unseen = sorted(set(np.asarray(y_test).tolist()) - set(encoder.classes_.tolist()))
    if unseen:
        raise ValueError(f"Test labels absent from training labels: {unseen}")
    return encoder


def load_native(path: Path):
    train_path = path / "UNSW-NB15_training-set.csv"; test_path = path / "UNSW-NB15_testing-set.csv"
    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Expected official UNSW-NB15_training-set.csv and UNSW-NB15_testing-set.csv")
    tr=pd.read_csv(train_path, low_memory=False); te=pd.read_csv(test_path, low_memory=False)
    label = "attack_cat" if "attack_cat" in tr.columns else "label"
    # Exclude both target representations.  UNSW-NB15 contains the
    # multiclass ``attack_cat`` target and a binary ``label`` target; keeping
    # the latter when predicting attack_cat would leak the answer into the
    # feature matrix.
    drop={"id", "label", "attack_cat"}; names=[c for c in tr.columns if c not in drop and c in te.columns]
    # One-hot encode categorical protocol/service/state using the training
    # vocabulary; unknown test categories become all-zero columns.
    categorical = [c for c in names if is_object_dtype(tr[c]) or is_string_dtype(tr[c])]
    train_part = pd.get_dummies(tr[names], columns=categorical, dummy_na=True)
    test_part = pd.get_dummies(te[names], columns=categorical, dummy_na=True)
    # Align test columns to the training vocabulary; test-only levels are
    # discarded rather than being allowed to define preprocessing dimensions.
    test_part = test_part.reindex(columns=train_part.columns, fill_value=0)
    xtr=train_part.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    xte=test_part.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy(float)
    return xtr,tr[label].fillna("Normal").astype(str).str.strip().to_numpy(),xte,te[label].fillna("Normal").astype(str).str.strip().to_numpy()


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--raw-dir",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True); ap.add_argument("--k",type=int,default=60); ap.add_argument("--n-estimators",type=int,default=100); ap.add_argument("--min-samples-leaf",type=int,default=2); ap.add_argument("--seed",type=int,default=42); args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    xtr,ytr,xte,yte=load_native(args.raw_dir); enc=fit_label_encoder(ytr, yte); scaler=MinMaxScaler(); a=scaler.fit_transform(xtr); b=scaler.transform(xte); scores,_=chi2(a,enc.transform(ytr)); idx=np.sort(np.argsort(-np.nan_to_num(scores,nan=0.0))[:min(args.k,a.shape[1])]);
    from xgboost import XGBClassifier
    models={"rf_all":(RandomForestClassifier(n_estimators=args.n_estimators,min_samples_leaf=args.min_samples_leaf,class_weight="balanced_subsample",n_jobs=-1,random_state=args.seed),np.arange(a.shape[1])),"rf_chi2":(RandomForestClassifier(n_estimators=args.n_estimators,min_samples_leaf=args.min_samples_leaf,class_weight="balanced_subsample",n_jobs=-1,random_state=args.seed),idx),"extra_trees_chi2":(ExtraTreesClassifier(n_estimators=args.n_estimators,min_samples_leaf=args.min_samples_leaf,class_weight="balanced",n_jobs=-1,random_state=args.seed),idx),"xgboost_chi2":(XGBClassifier(n_estimators=args.n_estimators,max_depth=6,learning_rate=.1,subsample=.9,colsample_bytree=.9,objective="multi:softprob",num_class=len(enc.classes_),eval_metric="mlogloss",tree_method="hist",n_jobs=-1,random_state=args.seed),idx)}; rows=[]
    for name,(m,cols) in models.items():
        fit_y = enc.transform(ytr) if name.startswith("xgboost") else ytr
        s=time.perf_counter(); m.fit(a[:,cols],fit_y); train_s=time.perf_counter()-s; s=time.perf_counter(); p_raw=m.predict(b[:,cols]); proba=m.predict_proba(b[:,cols]); pred_s=time.perf_counter()-s; p=enc.inverse_transform(p_raw.astype(int)) if name.startswith("xgboost") else p_raw; pm=probability_metrics(yte,proba,enc.classes_); rows.append({"model":name,"accuracy":accuracy_score(yte,p),"balanced_accuracy":balanced_accuracy_score(yte,p),"macro_f1":f1_score(yte,p,average="macro",zero_division=0),"train_seconds":train_s,"predict_seconds":pred_s,"feature_count":len(cols),"test_samples":len(yte),**pm}); pd.DataFrame(classification_report(yte,p,output_dict=True,zero_division=0)).T.to_csv(args.output_dir/f"classification_report_{name}.csv",encoding="utf-8-sig"); out=pd.DataFrame({"y_true":yte,"y_pred":p}); [out.__setitem__(f"proba_{label}",proba[:,j]) for j,label in enumerate(enc.classes_)]; out.to_csv(args.output_dir/f"predictions_{name}.csv",index=False,encoding="utf-8-sig"); labels=list(enc.classes_); pd.DataFrame(confusion_matrix(yte,p,labels=labels),index=labels,columns=labels).to_csv(args.output_dir/f"confusion_matrix_{name}.csv",encoding="utf-8-sig"); true_counts=pd.Series(yte).value_counts().reindex(labels,fill_value=0); pred_counts=pd.Series(p).value_counts().reindex(labels,fill_value=0); pd.DataFrame({"label":labels,"true_count":true_counts.to_numpy(),"pred_count":pred_counts.to_numpy()}).to_csv(args.output_dir/f"class_prediction_counts_{name}.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(rows).to_csv(args.output_dir/"metrics.csv",index=False,encoding="utf-8-sig"); protocol={"dataset":"UNSW-NB15","source":"UNSW Canberra Cyber official UNSW-NB15 project page","label_column":"attack_cat or label","split":"official training/testing files","feature_selection":"training-only chi2","cross_dataset_transfer":False,"seed":args.seed,"k":args.k,"n_estimators":args.n_estimators,"min_samples_leaf":args.min_samples_leaf,"files":{p.name:file_hash(p) for p in (args.raw_dir/"UNSW-NB15_training-set.csv",args.raw_dir/"UNSW-NB15_testing-set.csv")}}; (args.output_dir/"protocol.json").write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding="utf-8"); print(pd.DataFrame(rows).to_string(index=False))

if __name__=="__main__": main()
