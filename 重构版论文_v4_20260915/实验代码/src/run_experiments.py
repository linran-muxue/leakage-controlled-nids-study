"""Run baseline, chi-square, weighted voting, and ablation experiments."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import WeightedRandomForest, compute_metrics, select_chi2_features
from src.audit_utils import assert_no_feature_overlap, flatten_aggregate_columns, validate_split_schema


def load_split(path):
    frame = pd.read_csv(path, low_memory=False)
    if "target" not in frame:
        raise ValueError(f"缺少target列: {path}")
    return frame.drop(columns=["target"]), frame["target"]


def run_one(name, estimator, X_train, y_train, X_test, y_test, out_dir, seed, extra=None):
    start = time.perf_counter()
    estimator.fit(X_train, y_train)
    train_seconds = time.perf_counter() - start
    start = time.perf_counter()
    pred = estimator.predict(X_test)
    predict_seconds = time.perf_counter() - start
    metrics = compute_metrics(y_test, pred)
    metrics.update({"model": name, "seed": seed, "train_seconds": train_seconds, "predict_seconds": predict_seconds, "test_samples": len(y_test)})
    if extra:
        metrics.update(extra)
    pd.DataFrame(classification_report(y_test, pred, output_dict=True, zero_division=0)).T.to_csv(out_dir / f"classification_report_{name}_seed{seed}.csv", encoding="utf-8-sig")
    labels = sorted(pd.unique(pd.concat([pd.Series(y_test), pd.Series(pred)])))
    pd.DataFrame(confusion_matrix(y_test, pred, labels=labels), index=labels, columns=labels).to_csv(out_dir / f"confusion_matrix_{name}_seed{seed}.csv", encoding="utf-8-sig")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path(r"E:\论文\data\processed"))
    parser.add_argument("--output-dir", type=Path, default=Path(r"E:\论文\results"))
    parser.add_argument("--chi2-k", type=int, default=20)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X_train_raw, y_train = load_split(args.processed_dir / "train.csv")
    X_valid_raw, y_valid = load_split(args.processed_dir / "validation.csv")
    X_test_raw, y_test = load_split(args.processed_dir / "test.csv")
    train_frame = pd.read_csv(args.processed_dir / "train.csv", low_memory=False)
    valid_frame = pd.read_csv(args.processed_dir / "validation.csv", low_memory=False)
    test_frame = pd.read_csv(args.processed_dir / "test.csv", low_memory=False)
    schema_report = validate_split_schema(train_frame, valid_frame, test_frame)
    overlap_report = assert_no_feature_overlap(train_frame, valid_frame, test_frame)
    (args.output_dir / "split_schema_audit.json").write_text(json.dumps(schema_report, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "split_overlap_audit.json").write_text(json.dumps(overlap_report, ensure_ascii=False, indent=2), encoding="utf-8")
    feature_names = list(X_train_raw.columns)
    X_train_raw = X_train_raw[feature_names].apply(pd.to_numeric, errors="raise")
    X_valid_raw = X_valid_raw[feature_names].apply(pd.to_numeric, errors="raise")
    X_test_raw = X_test_raw[feature_names].apply(pd.to_numeric, errors="raise")

    scaler = MinMaxScaler()
    X_train_all = scaler.fit_transform(X_train_raw)
    X_valid_all = scaler.transform(X_valid_raw)
    X_test_all = scaler.transform(X_test_raw)
    selected, ranking = select_chi2_features(pd.DataFrame(X_train_all, columns=feature_names), y_train, k=args.chi2_k)
    ranking.to_csv(args.output_dir / "feature_scores.csv", index=False, encoding="utf-8-sig")
    (args.output_dir / "selected_features.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    selected_idx = [feature_names.index(name) for name in selected]

    all_results = []
    for seed in args.seeds:
        configs = [
            ("decision_tree_all", DecisionTreeClassifier(random_state=seed, class_weight="balanced"), X_train_all, X_test_all, {}),
            ("svm_chi2", SVC(kernel="rbf", C=10, gamma="scale", class_weight="balanced"), X_train_all[:, selected_idx], X_test_all[:, selected_idx], {"feature_mode": "chi2", "feature_count": len(selected)}),
            ("random_forest_all", RandomForestClassifier(n_estimators=args.n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample"), X_train_all, X_test_all, {"feature_mode": "all", "feature_count": len(feature_names)}),
            ("random_forest_chi2", RandomForestClassifier(n_estimators=args.n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample"), X_train_all[:, selected_idx], X_test_all[:, selected_idx], {"feature_mode": "chi2", "feature_count": len(selected)}),
        ]
        for name, estimator, xtr, xte, extra in configs:
            all_results.append(run_one(name, estimator, xtr, y_train, xte, y_test, args.output_dir, seed, extra))

        weighted_all = WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed)
        start = time.perf_counter(); weighted_all.fit(X_train_all, y_train, X_valid_all, y_valid); train_seconds = time.perf_counter() - start
        start = time.perf_counter(); pred = weighted_all.predict(X_test_all); predict_seconds = time.perf_counter() - start
        metrics = compute_metrics(y_test, pred); metrics.update({"model": "weighted_rf_all", "seed": seed, "train_seconds": train_seconds, "predict_seconds": predict_seconds, "test_samples": len(y_test), "feature_mode": "all", "feature_count": len(feature_names)})
        all_results.append(metrics)
        pd.DataFrame({"tree_score": weighted_all.tree_scores_, "tree_weight": weighted_all.tree_weights_}).to_csv(args.output_dir / f"tree_weights_all_seed{seed}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(classification_report(y_test, pred, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"classification_report_weighted_rf_all_seed{seed}.csv", encoding="utf-8-sig")

        weighted_chi2 = WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed)
        start = time.perf_counter(); weighted_chi2.fit(X_train_all[:, selected_idx], y_train, X_valid_all[:, selected_idx], y_valid); train_seconds = time.perf_counter() - start
        start = time.perf_counter(); pred = weighted_chi2.predict(X_test_all[:, selected_idx]); predict_seconds = time.perf_counter() - start
        metrics = compute_metrics(y_test, pred); metrics.update({"model": "weighted_rf_chi2", "seed": seed, "train_seconds": train_seconds, "predict_seconds": predict_seconds, "test_samples": len(y_test), "feature_mode": "chi2", "feature_count": len(selected)})
        all_results.append(metrics)
        pd.DataFrame({"tree_score": weighted_chi2.tree_scores_, "tree_weight": weighted_chi2.tree_weights_}).to_csv(args.output_dir / f"tree_weights_chi2_seed{seed}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(classification_report(y_test, pred, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"classification_report_weighted_rf_chi2_seed{seed}.csv", encoding="utf-8-sig")

    results = pd.DataFrame(all_results)
    results.to_csv(args.output_dir / "metrics_summary.csv", index=False, encoding="utf-8-sig")
    aggregate = results.groupby("model", as_index=False)[["accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index()
    flatten_aggregate_columns(aggregate).to_csv(args.output_dir / "metrics_aggregate_flat.csv", index=False, encoding="utf-8-sig")
    print(results[["model", "seed", "accuracy", "macro_f1", "train_seconds", "predict_seconds"]].to_string(index=False))


if __name__ == "__main__":
    main()
