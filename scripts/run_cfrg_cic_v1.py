"""Locked CIC runner for CFRG-Forest and comparable baselines."""

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

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.cfrg_forest import CFRGForest


def _brier_macro(y_true, probabilities, classes):
    return float(np.mean([brier_score_loss((np.asarray(y_true) == c).astype(int), probabilities[:, i]) for i, c in enumerate(classes)]))


def _metric_row(y_true, pred, probabilities, classes):
    p = np.clip(np.asarray(probabilities, dtype=float), 0.0, 1.0)
    p /= np.maximum(p.sum(axis=1, keepdims=True), np.finfo(float).tiny)
    out = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_precision": float(precision_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, pred, labels=classes, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y_true, p, labels=list(classes))),
        "brier_macro": _brier_macro(y_true, p, classes),
    }
    out.update(calibration_errors(y_true, p, class_labels=classes))
    return out


def _load(processed_dir):
    frames = {s: pd.read_csv(Path(processed_dir) / f"{s}.csv", low_memory=False) for s in ("train", "validation", "test")}
    features = [c for c in frames["train"].columns if c != "target"]
    if any(list(frames[s].columns) != features + ["target"] for s in frames):
        raise ValueError("inconsistent split schema")
    arrays = {s: frames[s][features].apply(pd.to_numeric, errors="raise").to_numpy(float) for s in frames}
    labels = {s: frames[s]["target"].to_numpy() for s in frames}
    return arrays, labels, features


def _save(out, name, seed, y_true, pred, probabilities, classes):
    pd.DataFrame(classification_report(y_true, pred, labels=classes, output_dict=True, zero_division=0)).T.to_csv(out / f"classification_report_{name}_seed{seed}.csv", encoding="utf-8-sig")
    cm = confusion_matrix(y_true, pred, labels=classes)
    pd.DataFrame(cm, index=classes, columns=classes).to_csv(out / f"confusion_matrix_{name}_seed{seed}.csv", encoding="utf-8-sig")
    normalized = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1)
    pd.DataFrame(normalized, index=classes, columns=classes).to_csv(out / f"confusion_matrix_normalized_{name}_seed{seed}.csv", encoding="utf-8-sig")
    frame = pd.DataFrame({"row_id": np.arange(len(y_true)), "y_true": y_true, "y_pred": pred})
    for i, c in enumerate(classes):
        frame[f"proba__{c}"] = probabilities[:, i]
    (out / "predictions").mkdir(exist_ok=True)
    frame.to_csv(out / "predictions" / f"predictions_{name}_seed{seed}.csv", index=False, encoding="utf-8-sig")


def run(processed_dir, output_dir, chi2_k=60, n_estimators=100, min_samples_leaf=2, seeds=(42, 2024, 3407)):
    processed_dir, output_dir = Path(processed_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    arrays, labels, features = _load(processed_dir)
    scaler = MinMaxScaler().fit(arrays["train"])
    Xtr, Xv, Xte = scaler.transform(arrays["train"]), scaler.transform(arrays["validation"]), scaler.transform(arrays["test"])
    scores, _ = chi2(Xtr, labels["train"])
    idx = np.argsort(-np.nan_to_num(scores, nan=0.0, posinf=0.0))[: min(int(chi2_k), Xtr.shape[1])]
    selected = [features[i] for i in idx]
    pd.DataFrame({"feature": features, "chi2": np.nan_to_num(scores, nan=0.0)}).sort_values("chi2", ascending=False).to_csv(output_dir / "feature_scores_training_only.csv", index=False, encoding="utf-8-sig")
    (output_dir / "selected_features.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    classes = np.unique(labels["train"])
    rows = []
    for seed in [int(s) for s in seeds]:
        specs = {
            "equal_rf_chi2": RandomForestClassifier(n_estimators=n_estimators, random_state=seed, min_samples_leaf=min_samples_leaf, class_weight="balanced_subsample", n_jobs=-1),
            "equal_rf_all": RandomForestClassifier(n_estimators=n_estimators, random_state=seed, min_samples_leaf=min_samples_leaf, class_weight="balanced_subsample", n_jobs=-1),
            "extra_trees_chi2": ExtraTreesClassifier(n_estimators=n_estimators, random_state=seed, min_samples_leaf=min_samples_leaf, class_weight="balanced", n_jobs=-1),
            "cfrg_forest_chi2": CFRGForest(n_estimators=n_estimators, random_state=seed, min_samples_leaf=min_samples_leaf, cost_beta=0.0, cost_min=1.0, cost_max=1.0, n_jobs=-1),
        }
        matrices = {"equal_rf_chi2": (Xtr[:, idx], Xv[:, idx], Xte[:, idx]), "equal_rf_all": (Xtr, Xv, Xte), "extra_trees_chi2": (Xtr[:, idx], Xv[:, idx], Xte[:, idx]), "cfrg_forest_chi2": (Xtr[:, idx], Xv[:, idx], Xte[:, idx])}
        for name, model in specs.items():
            x_train, _x_valid, x_test = matrices[name]
            start = time.perf_counter(); model.fit(x_train, labels["train"]); train_s = time.perf_counter() - start
            start = time.perf_counter(); prob = model.predict_proba(x_test); pred = model.classes_[np.argmax(prob, axis=1)]; pred_s = time.perf_counter() - start
            row = _metric_row(labels["test"], pred, prob, model.classes_); row.update({"model": name, "seed": seed, "train_seconds": train_s, "predict_seconds": pred_s, "feature_count": x_train.shape[1]}); rows.append(row)
            _save(output_dir, name, seed, labels["test"], pred, prob, model.classes_)
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    agg = table.groupby("model")["accuracy balanced_accuracy macro_precision macro_recall macro_f1 log_loss brier_macro ece mce train_seconds predict_seconds".split()].agg(["mean", "std"]).reset_index()
    agg.columns = ["_".join(str(x) for x in col if str(x) not in ("", "nan")) if isinstance(col, tuple) else str(col) for col in agg.columns]
    agg.to_csv(output_dir / "metrics_aggregate_flat.csv", index=False, encoding="utf-8-sig")
    protocol = {"protocol_name": "CIC-IDS2017_locked_cfrg_v1", "processed_dir": str(processed_dir), "train_samples": len(labels["train"]), "validation_samples": len(labels["validation"]), "test_samples": len(labels["test"]), "raw_feature_count": len(features), "selected_feature_count": len(selected), "chi2_k": int(chi2_k), "n_estimators": int(n_estimators), "min_samples_leaf": int(min_samples_leaf), "seeds": [int(s) for s in seeds], "feature_selection_fit_on": "training_only", "gate_fit_on": "oob_training_predictions_only", "test_usage": "locked_final_evaluation_only", "cross_dataset_transfer": False}
    (output_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    print(table[["model", "seed", "accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro"]].to_string(index=False))
    return table


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--processed-dir", type=Path, required=True); parser.add_argument("--output-dir", type=Path, required=True); parser.add_argument("--chi2-k", type=int, default=60); parser.add_argument("--n-estimators", type=int, default=100); parser.add_argument("--min-samples-leaf", type=int, default=2); parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); args = parser.parse_args(); run(args.processed_dir, args.output_dir, args.chi2_k, args.n_estimators, args.min_samples_leaf, args.seeds)


if __name__ == "__main__": main()
