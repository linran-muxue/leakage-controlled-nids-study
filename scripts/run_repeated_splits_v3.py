"""Repeated split comparison for full-feature and chi-square random forests."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import compute_metrics


def paired_sign_flip(values, n_permutations=100000, seed=42):
    values = np.asarray(values, dtype=float)
    observed = float(values.mean())
    rng = np.random.default_rng(seed)
    simulated = np.empty(n_permutations, dtype=float)
    for i in range(n_permutations):
        simulated[i] = float((values * rng.choice([-1.0, 1.0], len(values))).mean())
    p = float((np.count_nonzero(np.abs(simulated) >= abs(observed) - 1e-15) + 1) / (n_permutations + 1))
    return observed, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--split-seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--chi2-k", type=int, default=60)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--min-samples-leaf", type=int, default=2)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    parts = [pd.read_csv(args.processed_dir / f"{name}.csv", low_memory=False) for name in ["train", "validation", "test"]]
    frame = pd.concat(parts, ignore_index=True)
    names = [c for c in frame.columns if c != "target"]
    x_raw = frame[names].apply(pd.to_numeric, errors="raise").to_numpy(float)
    y = frame.target.to_numpy()
    rows = []
    for split_seed in args.split_seeds:
        train_idx, rest_idx = train_test_split(np.arange(len(y)), test_size=0.30, stratify=y, random_state=split_seed)
        _, test_idx = train_test_split(rest_idx, test_size=0.50, stratify=y[rest_idx], random_state=split_seed)
        scaler = MinMaxScaler()
        x_train = scaler.fit_transform(x_raw[train_idx])
        x_test = scaler.transform(x_raw[test_idx])
        y_train, y_test = y[train_idx], y[test_idx]
        scores, _ = chi2(x_train, y_train)
        selected = np.sort(np.argsort(-np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max), kind="stable")[:args.chi2_k])
        for model_name, columns in [("rf_all", np.arange(x_train.shape[1])), ("rf_chi2", selected)]:
            model = RandomForestClassifier(
                n_estimators=args.n_estimators,
                min_samples_leaf=args.min_samples_leaf,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=split_seed,
            )
            start = time.perf_counter(); model.fit(x_train[:, columns], y_train); train_seconds = time.perf_counter() - start
            start = time.perf_counter(); prediction = model.predict(x_test[:, columns]); predict_seconds = time.perf_counter() - start
            rows.append({"split_seed": split_seed, "model": model_name, **compute_metrics(y_test, prediction), "train_seconds": train_seconds, "predict_seconds": predict_seconds})

    metrics = pd.DataFrame(rows)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False, encoding="utf-8-sig")
    metric_columns = ["accuracy", "balanced_accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]
    metrics.groupby("model")[metric_columns].agg(["mean", "std", "count"]).reset_index().to_csv(args.output_dir / "summary.csv", index=False, encoding="utf-8-sig")
    wide = metrics.pivot(index="split_seed", columns="model", values=["accuracy", "balanced_accuracy", "macro_f1"])
    tests = []
    for metric in ["accuracy", "balanced_accuracy", "macro_f1"]:
        differences = wide[(metric, "rf_chi2")] - wide[(metric, "rf_all")]
        delta, p = paired_sign_flip(differences, seed=42)
        tests.append({"metric": metric, "mean_delta_chi2_minus_all": delta, "std_delta": float(differences.std(ddof=1)), "positive_splits": int((differences > 0).sum()), "equal_splits": int((differences == 0).sum()), "negative_splits": int((differences < 0).sum()), "paired_sign_flip_p_value": p})
    pd.DataFrame(tests).to_csv(args.output_dir / "paired_split_tests.csv", index=False, encoding="utf-8-sig")
    print(metrics.groupby("model")[["accuracy", "balanced_accuracy", "macro_f1"]].agg(["mean", "std"]).to_string())
    print(pd.DataFrame(tests).to_string(index=False))


if __name__ == "__main__":
    main()
