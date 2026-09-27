"""Leakage-safe chi-square k selection and final hold-out evaluation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import WeightedRandomForest, compute_metrics, select_chi2_features
from src.audit_utils import assert_no_feature_overlap, flatten_aggregate_columns, validate_split_schema


def choose_best_k(validation_table: pd.DataFrame) -> int:
    required = {"k", "validation_macro_f1", "validation_accuracy"}
    missing = required.difference(validation_table.columns)
    if missing:
        raise ValueError(f"缺少验证集选择字段: {sorted(missing)}")
    best = validation_table.sort_values(
        ["validation_macro_f1", "validation_accuracy", "k"],
        ascending=[False, False, True],
    ).iloc[0]
    return int(best["k"])


def load_split(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]), frame["target"]


def prepare_features(processed_dir: Path):
    X_train, y_train = load_split(processed_dir / "train.csv")
    X_valid, y_valid = load_split(processed_dir / "validation.csv")
    X_test, y_test = load_split(processed_dir / "test.csv")
    names = list(X_train.columns)
    X_train = X_train[names].apply(pd.to_numeric, errors="coerce").fillna(0)
    X_valid = X_valid[names].apply(pd.to_numeric, errors="coerce").fillna(0)
    X_test = X_test[names].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaler = MinMaxScaler()
    return names, scaler.fit_transform(X_train), scaler.transform(X_valid), scaler.transform(X_test), y_train, y_valid, y_test


def evaluate_rf(X_train, y_train, X_eval, y_eval, seed, n_estimators):
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample")
    start = time.perf_counter(); model.fit(X_train, y_train); train_s = time.perf_counter() - start
    start = time.perf_counter(); pred = model.predict(X_eval); pred_s = time.perf_counter() - start
    metrics = compute_metrics(y_eval, pred)
    metrics.update({"train_seconds": train_s, "predict_seconds": pred_s, "model": "random_forest_chi2", "seed": seed})
    return metrics, pred


def evaluate_weighted_rf(X_train, y_train, X_valid, y_valid, X_test, y_test, seed, n_estimators):
    model = WeightedRandomForest(n_estimators=n_estimators, random_state=seed)
    start = time.perf_counter(); model.fit(X_train, y_train, X_valid, y_valid); train_s = time.perf_counter() - start
    start = time.perf_counter(); pred = model.predict(X_test); pred_s = time.perf_counter() - start
    metrics = compute_metrics(y_test, pred)
    metrics.update({"train_seconds": train_s, "predict_seconds": pred_s, "model": "weighted_rf_chi2", "seed": seed})
    return metrics, model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path(r"E:\论文\data\processed_dedup"))
    parser.add_argument("--output-dir", type=Path, default=Path(r"E:\论文\results_leakage_safe"))
    parser.add_argument("--candidate-k", type=int, nargs="+", default=[10, 20, 30, 40, 60])
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    train_frame = pd.read_csv(args.processed_dir / "train.csv", low_memory=False)
    valid_frame = pd.read_csv(args.processed_dir / "validation.csv", low_memory=False)
    test_frame = pd.read_csv(args.processed_dir / "test.csv", low_memory=False)
    schema_report = validate_split_schema(train_frame, valid_frame, test_frame)
    overlap_report = assert_no_feature_overlap(train_frame, valid_frame, test_frame)
    (args.output_dir / "split_schema_audit.json").write_text(json.dumps(schema_report, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "split_overlap_audit.json").write_text(json.dumps(overlap_report, ensure_ascii=False, indent=2), encoding="utf-8")
    names, Xtr, Xv, Xte, ytr, yv, yte = prepare_features(args.processed_dir)
    ranking_features, ranking = select_chi2_features(pd.DataFrame(Xtr, columns=names), ytr, k=min(max(args.candidate_k), len(names)))
    ranking.to_csv(args.output_dir / "feature_scores_training_only.csv", index=False, encoding="utf-8-sig")
    index = {name: i for i, name in enumerate(names)}
    validation_rows = []
    for k in args.candidate_k:
        selected, _ = select_chi2_features(pd.DataFrame(Xtr, columns=names), ytr, k=k)
        idx = [index[name] for name in selected]
        for seed in args.seeds:
            model = RandomForestClassifier(n_estimators=args.n_estimators, random_state=seed, n_jobs=-1, class_weight="balanced_subsample")
            model.fit(Xtr[:, idx], ytr); pred = model.predict(Xv[:, idx]); m = compute_metrics(yv, pred)
            validation_rows.append({"k": k, "seed": seed, "validation_accuracy": m["accuracy"], "validation_macro_f1": m["macro_f1"]})
    validation = pd.DataFrame(validation_rows)
    validation.to_csv(args.output_dir / "k_selection_validation_results.csv", index=False, encoding="utf-8-sig")
    validation_mean = validation.groupby("k", as_index=False)[["validation_accuracy", "validation_macro_f1"]].mean()
    validation_mean.to_csv(args.output_dir / "k_selection_validation_summary.csv", index=False, encoding="utf-8-sig")
    best_k = choose_best_k(validation_mean)
    (args.output_dir / "selected_k.json").write_text(json.dumps({"best_k": best_k, "selection_metric": "validation_macro_f1", "candidate_k": args.candidate_k}, ensure_ascii=False, indent=2), encoding="utf-8")
    selected, _ = select_chi2_features(pd.DataFrame(Xtr, columns=names), ytr, k=best_k); idx = [index[name] for name in selected]
    final_rows = []
    for seed in args.seeds:
        m, pred = evaluate_rf(Xtr[:, idx], ytr, Xte[:, idx], yte, seed, args.n_estimators); m.update({"k": best_k, "feature_count": len(selected), "selection_metric": "validation_macro_f1"}); final_rows.append(m)
        pd.DataFrame(classification_report(yte, pred, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"final_classification_report_rf_seed{seed}.csv", encoding="utf-8-sig")
        labels = sorted(pd.unique(pd.concat([pd.Series(yte), pd.Series(pred)]))); pd.DataFrame(confusion_matrix(yte, pred, labels=labels), index=labels, columns=labels).to_csv(args.output_dir / f"final_confusion_matrix_rf_seed{seed}.csv", encoding="utf-8-sig")
        wm, weighted = evaluate_weighted_rf(Xtr[:, idx], ytr, Xv[:, idx], yv, Xte[:, idx], yte, seed, args.n_estimators); wm.update({"k": best_k, "feature_count": len(selected), "selection_metric": "validation_macro_f1"}); final_rows.append(wm)
        pd.DataFrame({"tree_score": weighted.tree_scores_, "tree_weight": weighted.tree_weights_}).to_csv(args.output_dir / f"final_tree_weights_seed{seed}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(classification_report(yte, weighted.predict(Xte[:, idx]), output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"final_classification_report_weighted_rf_seed{seed}.csv", encoding="utf-8-sig")
    final = pd.DataFrame(final_rows); final.to_csv(args.output_dir / "final_test_metrics.csv", index=False, encoding="utf-8-sig")
    aggregate = final.groupby("model", as_index=False)[["accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index()
    flatten_aggregate_columns(aggregate).to_csv(args.output_dir / "final_test_metrics_aggregate_flat.csv", index=False, encoding="utf-8-sig")
    print(f"BEST_K={best_k}"); print(validation_mean.to_string(index=False)); print(final.to_string(index=False))


if __name__ == "__main__":
    main()
