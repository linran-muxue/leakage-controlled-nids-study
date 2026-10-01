"""Leave-one-day-out temporal holdout on CIC-IDS2017.

The manuscript states that no time-separated holdout on a common testbed exists
in these corpora.  CIC-IDS2017 does carry the capture day in its file names, so
a day-level split is constructible; this script builds it.

For each held-out day: the training pool is every other day (per-class cap
20,000, stratified 85/15 train/validation), and the test set is the held-out day
itself, capped at 20,000 per class to bound the run.  Three arms are trained per
fold and seed: conditional weighting, the equal-weight chi-square forest and the
equal-weight full-feature forest.
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from src.feature_selection import chi2_top_k
from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def load(folder: Path):
    frames, provenance = [], []
    for name in ("train", "validation", "test"):
        frames.append(pd.read_csv(folder / f"{name}.csv", low_memory=False))
        provenance.append(pd.read_csv(folder / f"{name}_source_provenance.csv"))
    features = pd.concat(frames, ignore_index=True)
    source = pd.concat(provenance, ignore_index=True)
    assert len(features) == len(source), (len(features), len(source))
    X = features.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(dtype=np.float32)
    y = features["target"].to_numpy()
    files = source["_source_file"].astype(str).to_numpy()
    return X, y, files


def day_of(name: str) -> str:
    for day in DAYS:
        if name.startswith(day):
            return day
    return "Other"


def cap_per_class(indices: np.ndarray, y: np.ndarray, cap: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    picked = []
    for label in np.unique(y[indices]):
        rows = indices[y[indices] == label]
        if len(rows) > cap:
            rows = rng.choice(rows, size=cap, replace=False)
        picked.append(rows)
    return np.sort(np.concatenate(picked))


def metrics(y_true, y_pred, proba, classes, labels) -> dict:
    # a held-out day can lack a class in its training pool, so align the
    # probability columns to the full label set instead of indexing directly
    p = np.full((len(y_true), len(labels)), 1e-12)
    for index, label in enumerate(classes):
        if label in labels:
            p[:, list(labels).index(label)] = proba[:, index]
    index = np.array([list(labels).index(value) for value in y_true])
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", labels=labels,
                                   zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "log_loss": float(log_loss(index, p, labels=np.arange(len(labels)))),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v4_full")
    ap.add_argument("--output-dir", default="results_day_holdout_v1")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407, 7, 13])
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--train-cap", type=int, default=20_000)
    ap.add_argument("--test-cap", type=int, default=20_000)
    args = ap.parse_args()

    folder = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    (out / "predictions").mkdir(parents=True, exist_ok=True)
    X, y, files = load(folder)
    labels = np.unique(y)
    days = np.array([day_of(name) for name in files])
    print(f"rows {len(X):,}; day counts "
          f"{ {day: int((days == day).sum()) for day in DAYS} }", flush=True)

    rows = []
    for seed in args.seeds:
        for day in DAYS:
            started = time.time()
            pool = np.flatnonzero(days != day)
            test = cap_per_class(np.flatnonzero(days == day), y, args.test_cap, seed)
            uncapped_test = int((days == day).sum())
            pool = cap_per_class(pool, y, args.train_cap, seed)
            train_idx, val_idx = train_test_split(
                pool, test_size=0.15, stratify=y[pool], random_state=seed)
            X_train, y_train = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]
            X_test, y_test = X[test], y[test]

            model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                               cv=5, random_state=seed)
            start = time.perf_counter()
            model.fit(X_train, y_train, X_val, y_val)
            train_seconds = time.perf_counter() - start
            proba = model.predict_proba(X_test)
            pred = model.classes_[proba.argmax(axis=1)]
            entry = {"seed": seed, "day": day, "model": "rccf",
                     "train_rows": len(X_train), "validation_rows": len(X_val),
                     "test_rows": len(X_test), "test_rows_uncapped": uncapped_test,
                     "train_seconds": train_seconds, "fit_seconds": time.time() - started,
                     **metrics(y_test, pred, proba, model.classes_, labels)}
            rows.append(entry)
            rccf_pred, rccf_proba = pred, proba
            print(f"seed {seed} hold out {day}: rccf macro-F1 {entry['macro_f1']:.6f} "
                  f"({time.time() - started:.0f}s)", flush=True)

            scaler = MinMaxScaler().fit(X_train)
            X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)
            selection = chi2_top_k(X_train_s, y_train, args.feature_k)
            views = {
                "equal_rf_chi2": (selection.select(X_train_s), selection.select(X_test_s),
                                  RandomForestClassifier(
                                      n_estimators=args.n_estimators, min_samples_leaf=2,
                                      n_jobs=-1, class_weight="balanced_subsample",
                                      random_state=seed)),
                "equal_rf_all": (X_train_s, X_test_s, RandomForestClassifier(
                    n_estimators=args.n_estimators, min_samples_leaf=2, n_jobs=-1,
                    class_weight="balanced_subsample", random_state=seed)),
            }
            for name, (Xa, Xb, classifier) in views.items():
                classifier.fit(Xa, y_train)
                probability = classifier.predict_proba(Xb)
                prediction = classifier.classes_[probability.argmax(axis=1)]
                rows.append({"seed": seed, "day": day, "model": name,
                             "train_rows": len(X_train), "validation_rows": len(X_val),
                             "test_rows": len(X_test), "test_rows_uncapped": uncapped_test,
                             **metrics(y_test, prediction, probability,
                                       classifier.classes_, labels)})
                if name == "equal_rf_chi2" and seed == args.seeds[0]:
                    frame = pd.DataFrame({
                        "true_label": y_test, "rccf_pred": rccf_pred,
                        "equal_chi2_pred": prediction,
                        "rccf_max_prob": rccf_proba.max(axis=1),
                        "equal_chi2_max_prob": probability.max(axis=1),
                    })
                    frame.to_csv(out / "predictions" / f"holdout_{day}_seed{seed}.csv",
                                 index=False, encoding="utf-8-sig")
            print(f"  {day} arms done", flush=True)

    metrics_frame = pd.DataFrame(rows)
    metrics_frame.to_csv(out / "day_holdout_metrics.csv", index=False,
                         encoding="utf-8-sig")
    summary: dict[str, dict] = {}
    for (day, model), group in metrics_frame.groupby(["day", "model"]):
        summary.setdefault(day, {})[model] = {
            "seeds": int(len(group)),
            "macro_f1_mean": float(group["macro_f1"].mean()),
            "macro_f1_sd": float(group["macro_f1"].std(ddof=1)) if len(group) > 1 else 0.0,
            "test_rows": int(group["test_rows"].iloc[0]),
            "test_rows_uncapped": int(group["test_rows_uncapped"].iloc[0]),
        }
    for day in summary:
        rccf = summary[day]["rccf"]["macro_f1_mean"]
        chi2 = summary[day]["equal_rf_chi2"]["macro_f1_mean"]
        summary[day]["rccf_minus_equal_chi2"] = rccf - chi2
    (out / "day_holdout_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
