"""Run a leakage-controlled SCI baseline comparison on the v4 CIC subset."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import f1_score

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sci_baselines import evaluate_predictions, select_train_features


def load_split(path: Path):
    frames = {s: pd.read_csv(path / f"{s}.csv", low_memory=False) for s in ("train", "validation", "test")}
    names = [c for c in frames["train"].columns if c != "target"]
    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(frames["train"][names].apply(pd.to_numeric, errors="raise"))
    x_valid = scaler.transform(frames["validation"][names].apply(pd.to_numeric, errors="raise"))
    x_test = scaler.transform(frames["test"][names].apply(pd.to_numeric, errors="raise"))
    return x_train, frames["train"].target.to_numpy(), x_valid, frames["validation"].target.to_numpy(), x_test, frames["test"].target.to_numpy(), names


def model_specs(seed: int, n_classes: int):
    from xgboost import XGBClassifier
    return {
        "random_forest_all": [
            (RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "all"),
            (RandomForestClassifier(n_estimators=200, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "all"),
        ],
        "random_forest_chi2": [
            (RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "chi2"),
            (RandomForestClassifier(n_estimators=200, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "chi2"),
        ],
        "extra_trees_chi2": [
            (ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=seed), "chi2"),
            (ExtraTreesClassifier(n_estimators=200, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=seed), "chi2"),
        ],
        "xgboost_chi2": [
            (XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, subsample=.9, colsample_bytree=.9, objective="multi:softprob", num_class=n_classes, eval_metric="mlogloss", tree_method="hist", n_jobs=-1, random_state=seed), "chi2"),
            (XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, subsample=.9, colsample_bytree=.9, objective="multi:softprob", num_class=n_classes, eval_metric="mlogloss", tree_method="hist", n_jobs=-1, random_state=seed), "chi2"),
        ],
    }


def fit_eval(model, mode, x_train, y_train, x_valid, y_valid, x_test, y_test, idx, encoder):
    cols = np.arange(x_train.shape[1]) if mode == "all" else idx
    ytr = encoder.transform(y_train); yv = encoder.transform(y_valid); yte = encoder.transform(y_test)
    model.fit(x_train[:, cols], ytr)
    valid_pred = encoder.inverse_transform(model.predict(x_valid[:, cols]).astype(int))
    score = f1_score(y_valid, valid_pred, average="macro", zero_division=0)
    model.fit(x_train[:, cols], ytr)
    pred_num = model.predict(x_test[:, cols]).astype(int)
    proba = model.predict_proba(x_test[:, cols])
    pred = encoder.inverse_transform(pred_num)
    return score, pred, proba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--chi2-k", type=int, default=60)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--seeds", type=int, nargs="+", default=None)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    seeds = args.seeds or ([args.seed] if args.seed is not None else [42, 2024, 3407])
    seed_outputs = []
    for seed in seeds:
        seed_dir = args.output_dir / f"seed{seed}" if len(seeds) > 1 else args.output_dir
        seed_dir.mkdir(parents=True, exist_ok=True)
        seed_args = argparse.Namespace(**vars(args)); seed_args.seed = seed; seed_args.output_dir = seed_dir
        seed_outputs.append(run_one_seed(seed_args))
    all_metrics = pd.concat(seed_outputs, ignore_index=True)
    all_metrics.to_csv(args.output_dir / "metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    all_metrics.groupby("model")[["accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro", "ece"]].agg(["mean", "std"]).reset_index().to_csv(args.output_dir / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")
    print(all_metrics.to_string(index=False))


def run_one_seed(args):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    xtr, ytr, xv, yv, xte, yte, names = load_split(args.processed_dir)
    encoder = LabelEncoder().fit(np.concatenate([ytr, yv, yte]))
    idx = select_train_features(xtr, ytr, min(args.chi2_k, xtr.shape[1]))
    selected = [names[i] for i in idx]
    (args.output_dir / "protocol.json").write_text(json.dumps({"data":"data_processed_audit_v4", "chi2_k":int(args.chi2_k), "seed":args.seed, "selection_fit":"training_only", "tuning_split":"validation_only", "test_usage":"final_evaluation_only", "selected_features":selected}, ensure_ascii=False, indent=2), encoding="utf-8")
    rows=[]; pred_dir=args.output_dir / "predictions"; pred_dir.mkdir(exist_ok=True)
    for name, candidates in model_specs(args.seed, len(encoder.classes_)).items():
        best = None
        for config_id, (model, mode) in enumerate(candidates):
            start=time.perf_counter(); score, _, _ = fit_eval(model, mode, xtr, ytr, xv, yv, xte, yte, idx, encoder); elapsed=time.perf_counter()-start
            if best is None or score > best[0]: best=(score, config_id, model, mode, elapsed)
        _, config_id, model, mode, _ = best
        start=time.perf_counter(); score, pred, proba = fit_eval(model, mode, xtr, ytr, xv, yv, xte, yte, idx, encoder); train_predict_seconds=time.perf_counter()-start
        metrics=evaluate_predictions(yte, pred, proba, encoder.classes_)
        rows.append({"model":name,"seed":args.seed,"feature_mode":mode,"feature_count":int(xtr.shape[1] if mode=="all" else len(idx)),"selected_config":int(config_id),"validation_macro_f1":float(score),"elapsed_seconds":train_predict_seconds,**metrics,"test_samples":len(yte)})
        out=pd.DataFrame({"y_true":yte,"y_pred":pred})
        for j,label in enumerate(encoder.classes_): out[f"proba_{label}"]=proba[:,j]
        out.to_csv(pred_dir / f"predictions_{name}_seed{args.seed}.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(rows).to_csv(args.output_dir / "metrics.csv", index=False, encoding="utf-8-sig")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()
