"""Native-label external benchmark runner with strict train/test boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, classification_report, confusion_matrix, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.cfrg_forest import CFRGForest


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return {"path": str(path), "bytes": Path(path).stat().st_size, "sha256": h.hexdigest()}


def _encode_train_test(train, test, drop):
    names = [c for c in train.columns if c in test.columns and c not in drop]
    categorical = [c for c in names if train[c].dtype == object]
    train_part = pd.get_dummies(train[names], columns=categorical, dummy_na=True)
    test_part = pd.get_dummies(test[names], columns=categorical, dummy_na=True).reindex(columns=train_part.columns, fill_value=0)
    return train_part.apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(float), test_part.apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(float), list(train_part.columns)


def _metric(y, pred, p, classes):
    return {"accuracy": float(np.mean(pred == y)), "balanced_accuracy": float(balanced_accuracy_score(y, pred)), "macro_f1": float(f1_score(y, pred, labels=classes, average="macro", zero_division=0)), "log_loss": float(log_loss(y, p, labels=list(classes))), "brier_macro": float(np.mean([brier_score_loss((y == c).astype(int), p[:, i]) for i, c in enumerate(classes)])), **calibration_errors(y, p, class_labels=classes)}


def _save_model(out, name, y, pred, p, classes):
    pd.DataFrame(classification_report(y, pred, labels=classes, output_dict=True, zero_division=0)).T.to_csv(out / f"classification_report_{name}.csv", encoding="utf-8-sig")
    cm = confusion_matrix(y, pred, labels=classes); pd.DataFrame(cm, index=classes, columns=classes).to_csv(out / f"confusion_matrix_{name}.csv", encoding="utf-8-sig"); pd.DataFrame(cm / np.maximum(cm.sum(axis=1, keepdims=True), 1), index=classes, columns=classes).to_csv(out / f"confusion_matrix_normalized_{name}.csv", encoding="utf-8-sig")
    frame = pd.DataFrame({"row_id": np.arange(len(y)), "y_true": y, "y_pred": pred}); [frame.__setitem__(f"proba__{c}", p[:, i]) for i, c in enumerate(classes)]; frame.to_csv(out / f"predictions_{name}.csv", index=False, encoding="utf-8-sig")
    pd.Series(pred).value_counts().rename_axis("predicted_label").reset_index(name="count").to_csv(out / f"predicted_class_counts_{name}.csv", index=False, encoding="utf-8-sig")


def _predict_in_chunks(model, X, chunk_size=10000):
    probabilities = []
    for start in range(0, len(X), int(chunk_size)):
        probabilities.append(model.predict_proba(X[start:start + int(chunk_size)]))
    return np.vstack(probabilities)


def run_unsw(raw_dir, output_dir, k=60, n_estimators=100, seeds=(42, 2024, 3407)):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    train_path, test_path = raw_dir / "UNSW-NB15_training-set.csv", raw_dir / "UNSW-NB15_testing-set.csv"
    train, test = pd.read_csv(train_path, low_memory=False), pd.read_csv(test_path, low_memory=False)
    X_train_raw, X_test_raw, names = _encode_train_test(train, test, {"id", "label", "attack_cat"})
    y_train, y_test = train["attack_cat"].fillna("Normal").astype(str).str.strip().to_numpy(), test["attack_cat"].fillna("Normal").astype(str).str.strip().to_numpy()
    classes = np.array(sorted(np.unique(y_train)))
    fit_idx, valid_idx = train_test_split(np.arange(len(y_train)), test_size=.2, random_state=42, stratify=y_train)
    for seed in seeds:
        out = output_dir / f"seed_{int(seed)}"; out.mkdir(parents=True, exist_ok=True)
        scaler = MinMaxScaler().fit(X_train_raw[fit_idx]); X_fit, X_valid, X_test = scaler.transform(X_train_raw[fit_idx]), scaler.transform(X_train_raw[valid_idx]), scaler.transform(X_test_raw)
        scores, _ = chi2(X_fit, y_train[fit_idx]); idx = np.argsort(-np.nan_to_num(scores, nan=0.0))[: min(int(k), X_fit.shape[1])]
        specs = {"equal_rf_chi2": RandomForestClassifier(n_estimators=n_estimators, class_weight="balanced_subsample", min_samples_leaf=2, random_state=seed, n_jobs=-1), "extra_trees_chi2": ExtraTreesClassifier(n_estimators=n_estimators, class_weight="balanced", min_samples_leaf=2, random_state=seed, n_jobs=-1), "cfrg_forest_chi2": CFRGForest(n_estimators=n_estimators, class_weight="balanced_subsample", min_samples_leaf=2, random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0, n_jobs=-1)}
        rows = []
        for name, model in specs.items():
            start = time.perf_counter(); model.fit(X_fit[:, idx], y_train[fit_idx]); train_s = time.perf_counter() - start; start = time.perf_counter(); p = _predict_in_chunks(model, X_test[:, idx]); pred = model.classes_[np.argmax(p, axis=1)]; pred_s = time.perf_counter() - start
            rows.append({"model": name, **_metric(y_test, pred, p, model.classes_), "train_seconds": train_s, "predict_seconds": pred_s, "test_samples": len(y_test)}); _save_model(out, name, y_test, pred, p, model.classes_)
        pd.DataFrame(rows).to_csv(out / "metrics.csv", index=False, encoding="utf-8-sig")
        protocol = {"dataset": "UNSW-NB15", "official_train_test_boundary": True, "cross_dataset_transfer": False, "encoding_fit_on": "official_training_only", "scaler_fit_on": "official_training_only", "feature_selection_fit_on": "official_training_only", "train_rows": len(y_train), "test_rows": len(y_test), "chi2_k": int(k), "n_estimators": int(n_estimators), "seed": int(seed), "files": [_hash(train_path), _hash(test_path)]}
        (out / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_dir


def main():
    p = argparse.ArgumentParser(); p.add_argument("--raw-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--dataset", choices=["UNSW-NB15"], default="UNSW-NB15"); p.add_argument("--chi2-k", type=int, default=60); p.add_argument("--n-estimators", type=int, default=100); p.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); args = p.parse_args(); run_unsw(args.raw_dir, args.output_dir, args.chi2_k, args.n_estimators, args.seeds)


if __name__ == "__main__": main()
