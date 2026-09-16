"""Locked CIC-IDS2017 experiment for DRC-Forest and declared ablations.

The script evaluates every method on identical, leakage-controlled rows and
stores both hard predictions and probabilities for paired statistical tests.
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
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.drc_forest import DRCForest
from src.experiment_components import WeightedRandomForest, select_chi2_features


def build_protocol(args, n_train, n_valid, n_test, n_features, selected_count):
    return {
        "protocol_name": "CIC-IDS2017_locked_drc_v1",
        "data_boundary": "train_validation_test",
        "processed_dir": str(args.processed_dir),
        "train_samples": int(n_train),
        "validation_samples": int(n_valid),
        "test_samples": int(n_test),
        "raw_feature_count": int(n_features),
        "selected_feature_count": int(selected_count),
        "chi2_k": int(args.chi2_k),
        "n_estimators": int(args.n_estimators),
        "max_depth": args.max_depth,
        "min_samples_leaf": int(args.min_samples_leaf),
        "class_weight": "balanced_subsample",
        "seeds": [int(s) for s in args.seeds],
        "feature_selection_fit_on": "training_only",
        "scaler_fit_on": "training_only",
        "reliability_fit_on": "validation_only",
        "class_cost_fit_on": "training_only",
        "test_usage": "locked_final_evaluation_only",
        "method": "Dual-layer Reliability-Cost Forest (DRC-Forest)",
        "cost_beta": float(args.cost_beta),
        "cost_min": float(args.cost_min),
        "cost_max": float(args.cost_max),
    }


def write_prediction_artifact(path, y_true, y_pred, probabilities, classes):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({"row_id": np.arange(len(y_true)), "y_true": np.asarray(y_true), "y_pred": np.asarray(y_pred)})
    probabilities = np.asarray(probabilities, dtype=float)
    for i, label in enumerate(np.asarray(classes)):
        frame[f"proba__{label}"] = probabilities[:, i]
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def _brier_macro(y_true, probabilities, classes):
    y_true = np.asarray(y_true)
    probabilities = np.asarray(probabilities, dtype=float)
    labels = np.asarray(classes)
    values = []
    for i, label in enumerate(labels):
        values.append(brier_score_loss((y_true == label).astype(int), probabilities[:, i]))
    return float(np.mean(values))


def _metric_row(y_true, pred, probabilities, classes):
    probabilities = np.asarray(probabilities, dtype=float)
    probabilities = np.clip(probabilities, 0.0, 1.0)
    probabilities = probabilities / np.maximum(probabilities.sum(axis=1, keepdims=True), np.finfo(float).tiny)
    result = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_precision": float(precision_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y_true, probabilities, labels=list(classes))),
        "brier_macro": _brier_macro(y_true, probabilities, classes),
    }
    result.update(calibration_errors(y_true, probabilities, class_labels=classes))
    return result


def _fit_predict(name, model, X_train, y_train, X_valid, y_valid, X_test):
    start = time.perf_counter()
    if isinstance(model, (DRCForest, WeightedRandomForest)):
        model.fit(X_train, y_train, X_valid, y_valid)
    else:
        model.fit(X_train, y_train)
    train_seconds = time.perf_counter() - start
    start = time.perf_counter()
    probabilities = model.predict_proba(X_test)
    prediction_seconds = time.perf_counter() - start
    pred = model.classes_[np.argmax(probabilities, axis=1)] if hasattr(model, "classes_") else model.predict(X_test)
    return pred, probabilities, train_seconds, prediction_seconds, np.asarray(model.classes_)


def _drc_variant(variant, args, seed, X_train, y_train, X_valid, y_valid):
    if variant == "drc_forest_chi2":
        return DRCForest(n_estimators=args.n_estimators, random_state=seed, max_depth=args.max_depth, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, cost_beta=args.cost_beta, cost_min=args.cost_min, cost_max=args.cost_max)
    if variant == "reliability_only_rf_chi2":
        return DRCForest(n_estimators=args.n_estimators, random_state=seed, max_depth=args.max_depth, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, cost_beta=0.0, cost_min=1.0, cost_max=1.0)
    if variant == "cost_only_rf_chi2":
        model = DRCForest(n_estimators=args.n_estimators, random_state=seed, max_depth=args.max_depth, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, cost_beta=args.cost_beta, cost_min=args.cost_min, cost_max=args.cost_max)
        model._force_equal_tree_weights = True
        return model
    raise ValueError(variant)


def _apply_variant_postfit(model, variant):
    if variant == "cost_only_rf_chi2" and hasattr(model, "tree_class_weights_"):
        model.tree_class_weights_ = np.full_like(model.tree_class_weights_, 1.0 / model.tree_class_weights_.shape[0])


def load_splits(processed_dir):
    frames = {split: pd.read_csv(Path(processed_dir) / f"{split}.csv", low_memory=False) for split in ["train", "validation", "test"]}
    feature_names = [c for c in frames["train"].columns if c != "target"]
    if any([list(frames[s].columns) != feature_names + ["target"] for s in frames]):
        raise ValueError("inconsistent split schema")
    arrays = {}
    for split, frame in frames.items():
        arrays[split] = frame[feature_names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    return arrays, {s: frames[s]["target"].to_numpy() for s in frames}, feature_names


def _save_model_outputs(out_dir, name, seed, y_true, pred, probabilities, classes):
    reports = pd.DataFrame(classification_report(y_true, pred, labels=classes, output_dict=True, zero_division=0)).T
    reports.to_csv(out_dir / f"classification_report_{name}_seed{seed}.csv", encoding="utf-8-sig")
    cm = confusion_matrix(y_true, pred, labels=classes)
    pd.DataFrame(cm, index=classes, columns=classes).to_csv(out_dir / f"confusion_matrix_{name}_seed{seed}.csv", encoding="utf-8-sig")
    row_sum = np.maximum(cm.sum(axis=1, keepdims=True), 1)
    pd.DataFrame(cm / row_sum, index=classes, columns=classes).to_csv(out_dir / f"confusion_matrix_normalized_{name}_seed{seed}.csv", encoding="utf-8-sig")
    write_prediction_artifact(out_dir / "predictions" / f"predictions_{name}_seed{seed}.csv", y_true, pred, probabilities, classes)


def run(args):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    arrays, labels, feature_names = load_splits(args.processed_dir)
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(arrays["train"])
    X_valid = scaler.transform(arrays["validation"])
    X_test = scaler.transform(arrays["test"])
    selected, ranking = select_chi2_features(pd.DataFrame(X_train, columns=feature_names), labels["train"], k=args.chi2_k)
    ranking.to_csv(args.output_dir / "feature_scores_training_only.csv", index=False, encoding="utf-8-sig")
    (args.output_dir / "selected_features.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    idx = [feature_names.index(name) for name in selected]
    protocol = build_protocol(args, len(labels["train"]), len(labels["validation"]), len(labels["test"]), len(feature_names), len(selected))
    (args.output_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    classes = np.unique(labels["train"])
    for seed in args.seeds:
        specs = [
            ("equal_rf_chi2", RandomForestClassifier(n_estimators=args.n_estimators, random_state=seed, max_depth=args.max_depth, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, class_weight="balanced_subsample"), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("equal_rf_all", RandomForestClassifier(n_estimators=args.n_estimators, random_state=seed, max_depth=args.max_depth, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, class_weight="balanced_subsample"), X_train, X_valid, X_test),
            ("extra_trees_chi2", ExtraTreesClassifier(n_estimators=args.n_estimators, random_state=seed, min_samples_leaf=args.min_samples_leaf, n_jobs=-1, class_weight="balanced"), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("svm_chi2", SVC(C=10, kernel="rbf", class_weight="balanced", probability=True, random_state=seed), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("decision_tree_chi2", DecisionTreeClassifier(random_state=seed, class_weight="balanced", min_samples_leaf=args.min_samples_leaf), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("scalar_weighted_rf_chi2", WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed, min_samples_leaf=args.min_samples_leaf), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("reliability_only_rf_chi2", _drc_variant("reliability_only_rf_chi2", args, seed, X_train[:, idx], labels["train"], X_valid[:, idx], labels["validation"]), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("cost_only_rf_chi2", _drc_variant("cost_only_rf_chi2", args, seed, X_train[:, idx], labels["train"], X_valid[:, idx], labels["validation"]), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
            ("drc_forest_chi2", _drc_variant("drc_forest_chi2", args, seed, X_train[:, idx], labels["train"], X_valid[:, idx], labels["validation"]), X_train[:, idx], X_valid[:, idx], X_test[:, idx]),
        ]
        for name, model, xtr, xv, xte in specs:
            pred, probabilities, train_s, predict_s, model_classes = _fit_predict(name, model, xtr, labels["train"], xv, labels["validation"], xte)
            _apply_variant_postfit(model, name)
            if name == "cost_only_rf_chi2":
                probabilities = model.predict_proba(xte)
                pred = model.classes_[np.argmax(probabilities, axis=1)]
            metrics = _metric_row(labels["test"], pred, probabilities, model_classes)
            metrics.update({"model": name, "seed": int(seed), "train_seconds": train_s, "predict_seconds": predict_s, "test_samples": len(labels["test"]), "feature_count": len(xtr[0]) if xtr.ndim > 1 else int(xtr.shape[1])})
            rows.append(metrics)
            _save_model_outputs(args.output_dir, name, seed, labels["test"], pred, probabilities, model_classes)

    table = pd.DataFrame(rows)
    table.to_csv(args.output_dir / "metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    aggregate = table.groupby("model")[["accuracy", "balanced_accuracy", "macro_precision", "macro_recall", "macro_f1", "log_loss", "brier_macro", "ece", "mce", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index()
    aggregate.columns = ["_".join(str(v) for v in c if str(v) not in {"", "nan"}) if isinstance(c, tuple) else str(c) for c in aggregate.columns]
    aggregate.to_csv(args.output_dir / "metrics_aggregate_flat.csv", index=False, encoding="utf-8-sig")
    print(table[["model", "seed", "accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro"]].to_string(index=False))
    return table


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chi2-k", type=int, default=60)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--min-samples-leaf", type=int, default=2)
    parser.add_argument("--cost-beta", type=float, default=0.5)
    parser.add_argument("--cost-min", type=float, default=0.5)
    parser.add_argument("--cost-max", type=float, default=2.0)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
