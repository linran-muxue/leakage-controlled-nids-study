from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.audit_utils import assert_no_feature_overlap, validate_split_schema
from src.experiment_components import WeightedRandomForest, compute_metrics


def choose_best_config(rows):
    if not rows:
        raise ValueError("empty configuration table")
    return sorted(rows, key=lambda r: (-r["cv_macro_f1"], -r["cv_accuracy"], r["complexity"], r["config_id"]))[0]


def select_features_train(X, y, k):
    scores, _ = chi2(np.asarray(X, dtype=float), np.asarray(y))
    order = np.argsort(-np.nan_to_num(scores, nan=0.0))
    return order[:k]


def load_data(processed):
    frames = {s: pd.read_csv(processed / f"{s}.csv", low_memory=False) for s in ["train", "validation", "test"]}
    validate_split_schema(frames["train"], frames["validation"], frames["test"])
    assert_no_feature_overlap(frames["train"], frames["validation"], frames["test"])
    names = [c for c in frames["train"].columns if c != "target"]
    # Return raw numeric features. Scaling is fitted inside each CV fold in
    # cv_rf(), and is fitted once on the complete training set only for the
    # final untouched-test evaluation.
    Xtr = frames["train"][names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    Xv = frames["validation"][names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    Xte = frames["test"][names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    return Xtr, frames["train"]["target"].to_numpy(), Xv, frames["validation"]["target"].to_numpy(), Xte, frames["test"]["target"].to_numpy(), names


def cv_rf(X, y, k, n_estimators, max_depth, min_samples_leaf, seed):
    fold_scores, fold_acc = [], []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for train_idx, valid_idx in skf.split(X, y):
        scaler = MinMaxScaler()
        X_fit = scaler.fit_transform(X[train_idx])
        X_valid = scaler.transform(X[valid_idx])
        idx = select_features_train(X_fit, y[train_idx], k)
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, min_samples_leaf=min_samples_leaf, random_state=seed, n_jobs=-1, class_weight="balanced_subsample")
        model.fit(X_fit[:, idx], y[train_idx])
        pred = model.predict(X_valid[:, idx])
        fold_scores.append(f1_score(y[valid_idx], pred, average="macro", zero_division=0))
        fold_acc.append(accuracy_score(y[valid_idx], pred))
    return float(np.mean(fold_scores)), float(np.mean(fold_acc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, default=Path(r"E:\论文\data\processed_dedup"))
    ap.add_argument("--output-dir", type=Path, default=Path("results_journal_upgrade"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    Xtr, ytr, Xv, yv, Xte, yte, names = load_data(args.processed_dir)
    configs = []
    for k in [20, 40, 60]:
        for trees in [100, 200, 300]:
            for depth in [None, 20]:
                for leaf in [1, 2]:
                    f1, acc = cv_rf(Xtr, ytr, k, trees, depth, leaf, args.seed)
                    complexity = trees * (1 if depth is None else depth) * leaf
                    configs.append({"config_id": f"rf_k{k}_trees{trees}_depth{depth}_leaf{leaf}", "k": k, "n_estimators": trees, "max_depth": depth, "min_samples_leaf": leaf, "cv_macro_f1": f1, "cv_accuracy": acc, "complexity": complexity})
    table = pd.DataFrame(configs)
    table.to_csv(args.output_dir / "cv_hyperparameter_results.csv", index=False, encoding="utf-8-sig")
    best = choose_best_config(configs)
    (args.output_dir / "selected_hyperparameters.json").write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")

    final_scaler = MinMaxScaler()
    Xtr_scaled = final_scaler.fit_transform(Xtr)
    Xte_scaled = final_scaler.transform(Xte)
    idx = select_features_train(Xtr_scaled, ytr, best["k"])
    final_rows = []
    for seed in [42, 2024, 3407]:
        start = time.perf_counter()
        rf = RandomForestClassifier(n_estimators=best["n_estimators"], max_depth=best["max_depth"], min_samples_leaf=best["min_samples_leaf"], random_state=seed, n_jobs=-1, class_weight="balanced_subsample")
        rf.fit(Xtr_scaled[:, idx], ytr)
        train_s = time.perf_counter() - start
        start = time.perf_counter(); pred = rf.predict(Xte_scaled[:, idx]); pred_s = time.perf_counter() - start
        m = compute_metrics(yte, pred); m.update({"model":"tuned_random_forest_chi2", "seed":seed, "k":best["k"], "n_estimators":best["n_estimators"], "max_depth":best["max_depth"], "min_samples_leaf":best["min_samples_leaf"], "train_seconds":train_s, "predict_seconds":pred_s, "test_samples":len(yte)})
        final_rows.append(m)
    pd.DataFrame(final_rows).to_csv(args.output_dir / "tuned_test_metrics.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(best, ensure_ascii=False))
    print(pd.DataFrame(final_rows).to_string(index=False))


if __name__ == "__main__":
    main()
