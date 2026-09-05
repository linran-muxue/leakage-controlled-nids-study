"""Fair final comparison: same leakage-safe splits, metrics, seeds and test set."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import WeightedRandomForest, compute_metrics, select_chi2_features
from src.audit_utils import assert_no_feature_overlap, flatten_aggregate_columns, validate_split_schema


def build_model_specs(n_estimators: int, seed: int, selected_count: int):
    return [
        ("decision_tree_all", DecisionTreeClassifier(random_state=seed, class_weight="balanced"), "all", {"feature_mode": "all", "feature_count": None}),
        ("decision_tree_chi2", DecisionTreeClassifier(random_state=seed, class_weight="balanced"), "chi2", {"feature_mode": "chi2", "feature_count": selected_count}),
        ("svm_all", SVC(kernel="rbf", C=10, gamma="scale", class_weight="balanced"), "all", {"feature_mode": "all", "feature_count": None}),
        ("svm_chi2", SVC(kernel="rbf", C=10, gamma="scale", class_weight="balanced"), "chi2", {"feature_mode": "chi2", "feature_count": selected_count}),
        ("random_forest_all", RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample"), "all", {"feature_mode": "all", "feature_count": None}),
        ("random_forest_chi2", RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample"), "chi2", {"feature_mode": "chi2", "feature_count": selected_count}),
        ("extra_trees_chi2", ExtraTreesClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced"), "chi2", {"feature_mode": "chi2", "feature_count": selected_count}),
    ]


def load_split(path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]), frame["target"]


def evaluate(name, model, X_train, y_train, X_test, y_test, out_dir, seed, extra):
    start = time.perf_counter(); model.fit(X_train, y_train); train_s = time.perf_counter() - start
    start = time.perf_counter(); pred = model.predict(X_test); predict_s = time.perf_counter() - start
    metrics = compute_metrics(y_test, pred)
    metrics.update({"model": name, "seed": seed, "train_seconds": train_s, "predict_seconds": predict_s, "test_samples": len(y_test), **extra})
    pd.DataFrame(classification_report(y_test, pred, output_dict=True, zero_division=0)).T.to_csv(out_dir / f"classification_report_{name}_seed{seed}.csv", encoding="utf-8-sig")
    labels = sorted(pd.unique(pd.concat([pd.Series(y_test), pd.Series(pred)])))
    pd.DataFrame(confusion_matrix(y_test, pred, labels=labels), index=labels, columns=labels).to_csv(out_dir / f"confusion_matrix_{name}_seed{seed}.csv", encoding="utf-8-sig")
    pd.DataFrame({"y_true": y_test, "y_pred": pred}).to_csv(out_dir / f"predictions_{name}_seed{seed}.csv", index=False, encoding="utf-8-sig")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path(r"E:\论文\data\processed_dedup"))
    parser.add_argument("--output-dir", type=Path, default=Path(r"E:\论文\results_fair_final"))
    parser.add_argument("--chi2-k", type=int, default=60)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    names, Xtr_raw, Xv_raw, Xte_raw, ytr, yv, yte = None, *[None] * 6
    Xtr_raw, ytr = load_split(args.processed_dir / "train.csv"); Xv_raw, yv = load_split(args.processed_dir / "validation.csv"); Xte_raw, yte = load_split(args.processed_dir / "test.csv")
    train_frame = pd.read_csv(args.processed_dir / "train.csv", low_memory=False)
    valid_frame = pd.read_csv(args.processed_dir / "validation.csv", low_memory=False)
    test_frame = pd.read_csv(args.processed_dir / "test.csv", low_memory=False)
    schema_report = validate_split_schema(train_frame, valid_frame, test_frame)
    (args.output_dir / "split_schema_audit.json").write_text(json.dumps(schema_report, ensure_ascii=False, indent=2), encoding="utf-8")
    overlap_report = assert_no_feature_overlap(train_frame, valid_frame, test_frame)
    (args.output_dir / "split_overlap_audit.json").write_text(json.dumps(overlap_report, ensure_ascii=False, indent=2), encoding="utf-8")
    names = list(Xtr_raw.columns)
    Xtr_raw = Xtr_raw[names].apply(pd.to_numeric, errors="raise"); Xv_raw = Xv_raw[names].apply(pd.to_numeric, errors="raise"); Xte_raw = Xte_raw[names].apply(pd.to_numeric, errors="raise")
    scaler = MinMaxScaler(); Xtr = scaler.fit_transform(Xtr_raw); Xv = scaler.transform(Xv_raw); Xte = scaler.transform(Xte_raw)
    selected, ranking = select_chi2_features(pd.DataFrame(Xtr, columns=names), ytr, k=args.chi2_k); ranking.to_csv(args.output_dir / "feature_scores_training_only.csv", index=False, encoding="utf-8-sig"); (args.output_dir / "selected_features.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    idx = [names.index(name) for name in selected]
    all_results = []
    for seed in args.seeds:
        for name, model, mode, extra in build_model_specs(args.n_estimators, seed, len(selected)):
            xtr, xte = (Xtr, Xte) if mode == "all" else (Xtr[:, idx], Xte[:, idx])
            if extra["feature_count"] is None: extra["feature_count"] = len(names)
            all_results.append(evaluate(name, model, xtr, ytr, xte, yte, args.output_dir, seed, extra))
        weighted = WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed, weight_metric="balanced_accuracy")
        start = time.perf_counter(); weighted.fit(Xtr[:, idx], ytr, Xv[:, idx], yv); train_s = time.perf_counter() - start
        start = time.perf_counter(); pred = weighted.predict(Xte[:, idx]); predict_s = time.perf_counter() - start
        metrics = compute_metrics(yte, pred); metrics.update({"model": "weighted_rf_chi2", "seed": seed, "train_seconds": train_s, "predict_seconds": predict_s, "test_samples": len(yte), "feature_mode": "chi2", "feature_count": len(selected)})
        all_results.append(metrics); pd.DataFrame({"tree_score": weighted.tree_scores_, "tree_weight": weighted.tree_weights_}).to_csv(args.output_dir / f"tree_weights_chi2_seed{seed}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(classification_report(yte, pred, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"classification_report_weighted_rf_chi2_seed{seed}.csv", encoding="utf-8-sig")
        pd.DataFrame({"y_true": yte, "y_pred": pred}).to_csv(args.output_dir / f"predictions_weighted_rf_chi2_seed{seed}.csv", index=False, encoding="utf-8-sig")
        labels = sorted(pd.unique(pd.concat([pd.Series(yte), pd.Series(pred)]))); pd.DataFrame(confusion_matrix(yte, pred, labels=labels), index=labels, columns=labels).to_csv(args.output_dir / f"confusion_matrix_weighted_rf_chi2_seed{seed}.csv", encoding="utf-8-sig")
    results = pd.DataFrame(all_results); results.to_csv(args.output_dir / "metrics_summary.csv", index=False, encoding="utf-8-sig")
    aggregate = results.groupby("model")[["accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index()
    aggregate = flatten_aggregate_columns(aggregate)
    aggregate.to_csv(args.output_dir / "metrics_aggregate_flat.csv", index=False, encoding="utf-8-sig")
    print(results[["model", "seed", "accuracy", "macro_f1", "train_seconds", "predict_seconds"]].to_string(index=False))


if __name__ == "__main__":
    main()
