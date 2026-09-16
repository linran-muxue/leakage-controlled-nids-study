"""Extended robustness: label noise, missing features and feature-offset drift.

Complements the existing shared-perturbation experiment (Gaussian noise and feature
masking) with three further failure modes that a reviewer would expect for a data-quality
paper: corrupted supervision, missing measurements and calibration drift.
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
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import f1_score
from sklearn.preprocessing import MinMaxScaler

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def is_attack(y) -> np.ndarray:
    return (y != "Normal")


def per_class_recall(y, pred) -> dict:
    out = {}
    for label in LABELS:
        mask = y == label
        if mask.sum():
            out[label] = float((pred[mask] == label).mean())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_robustness_extended_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--noise-levels", nargs="+", type=float, default=[0.05, 0.10])
    ap.add_argument("--missing-fraction", type=float, default=0.10)
    ap.add_argument("--drift-fraction", type=float, default=0.20)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")
    rng = np.random.default_rng(0)

    # test-time perturbations (no retraining required)
    col_median = np.median(Xtr, axis=0)
    X_missing = Xte.copy()
    mask = rng.random(X_missing.shape) < args.missing_fraction
    X_missing[mask] = np.take(col_median, np.where(mask)[1])
    span = Xtr.max(axis=0) - Xtr.min(axis=0)
    drift_cols = rng.random(Xte.shape[1]) < args.drift_fraction
    X_drift = Xte + drift_cols * (0.01 * span)

    rows = []
    for seed in args.seeds:
        # ---------------- conditional mechanism ---------------------------------
        model = RCCFForest(n_estimators=100, feature_k=60, cv=5, random_state=seed, n_jobs=-1)
        model.fit(Xtr, ytr, Xva, yva)
        for name, X in (("clean", Xte), ("missing_10pct", X_missing), ("offset_drift", X_drift)):
            pred = model.classes_[np.argmax(model.predict_proba(X), axis=1)]
            rows.append({"model": "rccf", "seed": seed, "condition": name,
                         "macro_f1": macro_f1(yte, pred),
                         **{f"recall_{k}": v for k, v in per_class_recall(yte, pred).items()}})
        # ---------------- equal-weight control ----------------------------------
        scaler = MinMaxScaler().fit(Xtr)
        selector = SelectKBest(chi2, k=60).fit(scaler.transform(Xtr), ytr)
        baseline = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, n_jobs=-1,
                                          class_weight="balanced_subsample",
                                          random_state=seed).fit(
            selector.transform(scaler.transform(Xtr)), ytr)
        for name, X in (("clean", Xte), ("missing_10pct", X_missing), ("offset_drift", X_drift)):
            pred = baseline.classes_[np.argmax(baseline.predict_proba(
                selector.transform(scaler.transform(X))), axis=1)]
            rows.append({"model": "equal_rf_chi2", "seed": seed, "condition": name,
                         "macro_f1": macro_f1(yte, pred),
                         **{f"recall_{k}": v for k, v in per_class_recall(yte, pred).items()}})

        # ---------------- label noise (retraining required) ---------------------
        for level in args.noise_levels:
            noisy = ytr.copy()
            flip = rng.random(len(noisy)) < level
            alternatives = rng.choice(np.unique(ytr), size=int(flip.sum()))
            noisy[flip] = alternatives
            start = time.perf_counter()
            rccf = RCCFForest(n_estimators=100, feature_k=60, cv=5, random_state=seed, n_jobs=-1)
            rccf.fit(Xtr, noisy, Xva, yva)
            pred = rccf.classes_[np.argmax(rccf.predict_proba(Xte), axis=1)]
            rows.append({"model": "rccf", "seed": seed,
                         "condition": f"label_noise_{int(level * 100)}pct",
                         "macro_f1": macro_f1(yte, pred), "train_seconds": time.perf_counter() - start,
                         **{f"recall_{k}": v for k, v in per_class_recall(yte, pred).items()}})
            rf = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, n_jobs=-1,
                                        class_weight="balanced_subsample",
                                        random_state=seed).fit(
                selector.transform(scaler.transform(Xtr)), noisy)
            pred = rf.classes_[np.argmax(rf.predict_proba(selector.transform(scaler.transform(Xte))), axis=1)]
            rows.append({"model": "equal_rf_chi2", "seed": seed,
                         "condition": f"label_noise_{int(level * 100)}pct",
                         "macro_f1": macro_f1(yte, pred),
                         **{f"recall_{k}": v for k, v in per_class_recall(yte, pred).items()}})
        pd.DataFrame(rows).to_csv(out / "robustness_extended_by_seed.csv",
                                  index=False, encoding="utf-8-sig")
        print(f"seed={seed} done", flush=True)

    df = pd.DataFrame(rows)
    summary = (df.groupby(["model", "condition"])["macro_f1"].agg(["mean", "std"])
               .round(6).reset_index())
    clean = summary[summary.condition == "clean"].set_index("model")["mean"]
    summary["relative_drop_pct"] = summary.apply(
        lambda r: 100 * (1 - r["mean"] / clean[r["model"]]) if r["condition"] != "clean" else 0.0,
        axis=1).round(3)
    summary.to_csv(out / "robustness_extended_summary.csv", index=False, encoding="utf-8-sig")
    (out / "robustness_extended_summary.json").write_text(json.dumps({
        "protocol": "natural-prior population; test-time perturbations plus retraining under label noise",
        "seeds": args.seeds,
        "missing_fraction": args.missing_fraction,
        "drift_fraction_of_features": args.drift_fraction,
        "drift_magnitude": "1% of the training range added to the selected features",
        "summary": summary.to_dict(orient="records"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
