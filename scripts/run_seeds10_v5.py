"""Extend the primary experiment from 3 to 10 seeds (self-check items D9/D10/D11).

The data split is fixed; only the model random seed varies, matching the locked
protocol. Four arms are produced with the same naming convention as the 3-seed run so
that existing analysis scripts can consume them unchanged:

  rccf                    conditional weighting (Risk-Calibrated Conformal Forest)
  equal_rf_all            equal-weight random forest, all features
  equal_rf_chi2           equal-weight random forest, chi-square top-k
  extra_trees_chi2        extremely randomised trees, chi-square top-k
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
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import MinMaxScaler

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def ece(y, proba, classes) -> float:
    order = [list(classes).index(label) for label in LABELS]
    p = proba[:, order]
    y_idx = np.array([list(LABELS).index(v) for v in y])
    conf = p.max(axis=1)
    correct = (p.argmax(axis=1) == y_idx).astype(float)
    value = 0.0
    for lo in np.linspace(0.0, 0.9, 10):
        mask = (conf >= lo) & (conf < lo + 0.1)
        if mask.sum() > 0:
            value += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return float(value)


def write_predictions(path: Path, y_true, pred, proba, classes):
    frame = pd.DataFrame({
        "row_id": np.arange(len(y_true)), "true_label": y_true, "predicted_label": pred,
        **{f"prob_{c}": proba[:, i] for i, c in enumerate(classes)},
    })
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def metric_row(model: str, seed: int, y, pred, proba, classes, train_s: float, predict_s: float):
    y_idx = np.array([list(LABELS).index(v) for v in y])
    order = [list(classes).index(label) for label in LABELS]
    p = proba[:, order]
    return {
        "model": model, "seed": seed,
        "macro_f1": macro_f1(y, pred),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "log_loss": float(log_loss(y_idx, p, labels=np.arange(len(LABELS)))),
        "ece": ece(y, proba, classes),
        "train_seconds": train_s, "predict_seconds": predict_s,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_seeds10_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--skip-rccf", action="store_true")
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    (out / "predictions").mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")
    rows = []

    for seed in args.seeds:
        # ---- conditional weighting -----------------------------------------
        if not args.skip_rccf:
            start = time.perf_counter()
            model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                               cv=5, random_state=seed, n_jobs=-1)
            model.fit(Xtr, ytr, Xva, yva)
            train_s = time.perf_counter() - start
            start = time.perf_counter()
            proba = model.predict_proba(Xte)
            pred = model.classes_[np.argmax(proba, axis=1)]
            predict_s = time.perf_counter() - start
            write_predictions(out / f"predictions_seed{seed}.csv", yte, pred, proba, model.classes_)
            rows.append(metric_row("rccf", seed, yte, pred, proba, model.classes_, train_s, predict_s))
            print(f"seed={seed} rccf macro_f1={rows[-1]['macro_f1']:.6f}", flush=True)

        # ---- equal-weight controls -----------------------------------------
        scaler = MinMaxScaler().fit(Xtr)
        Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
        selector = SelectKBest(chi2, k=args.feature_k).fit(Xtr_s, ytr)
        views = {
            "equal_rf_all": (Xtr_s, Xte_s,
                             RandomForestClassifier(n_estimators=args.n_estimators,
                                                    min_samples_leaf=2, n_jobs=-1,
                                                    class_weight="balanced_subsample",
                                                    random_state=seed)),
            "equal_rf_chi2": (selector.transform(Xtr_s), selector.transform(Xte_s),
                              RandomForestClassifier(n_estimators=args.n_estimators,
                                                     min_samples_leaf=2, n_jobs=-1,
                                                     class_weight="balanced_subsample",
                                                     random_state=seed)),
            "extra_trees_chi2": (selector.transform(Xtr_s), selector.transform(Xte_s),
                                 ExtraTreesClassifier(n_estimators=args.n_estimators,
                                                      min_samples_leaf=2, n_jobs=-1,
                                                      class_weight="balanced",
                                                      random_state=seed)),
        }
        for name, (Xa, Xb, clf) in views.items():
            start = time.perf_counter()
            clf.fit(Xa, ytr)
            train_s = time.perf_counter() - start
            start = time.perf_counter()
            proba = clf.predict_proba(Xb)
            classes = clf.classes_
            pred = classes[np.argmax(proba, axis=1)]
            predict_s = time.perf_counter() - start
            write_predictions(out / "predictions" / f"predictions_{name}_seed{seed}.csv",
                              yte, pred, proba, classes)
            rows.append(metric_row(name, seed, yte, pred, proba, classes, train_s, predict_s))
        print(f"seed={seed} baselines done", flush=True)
        pd.DataFrame(rows).to_csv(out / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")

    df = pd.DataFrame(rows)
    agg = (df.groupby("model")[["macro_f1", "accuracy", "balanced_accuracy", "log_loss", "ece",
                                "train_seconds", "predict_seconds"]]
           .agg(["mean", "std"]).round(6))
    agg.to_csv(out / "metrics_aggregate.csv", encoding="utf-8-sig")
    (out / "run_manifest.json").write_text(json.dumps({
        "purpose": "10-seed extension of the primary CIC comparison",
        "seeds": args.seeds, "n_seeds": len(args.seeds),
        "n_estimators": args.n_estimators, "feature_k": args.feature_k,
        "cv_for_rccf": 5,
        "protocol": "fixed stratified 70/15/15 split; seed-specific model fitting",
        "processed_dir": args.processed_dir,
        "test_rows": int(len(yte)),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(agg.to_string())


if __name__ == "__main__":
    main()
