"""Scale-sensitivity experiment: the primary protocol on a 7.8x population.
The paper's main population is a 53,237-flow capped subset (2.0% of the
deduplicated corpus). Reviewers ask whether that cap drives the conclusion, so
this script repeats the headline comparison plus the main baselines on a
413,209-flow population built with the identical audit protocol and only a
larger per-class cap.

The headline control (equal-weight chi-square forest) is run on every seed the
caller passes; the context models are run on the first three seeds to bound the
compute cost. Predictions are written so the paired statistics can be computed
against the RCCF run on identical test rows.
"""
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
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import compute_metrics


def select_idx(x: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max)
    return np.sort(np.argsort(-scores, kind="stable")[:k])


def load_data(path: Path):
    tr = pd.read_csv(path / "train.csv", low_memory=False)
    te = pd.read_csv(path / "test.csv", low_memory=False)
    names = [c for c in tr.columns if c != "target"]
    scaler = MinMaxScaler()
    x = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors="raise"))
    xt = scaler.transform(te[names].apply(pd.to_numeric, errors="raise"))
    return x, tr.target.to_numpy(), xt, te.target.to_numpy(), names


def build_models(seed: int, n_estimators: int, min_samples_leaf: int):
    from xgboost import XGBClassifier
    return [
        ("decision_tree_chi2", DecisionTreeClassifier(max_depth=10, class_weight="balanced",
                                                      random_state=seed), "chi2"),
        ("equal_rf_chi2", RandomForestClassifier(n_estimators=n_estimators, n_jobs=-1,
                                                 class_weight="balanced_subsample",
                                                 min_samples_leaf=min_samples_leaf,
                                                 random_state=seed), "chi2"),
        ("equal_rf_all", RandomForestClassifier(n_estimators=n_estimators, n_jobs=-1,
                                                class_weight="balanced_subsample",
                                                min_samples_leaf=min_samples_leaf,
                                                random_state=seed), "all"),
        ("extra_trees_chi2", ExtraTreesClassifier(n_estimators=n_estimators, n_jobs=-1,
                                                  class_weight="balanced",
                                                  min_samples_leaf=min_samples_leaf,
                                                  random_state=seed), "chi2"),
        ("xgboost_chi2", XGBClassifier(n_estimators=n_estimators, max_depth=6, learning_rate=0.1,
                                       subsample=0.8, colsample_bytree=0.8,
                                       objective="multi:softprob", tree_method="hist",
                                       n_jobs=-1, random_state=seed), "chi2"),
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--context-seeds", type=int, default=3)
    ap.add_argument("--chi2-k", type=int, default=60)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--min-samples-leaf", type=int, default=2)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    x, y, xt, yt, names = load_data(args.processed_dir)
    idx = select_idx(x, y, args.chi2_k)
    labels = sorted(set(map(str, np.unique(np.concatenate([y, yt])))))
    encoder = LabelEncoder().fit(y)
    y_encoded = encoder.transform(y)
    print(f"train {x.shape}, test {xt.shape}, selected {len(idx)} feature(s)", flush=True)

    rows = []
    for position, seed in enumerate(args.seeds):
        models = build_models(seed, args.n_estimators, args.min_samples_leaf)
        if position >= args.context_seeds:
            models = [m for m in models if m[0] == "equal_rf_chi2"]
        for name, model, mode in models:
            cols = idx if mode == "chi2" else np.arange(x.shape[1])
            target = y_encoded if name.startswith("xgboost") else y
            start = time.perf_counter()
            model.fit(x[:, cols], target)
            train_seconds = time.perf_counter() - start
            start = time.perf_counter()
            pred = model.predict(xt[:, cols])
            if name.startswith("xgboost"):
                pred = encoder.inverse_transform(pred.astype(int))
            predict_seconds = time.perf_counter() - start
            rows.append({"model": name, "seed": seed, **compute_metrics(yt, pred),
                         "train_seconds": train_seconds, "predict_seconds": predict_seconds,
                         "feature_count": int(len(cols)), "test_rows": int(len(yt))})
            pd.DataFrame({"y_true": yt, "y_pred": pred}).to_csv(
                args.output_dir / f"predictions_{name}_seed{seed}.csv", index=False, encoding="utf-8-sig")
            pd.DataFrame(classification_report(yt, pred, labels=labels, output_dict=True,
                                               zero_division=0)).T.to_csv(
                args.output_dir / f"classification_report_{name}_seed{seed}.csv", encoding="utf-8-sig")
            pd.DataFrame(confusion_matrix(yt, pred, labels=labels), index=labels, columns=labels).to_csv(
                args.output_dir / f"confusion_matrix_{name}_seed{seed}.csv", encoding="utf-8-sig")
            print(f"  {name:<18} seed {seed}: macro_f1 {rows[-1]['macro_f1']:.6f} "
                  f"({train_seconds:.1f}s train)", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(args.output_dir / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    numeric = ["accuracy", "macro_precision", "macro_recall", "macro_f1",
               "train_seconds", "predict_seconds"]
    metrics.groupby("model")[numeric].agg(["mean", "std"]).to_csv(
        args.output_dir / "metrics_aggregate.csv", encoding="utf-8-sig")
    print(metrics.groupby("model")[["macro_f1", "train_seconds"]].mean().to_string())


if __name__ == "__main__":
    main()
