"""Quantify the effect of UNSW-NB15 train/test feature-key overlap.

The three protocols keep the published files and model configuration fixed:
official split, remove overlapping rows from the test side only, and remove
overlapping rows from both sides.  All preprocessing is fitted on the
protocol-specific training rows.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import brier_score_loss

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_unsw_nb15_independent_v1 import file_hash, load_native
from src.additional_metrics import calibration_errors


def normalize_key_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Create deterministic comparable keys while excluding identifiers."""
    out = pd.DataFrame(index=frame.index)
    for col in columns:
        series = frame[col]
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().all():
            out[col] = numeric.astype("float64").round(12).map(lambda value: format(value, ".12g"))
        else:
            out[col] = series.fillna("<NA>").astype(str).str.strip()
    return out


def build_overlap_masks(
    train_norm: pd.DataFrame,
    test_norm: pd.DataFrame,
    train_labels: pd.Series | np.ndarray,
    test_labels: pd.Series | np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return train/test overlap masks and key-level audit statistics."""
    train_keys = train_norm.astype(str).agg("\x1f".join, axis=1)
    test_keys = test_norm.astype(str).agg("\x1f".join, axis=1)
    train_map: dict[str, list[int]] = {}
    test_map: dict[str, list[int]] = {}
    for idx, key in enumerate(train_keys.tolist()):
        train_map.setdefault(key, []).append(idx)
    for idx, key in enumerate(test_keys.tolist()):
        test_map.setdefault(key, []).append(idx)
    common = set(train_map).intersection(test_map)
    train_mask = train_keys.isin(common).to_numpy()
    test_mask = test_keys.isin(common).to_numpy()
    train_labels = np.asarray(train_labels).astype(str)
    test_labels = np.asarray(test_labels).astype(str)
    same_label_keys = 0
    conflict_label_keys = 0
    same_label_pairs = 0
    conflict_label_pairs = 0
    for key in common:
        for train_idx in train_map[key]:
            for test_idx in test_map[key]:
                if train_labels[train_idx] == test_labels[test_idx]:
                    same_label_pairs += 1
                else:
                    conflict_label_pairs += 1
        train_set = set(train_labels[train_map[key]])
        test_set = set(test_labels[test_map[key]])
        if train_set == test_set and len(train_set) == 1:
            same_label_keys += 1
        else:
            conflict_label_keys += 1
    stats = {
        "common_keys": int(len(common)),
        "matched_train_rows": int(train_mask.sum()),
        "matched_test_rows": int(test_mask.sum()),
        "same_label_keys": int(same_label_keys),
        "conflict_label_keys": int(conflict_label_keys),
        "same_label_pairs": int(same_label_pairs),
        "conflict_label_pairs": int(conflict_label_pairs),
        "test_matched_fraction": float(test_mask.mean()) if len(test_mask) else 0.0,
    }
    return train_mask, test_mask, stats


def metrics(y_true: np.ndarray, pred: np.ndarray, proba: np.ndarray, classes: np.ndarray) -> dict:
    proba = np.clip(proba, 1e-15, 1.0)
    proba = proba / proba.sum(axis=1, keepdims=True)
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y_true, proba, labels=classes)),
        "brier_macro": float(np.mean([brier_score_loss((y_true == c).astype(int), proba[:, i]) for i, c in enumerate(classes)])),
        "ece": float(calibration_errors(y_true, proba, class_labels=classes)["ece"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--k", type=int, default=60)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--min-samples-leaf", type=int, default=2)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_path = args.raw_dir / "UNSW-NB15_training-set.csv"
    test_path = args.raw_dir / "UNSW-NB15_testing-set.csv"
    train_raw = pd.read_csv(train_path, low_memory=False)
    test_raw = pd.read_csv(test_path, low_memory=False)
    label_col = "attack_cat" if "attack_cat" in train_raw.columns else "label"
    key_columns = [c for c in train_raw.columns if c in test_raw.columns and c not in {"id", "label", label_col}]
    train_norm = normalize_key_frame(train_raw, key_columns)
    test_norm = normalize_key_frame(test_raw, key_columns)
    train_overlap, test_overlap, overlap_stats = build_overlap_masks(
        train_norm, test_norm, train_raw[label_col], test_raw[label_col]
    )
    x_train, y_train, x_test, y_test = load_native(args.raw_dir)
    classes = np.asarray(sorted(set(y_train.tolist()) | set(y_test.tolist())))
    protocols = {
        "official_split": (np.ones(len(y_train), dtype=bool), np.ones(len(y_test), dtype=bool)),
        "remove_test_overlap": (np.ones(len(y_train), dtype=bool), ~test_overlap),
        "remove_both_overlap": (~train_overlap, ~test_overlap),
    }
    rows: list[dict] = []
    for protocol, (train_keep, test_keep) in protocols.items():
        for seed in args.seeds:
            xtr = x_train[train_keep]
            xte = x_test[test_keep]
            ytr = y_train[train_keep]
            yte = y_test[test_keep]
            scaler = MinMaxScaler()
            xtr_s = scaler.fit_transform(xtr)
            xte_s = scaler.transform(xte)
            scores, _ = chi2(xtr_s, pd.factorize(ytr)[0])
            selected = np.argsort(-np.nan_to_num(scores, nan=0.0))[: min(args.k, xtr_s.shape[1])]
            model = RandomForestClassifier(
                n_estimators=args.n_estimators,
                min_samples_leaf=args.min_samples_leaf,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=seed,
            )
            start = time.perf_counter()
            model.fit(xtr_s[:, selected], ytr)
            train_seconds = time.perf_counter() - start
            start = time.perf_counter()
            pred = model.predict(xte_s[:, selected])
            proba = model.predict_proba(xte_s[:, selected])
            predict_seconds = time.perf_counter() - start
            row = metrics(yte, pred, proba, classes)
            row.update({
                "protocol": protocol,
                "seed": seed,
                "train_rows": int(len(ytr)),
                "test_rows": int(len(yte)),
                "removed_train_rows": int((~train_keep).sum()),
                "removed_test_rows": int((~test_keep).sum()),
                "feature_count": int(len(selected)),
                "n_estimators": args.n_estimators,
                "min_samples_leaf": args.min_samples_leaf,
                "train_seconds": train_seconds,
                "predict_seconds": predict_seconds,
            })
            rows.append(row)
            pd.DataFrame({"y_true": yte, "y_pred": pred, **{f"proba_{c}": proba[:, i] for i, c in enumerate(model.classes_)}}).to_csv(
                args.output_dir / f"predictions_{protocol}_seed{seed}.csv", index=False, encoding="utf-8-sig"
            )

    metrics_frame = pd.DataFrame(rows)
    metrics_frame.to_csv(args.output_dir / "metrics.csv", index=False, encoding="utf-8-sig")
    aggregate = metrics_frame.groupby("protocol").agg({
        "accuracy": ["mean", "std"],
        "balanced_accuracy": ["mean", "std"],
        "macro_f1": ["mean", "std"],
        "log_loss": ["mean", "std"],
        "brier_macro": ["mean", "std"],
        "ece": ["mean", "std"],
    })
    aggregate.to_csv(args.output_dir / "metrics_aggregate.csv", encoding="utf-8-sig")
    protocol = {
        "dataset": "UNSW-NB15",
        "protocols": list(protocols),
        "overlap_audit": overlap_stats,
        "key_columns_count": len(key_columns),
        "excluded_columns": ["id", "label", label_col],
        "seeds": args.seeds,
        "k": args.k,
        "n_estimators": args.n_estimators,
        "min_samples_leaf": args.min_samples_leaf,
        "train_file_sha256": file_hash(train_path)["sha256"],
        "test_file_sha256": file_hash(test_path)["sha256"],
        "preprocessing": "MinMaxScaler and chi2 fitted independently on each protocol's retained training rows",
    }
    (args.output_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    print(metrics_frame.to_string(index=False))


if __name__ == "__main__":
    main()
