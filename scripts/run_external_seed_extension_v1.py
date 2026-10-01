"""Extend the three external benchmarks from three to ten seeds.

The three-seed numbers were limited by the mutual-information expert, whose
k-nearest-neighbour estimator is very slow on 100k-row training sets.  This
extension keeps the same data, splits, forests and statistics but uses the three
cheap deterministic views (full / chi-square / ANOVA); the deviation is recorded
in the run manifest.  Each seed is written as soon as it finishes, so partial
progress survives.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype
from sklearn.model_selection import train_test_split

import src.rccf_forest as rccf
from scripts.run_native_label_benchmark_v1 import load, metrics, write_predictions

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load_nsl() -> tuple:
    root = ROOT / "data_external_nsl_kdd_processed_v2"
    X_train, y_train = load(root / "train.csv")
    X_test, y_test = load(root / "test.csv")
    return X_train, y_train, X_test, y_test


def load_unsw() -> tuple:
    root = ROOT / "data_external" / "UNSW-NB15"
    train = pd.read_csv(root / "UNSW-NB15_training-set.csv", low_memory=False)
    test = pd.read_csv(root / "UNSW-NB15_testing-set.csv", low_memory=False)
    label = "attack_cat" if "attack_cat" in train.columns else "label"
    drop = {"id", "label", "attack_cat"}
    names = [c for c in train.columns if c not in drop and c in test.columns]
    cats = [c for c in names if is_object_dtype(train[c]) or is_string_dtype(train[c])]
    a = pd.get_dummies(train[names], columns=cats, dummy_na=True)
    b = pd.get_dummies(test[names], columns=cats, dummy_na=True).reindex(columns=a.columns,
                                                                        fill_value=0)
    y_train = train[label].fillna("Normal").astype(str).str.strip().to_numpy()
    y_test = test[label].fillna("Normal").astype(str).str.strip().to_numpy()
    to_num = lambda f: f.apply(pd.to_numeric, errors="coerce").replace(
        [np.inf, -np.inf], np.nan).fillna(0).to_numpy(float)
    return to_num(a), y_train, to_num(b), y_test


def load_nbaiot() -> tuple:
    root = ROOT / "data_processed_nbaiot_v48"
    X_train, y_train = load(root / "train.csv")
    X_test, y_test = load(root / "test.csv")
    return X_train, y_train, X_test, y_test


LOADERS = {"nsl": load_nsl, "unsw": load_unsw, "nbaiot": load_nbaiot}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["nsl", "unsw", "nbaiot"],
                    choices=sorted(LOADERS))
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--experts", nargs="+", default=["full", "chi2", "anova"])
    args = ap.parse_args()

    # the four-view protocol includes the slow mutual-information expert; the
    # extension runs the three deterministic views and records the deviation
    rccf.RCCFForest.expert_names = tuple(args.experts)
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.ensemble import RandomForestClassifier
    from src.feature_selection import chi2_top_k

    for dataset in args.datasets:
        out = ROOT / f"results_rccf_{dataset}_v10"
        out.mkdir(parents=True, exist_ok=True)
        X_train, y_train, X_test, y_test = LOADERS[dataset]()
        labels = np.unique(y_train)
        rows = []
        print(f"== {dataset}: train {X_train.shape} test {X_test.shape} "
              f"classes {len(labels)}", flush=True)
        for seed in args.seeds:
            started = time.time()
            tr_idx, cal_idx = train_test_split(np.arange(len(y_train)), test_size=0.15,
                                               stratify=y_train, random_state=seed)
            model = rccf.RCCFForest(n_estimators=args.n_estimators,
                                    feature_k=args.feature_k, cv=5, random_state=seed)
            model.fit(X_train[tr_idx], y_train[tr_idx], X_train[cal_idx], y_train[cal_idx])
            probability = model.predict_proba(X_test)
            prediction = model.classes_[probability.argmax(axis=1)]
            write_predictions(out / f"predictions_rccf_seed{seed}.csv", y_test, prediction,
                              probability, model.classes_)
            entry = {"model": "rccf", "seed": seed, "train_seconds": time.time() - started,
                     **metrics(y_test, prediction, probability, model.classes_, labels)}
            probabilities = [model._expert_proba(expert, X_test)
                             for expert in model.experts_]
            equal = np.mean(probabilities, axis=0)
            equal_pred = model.classes_[equal.argmax(axis=1)]
            write_predictions(out / f"predictions_equal_fusion_seed{seed}.csv", y_test,
                              equal_pred, equal, model.classes_)
            entry["equal_fusion_macro_f1"] = float(
                __import__("sklearn.metrics", fromlist=["f1_score"]).f1_score(
                    y_test, equal_pred, average="macro", labels=labels, zero_division=0))
            entry["labels_changed_vs_equal"] = int((equal_pred != prediction).sum())
            rows.append(entry)
            pd.DataFrame(rows).to_csv(out / "metrics_by_seed.csv", index=False,
                                      encoding="utf-8-sig")
            print(f"seed {seed}: rccf {entry['macro_f1']:.6f} "
                  f"equal-fusion {entry['equal_fusion_macro_f1']:.6f} "
                  f"({entry['labels_changed_vs_equal']} labels differ, "
                  f"{time.time() - started:.0f}s)", flush=True)
        frame = pd.DataFrame(rows)
        aggregate = frame.groupby("model").agg(
            macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"),
            accuracy_mean=("accuracy", "mean"),
            balanced_accuracy_mean=("balanced_accuracy", "mean"),
            log_loss_mean=("log_loss", "mean"),
            test_samples_mean=("macro_f1", "size")).reset_index()
        aggregate.to_csv(out / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")
        manifest = {"dataset": dataset, "seeds": [int(s) for s in args.seeds],
                    "experts": list(args.experts),
                    "deviation_from_primary_protocol": (
                        "mutual-information expert omitted because its kNN estimator "
                        "does not scale to the 100k-row external training sets"),
                    "training_rows": int(len(X_train)), "test_rows": int(len(X_test)),
                    "calibration": "15% stratified split of the official training side"}
        (out / "run_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(aggregate.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
