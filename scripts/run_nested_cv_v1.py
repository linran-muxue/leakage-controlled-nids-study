"""Run nested cross-validation without preprocessing leakage."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sci_baselines import evaluate_predictions


def load_data(path: Path):
    # Nested CV runs only on the development pool (train + validation).  The
    # original test.csv remains a completely untouched final hold-out set.
    frames = {s: pd.read_csv(path / f"{s}.csv", low_memory=False) for s in ("train", "validation")}
    names = [c for c in frames["train"].columns if c != "target"]
    x = pd.concat([frames[s][names] for s in ("train", "validation")], ignore_index=True).apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    y = pd.concat([frames[s]["target"] for s in ("train", "validation")], ignore_index=True).to_numpy()
    return x, y, names


def select_features(x, y, k):
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    return np.sort(np.argsort(-scores, kind="stable")[: int(k)])


def candidate_grid(seed, n_classes, k_values):
    from xgboost import XGBClassifier
    out = []
    for k in k_values:
        out.extend([
            {"model": "random_forest", "mode": "all", "k": None, "config": f"rf_all_t100", "estimator": RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)},
            {"model": "random_forest", "mode": "chi2", "k": k, "config": f"rf_chi2_k{k}_t100", "estimator": RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)},
            {"model": "extra_trees", "mode": "chi2", "k": k, "config": f"et_chi2_k{k}_t100", "estimator": ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=seed)},
            {"model": "xgboost", "mode": "chi2", "k": k, "config": f"xgb_chi2_k{k}_t100_d6", "estimator": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=.1, subsample=.9, colsample_bytree=.9, objective="multi:softprob", num_class=n_classes, eval_metric="mlogloss", tree_method="hist", n_jobs=-1, random_state=seed)},
        ])
    # The all-feature RF control is independent of k; retain one copy.
    dedup = {c["config"]: c for c in out}
    return list(dedup.values())


def transformed_fold(x_fit, x_valid, y_fit, mode, k):
    scaler = MinMaxScaler()
    fit_scaled = scaler.fit_transform(x_fit)
    valid_scaled = scaler.transform(x_valid)
    if mode == "chi2":
        idx = select_features(fit_scaled, y_fit, k)
    else:
        idx = np.arange(fit_scaled.shape[1])
    return fit_scaled[:, idx], valid_scaled[:, idx], idx


def tune_inner(x, y, train_idx, inner_splits, seed, k_values, encoder):
    inner = StratifiedKFold(n_splits=inner_splits, shuffle=True, random_state=seed)
    candidates = candidate_grid(seed, len(encoder.classes_), k_values)
    scores = []
    for cand in candidates:
        fold_scores = []
        for fit_rel, valid_rel in inner.split(train_idx, y[train_idx]):
            fit_idx, valid_idx = train_idx[fit_rel], train_idx[valid_rel]
            x_fit, x_valid, idx = transformed_fold(x[fit_idx], x[valid_idx], y[fit_idx], cand["mode"], cand["k"])
            model = cand["estimator"]
            model.fit(x_fit, encoder.transform(y[fit_idx]))
            pred = encoder.inverse_transform(model.predict(x_valid).astype(int))
            fold_scores.append(f1_score(y[valid_idx], pred, average="macro", zero_division=0))
        scores.append({"config": cand["config"], "model": cand["model"], "mode": cand["mode"], "k": cand["k"], "inner_macro_f1": float(np.mean(fold_scores)), "inner_macro_f1_std": float(np.std(fold_scores, ddof=1))})
    return sorted(scores, key=lambda r: (-r["inner_macro_f1"], r["config"]))[0], scores


def fit_outer(x, y, train_idx, test_idx, selected, seed, encoder):
    x_fit, x_test, idx = transformed_fold(x[train_idx], x[test_idx], y[train_idx], selected["mode"], selected["k"])
    candidates = {c["config"]: c for c in candidate_grid(seed, len(encoder.classes_), [20, 40, 60])}
    model = candidates[selected["config"]]["estimator"]
    start = time.perf_counter(); model.fit(x_fit, encoder.transform(y[train_idx])); train_s = time.perf_counter() - start
    start = time.perf_counter(); pred_num = model.predict(x_test).astype(int); proba = model.predict_proba(x_test); predict_s = time.perf_counter() - start
    pred = encoder.inverse_transform(pred_num)
    return idx, pred, proba, train_s, predict_s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--outer-splits", type=int, default=3)
    ap.add_argument("--inner-splits", type=int, default=3)
    ap.add_argument("--k-values", type=int, nargs="+", default=[20, 40, 60])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    x, y, names = load_data(args.processed_dir)
    encoder = LabelEncoder().fit(y)
    outer = StratifiedKFold(n_splits=args.outer_splits, shuffle=True, random_state=args.seed)
    pred_dir = args.output_dir / "predictions"; pred_dir.mkdir(exist_ok=True)
    rows=[]; tuning_rows=[]
    for fold, (train_idx, test_idx) in enumerate(outer.split(x, y), start=1):
        selected, all_scores = tune_inner(x, y, train_idx, args.inner_splits, args.seed + fold, args.k_values, encoder)
        for row in all_scores: tuning_rows.append({"fold":fold, **row})
        idx, pred, proba, train_s, predict_s = fit_outer(x, y, train_idx, test_idx, selected, args.seed + fold, encoder)
        metrics = evaluate_predictions(y[test_idx], pred, proba, encoder.classes_)
        rows.append({"fold":fold,"seed":args.seed,"selected_config":selected["config"],"selected_model":selected["model"],"feature_mode":selected["mode"],"k":selected["k"] or x.shape[1],"feature_count":len(idx),"inner_macro_f1":selected["inner_macro_f1"],"train_seconds":train_s,"predict_seconds":predict_s,"test_samples":len(test_idx),**metrics})
        out = pd.DataFrame({"row_index":test_idx,"y_true":y[test_idx],"y_pred":pred})
        for j,label in enumerate(encoder.classes_): out[f"proba_{label}"]=proba[:,j]
        out.to_csv(pred_dir / f"predictions_fold{fold}.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(rows).to_csv(args.output_dir / "outer_fold_metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(tuning_rows).to_csv(args.output_dir / "inner_tuning_results.csv", index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(rows).groupby("selected_model")[["accuracy","balanced_accuracy","macro_f1","log_loss","brier_macro","ece"]].agg(["mean","std"]).reset_index()
    summary.to_csv(args.output_dir / "outer_summary.csv", index=False, encoding="utf-8-sig")
    (args.output_dir / "protocol.json").write_text(json.dumps({"data":"data_processed_audit_v4 development pool (train+validation)", "held_out_test":"data_processed_audit_v4/test.csv remains untouched", "outer_splits":args.outer_splits,"inner_splits":args.inner_splits,"k_values":args.k_values,"seed":args.seed,"preprocessing":"fit inside each fold","test_usage":"outer-fold evaluation on development pool only"}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
