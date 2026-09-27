"""Native-label independent benchmarks for NSL-KDD and UNSW-NB15.

This runner deliberately preserves each dataset's own label ontology and
official train/test boundary.  It is not a cross-dataset transfer experiment.
"""

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
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.drc_forest import DRCForest

NSL_DOS = {"back", "land", "mailbomb", "neptune", "pod", "processtable", "smurf", "teardrop", "udpstorm", "apache2", "dosnuke", "snmpgetattack"}
NSL_PROBE = {"ipsweep", "nmap", "portsweep", "satan", "saint", "mscan"}
NSL_R2L = {"guess_passwd", "ftp_write", "imap", "multihop", "phf", "spy", "warezclient", "warezmaster", "named", "sendmail", "snmpguess", "xlock", "xsnoop", "httptunnel", "worm"}
NSL_U2R = {"buffer_overflow", "loadmodule", "perl", "rootkit", "ps", "sqlattack", "xterm"}


def map_nsl_label(value):
    key = str(value).strip().lower()
    if key == "normal":
        return "Normal"
    if key in NSL_DOS:
        return "DoS"
    if key in NSL_PROBE:
        return "Probe"
    if key in NSL_R2L:
        return "R2L"
    if key in NSL_U2R:
        return "U2R"
    raise ValueError(f"unrecognized NSL-KDD attack label: {value}")


def make_train_validation_split(y, valid_fraction=0.2, seed=42):
    indices = np.arange(len(y))
    train_idx, valid_idx = train_test_split(indices, test_size=valid_fraction, random_state=seed, stratify=y)
    return np.asarray(train_idx), np.asarray(valid_idx)


def native_label_summary(labels):
    return {"label_set": sorted(set(map(str, labels))), "cross_dataset_transfer": False}


def file_hash(path: Path):
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha.hexdigest()}


def load_nsl(path: Path):
    train = pd.read_csv(path / "KDDTrain+.txt", header=None)
    test = pd.read_csv(path / "KDDTest+.txt", header=None)
    # NSL-KDD has 41 features, protocol/service/state categorical fields,
    # attack name at column 41, and difficulty at column 42.
    feature_cols = list(range(41))
    categorical = [1, 2, 3]
    combined = pd.concat([train.iloc[:, feature_cols], test.iloc[:, feature_cols]], ignore_index=True)
    encoded = pd.get_dummies(combined, columns=categorical, dummy_na=True)
    X_train = encoded.iloc[: len(train)].to_numpy(float)
    X_test = encoded.iloc[len(train) :].to_numpy(float)
    y_train = train.iloc[:, 41].map(map_nsl_label)
    y_test = test.iloc[:, 41].map(map_nsl_label)
    return X_train, y_train.to_numpy(), X_test, y_test.to_numpy(), [path / "KDDTrain+.txt", path / "KDDTest+.txt"]


def load_unsw(path: Path):
    train_path, test_path = path / "UNSW-NB15_training-set.csv", path / "UNSW-NB15_testing-set.csv"
    train, test = pd.read_csv(train_path, low_memory=False), pd.read_csv(test_path, low_memory=False)
    label_col = "attack_cat"
    drop = {"id", "label", "attack_cat"}
    names = [col for col in train.columns if col in test.columns and col not in drop]
    categorical = [col for col in names if train[col].dtype == object]
    train_part = pd.get_dummies(train[names], columns=categorical, dummy_na=True)
    test_part = pd.get_dummies(test[names], columns=categorical, dummy_na=True).reindex(columns=train_part.columns, fill_value=0)
    return train_part.apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(float), train[label_col].fillna("Normal").astype(str).str.strip().to_numpy(), test_part.apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(float), test[label_col].fillna("Normal").astype(str).str.strip().to_numpy(), [train_path, test_path]


def _fit_one(name, model, X_train, y_train, X_valid, y_valid, X_test, y_test, classes, out_dir):
    start = time.perf_counter(); model.fit(X_train, y_train, X_valid, y_valid) if isinstance(model, DRCForest) else model.fit(X_train, y_train); train_seconds = time.perf_counter() - start
    start = time.perf_counter(); probabilities = model.predict_proba(X_test); predict_seconds = time.perf_counter() - start; pred = model.classes_[np.argmax(probabilities, axis=1)]
    report = pd.DataFrame(classification_report(y_test, pred, labels=classes, output_dict=True, zero_division=0)).T
    report.to_csv(out_dir / f"classification_report_{name}.csv", encoding="utf-8-sig")
    pd.DataFrame(confusion_matrix(y_test, pred, labels=classes), index=classes, columns=classes).to_csv(out_dir / f"confusion_matrix_{name}.csv", encoding="utf-8-sig")
    frame = pd.DataFrame({"row_id": np.arange(len(y_test)), "y_true": y_test, "y_pred": pred})
    for i, label in enumerate(classes): frame[f"proba__{label}"] = probabilities[:, i]
    frame.to_csv(out_dir / f"predictions_{name}.csv", index=False, encoding="utf-8-sig")
    rows = {"model": name, "accuracy": accuracy_score(y_test, pred), "balanced_accuracy": balanced_accuracy_score(y_test, pred), "macro_f1": f1_score(y_test, pred, labels=classes, average="macro", zero_division=0), "train_seconds": train_seconds, "predict_seconds": predict_seconds, "test_samples": len(y_test), **calibration_errors(y_test, probabilities, class_labels=classes)}
    return rows


def run(dataset, raw_dir: Path, output_dir: Path, k=60, n_estimators=100, min_samples_leaf=2, seed=42):
    output_dir.mkdir(parents=True, exist_ok=True)
    loader = load_nsl if dataset == "NSL-KDD" else load_unsw
    X_train, y_train, X_test, y_test, files = loader(raw_dir)
    train_idx, valid_idx = make_train_validation_split(y_train, seed=seed)
    scaler = MinMaxScaler(); X_train = scaler.fit_transform(X_train); X_test = scaler.transform(X_test)
    X_fit, X_valid = X_train[train_idx], X_train[valid_idx]; y_fit, y_valid = y_train[train_idx], y_train[valid_idx]
    encoder = LabelEncoder().fit(y_fit); y_fit_enc, y_valid_enc = encoder.transform(y_fit), encoder.transform(y_valid); classes = encoder.classes_
    scores, _ = chi2(X_fit, y_fit_enc); idx = np.argsort(-np.nan_to_num(scores, nan=0.0))[: min(k, X_fit.shape[1])]
    X_test_sel = X_test[:, idx]; X_fit_sel, X_valid_sel = X_fit[:, idx], X_valid[:, idx]
    models = {
        "equal_rf_chi2": RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf, class_weight="balanced_subsample", n_jobs=-1, random_state=seed),
        "extra_trees_chi2": ExtraTreesClassifier(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf, class_weight="balanced", n_jobs=-1, random_state=seed),
        "drc_forest_chi2": DRCForest(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf, n_jobs=-1, random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0),
    }
    rows = []
    for name, model in models.items():
        if name == "drc_forest_chi2":
            rows.append(_fit_one(name, model, X_fit_sel, y_fit, X_valid_sel, y_valid, X_test_sel, y_test, classes, output_dir))
        else:
            rows.append(_fit_one(name, model, X_fit_sel, y_fit, X_valid_sel, y_valid, X_test_sel, y_test, classes, output_dir))
    pd.DataFrame(rows).to_csv(output_dir / "metrics.csv", index=False, encoding="utf-8-sig")
    protocol = {"dataset": dataset, "cross_dataset_transfer": False, "official_train_test_boundary": True, "native_labels": native_label_summary(y_train), "train_rows": len(y_train), "test_rows": len(y_test), "chi2_k": k, "n_estimators": n_estimators, "min_samples_leaf": min_samples_leaf, "seed": seed, "files": [file_hash(p) for p in files]}
    (output_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--dataset", choices=["NSL-KDD", "UNSW-NB15"], required=True); parser.add_argument("--raw-dir", type=Path, required=True); parser.add_argument("--output-dir", type=Path, required=True); parser.add_argument("--chi2-k", type=int, default=60); parser.add_argument("--n-estimators", type=int, default=100); parser.add_argument("--min-samples-leaf", type=int, default=2); parser.add_argument("--seed", type=int, default=42); args = parser.parse_args(); run(args.dataset, args.raw_dir, args.output_dir, args.chi2_k, args.n_estimators, args.min_samples_leaf, args.seed)


if __name__ == "__main__": main()
