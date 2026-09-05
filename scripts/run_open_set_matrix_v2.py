"""Evaluate several held-out unknown-attack combinations on CIC-IDS2017."""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import chi2

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_open_set_v1 import KNOWN, UNKNOWN_RAW, collect_raw
from src.open_set import reject_by_threshold


def unknown_combinations(labels: list[str]) -> list[list[str]]:
    return [list(c) for size in range(1, len(labels) + 1) for c in combinations(labels, size)]


def fpr_at_tpr(y_true: np.ndarray, scores: np.ndarray, target_tpr: float = 0.95) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    eligible = fpr[tpr >= target_tpr]
    return float(eligible[0]) if len(eligible) else 1.0


def precision_recall_summary(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    return float(average_precision_score(y_true, scores)), float(y_true[scores >= np.quantile(scores, 0.5)].mean())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-group", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=100)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    known, unknown = collect_raw(args.raw_dir, per_group=args.per_group, seed=args.seed)
    features = [c for c in known.columns if c not in {"target", "raw_label", "source_file"}]
    known_train, known_valid = train_test_split(known, test_size=0.2, stratify=known["target"], random_state=args.seed)
    known_train = known_train.reset_index(drop=True)
    known_valid = known_valid.reset_index(drop=True)
    scaler = MinMaxScaler()
    xtr = scaler.fit_transform(known_train[features].astype(float))
    xv = scaler.transform(known_valid[features].astype(float))
    scores, _ = chi2(xtr, pd.factorize(known_train["target"])[0])
    idx = np.argsort(-np.nan_to_num(scores, nan=0.0))[: min(60, xtr.shape[1])]
    clf = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=args.seed)
    clf.fit(xtr[:, idx], known_train["target"])
    valid_proba = clf.predict_proba(xv[:, idx])
    threshold = float(np.quantile(valid_proba.max(axis=1), 0.05))

    rows = []
    raw_order = sorted(UNKNOWN_RAW)
    for combo in unknown_combinations(raw_order):
        subset = unknown[unknown["raw_label"].isin(combo)].copy()
        xu = scaler.transform(subset[features].astype(float))
        unknown_proba = clf.predict_proba(xu[:, idx])
        y_true = np.concatenate([np.zeros(len(known_valid), dtype=int), np.ones(len(subset), dtype=int)])
        anomaly_score = np.concatenate([1.0 - valid_proba.max(axis=1), 1.0 - unknown_proba.max(axis=1)])
        pred_unknown = reject_by_threshold(unknown_proba, clf.classes_, threshold)
        unknown_recall = float((pred_unknown == "unknown").mean()) if len(pred_unknown) else float("nan")
        ap, median_recall = precision_recall_summary(y_true, anomaly_score)
        rows.append({
            "unknown_combination": "+".join(combo),
            "known_validation_samples": int(len(known_valid)),
            "unknown_samples": int(len(subset)),
            "threshold": threshold,
            "unknown_recall": unknown_recall,
            "unknown_auroc": float(roc_auc_score(y_true, anomaly_score)),
            "unknown_aupr": ap,
            "unknown_fpr_at_95_tpr": fpr_at_tpr(y_true, anomaly_score, 0.95),
            "coverage": float((len(known_valid) / (len(known_valid) + len(subset)))),
            "known_macro_f1": float(f1_score(known_valid["target"], clf.predict(xv[:, idx]), average="macro", zero_division=0)),
            "median_score_recall_diagnostic": median_recall,
        })
    result = pd.DataFrame(rows)
    result.to_csv(args.output_dir / "open_set_matrix_metrics.csv", index=False, encoding="utf-8-sig")
    protocol = {"known_labels": sorted(KNOWN), "unknown_combinations": unknown_combinations(raw_order), "unknown_used_for_training": False, "threshold_fit": "5th percentile of known validation confidence", "per_group_cap": args.per_group, "seed": args.seed, "n_estimators": args.n_estimators}
    (args.output_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
