"""Resource profile for the primary comparison (self-check item D7).

The manuscript argues a cost-benefit trade-off but only reported time. This script
measures peak process memory, serialised model size and prediction throughput for the
conditional mechanism and the equal-weight control under the locked protocol.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd
import psutil
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import MinMaxScaler

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def rss_mb() -> float:
    return psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_resources_v5")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")

    rows = []
    baseline_rss = rss_mb()

    # ---------------- conditional mechanism ---------------------------------
    peak0 = rss_mb()
    model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                       cv=5, random_state=args.seed, n_jobs=-1)
    model.fit(Xtr, ytr, Xva, yva)
    peak_rccf = rss_mb()
    path = out / "model_rccf.joblib"
    joblib.dump(model, path, compress=3)
    size_rccf = path.stat().st_size / 1024 ** 2
    for batch in (1, 64, 1024, len(Xte)):
        X = Xte[:batch]
        start = time.perf_counter()
        model.predict_proba(X)
        elapsed = time.perf_counter() - start
        rows.append({"model": "rccf", "batch_size": batch, "seconds": elapsed,
                     "rows_per_second": batch / elapsed,
                     "peak_rss_mb": peak_rccf - baseline_rss,
                     "model_size_mb": size_rccf})
    del model

    # ---------------- equal-weight control ----------------------------------
    scaler = MinMaxScaler().fit(Xtr)
    Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
    selector = SelectKBest(chi2, k=args.feature_k).fit(Xtr_s, ytr)
    baseline = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=2,
                                      class_weight="balanced_subsample", n_jobs=-1,
                                      random_state=args.seed)
    baseline.fit(selector.transform(Xtr_s), ytr)
    peak_rf = rss_mb()
    path = out / "model_equal_rf_chi2.joblib"
    joblib.dump(baseline, path, compress=3)
    size_rf = path.stat().st_size / 1024 ** 2
    for batch in (1, 64, 1024, len(Xte)):
        X = selector.transform(Xte_s[:batch])
        start = time.perf_counter()
        baseline.predict_proba(X)
        elapsed = time.perf_counter() - start
        rows.append({"model": "equal_rf_chi2", "batch_size": batch, "seconds": elapsed,
                     "rows_per_second": batch / elapsed,
                     "peak_rss_mb": peak_rf - baseline_rss,
                     "model_size_mb": size_rf})

    df = pd.DataFrame(rows)
    df.to_csv(out / "resource_profile.csv", index=False, encoding="utf-8-sig")
    summary = (df[df.batch_size == len(Xte)]
               .set_index("model")[["rows_per_second", "peak_rss_mb", "model_size_mb"]]
               .round(2).to_dict(orient="index"))
    (out / "resource_profile_summary.json").write_text(json.dumps({
        "protocol": "natural-prior population, single seed, whole test batch",
        "test_rows": int(len(Xte)),
        "summary": summary,
        "note": "peak_rss_mb is the increment over the interpreter baseline after fitting; "
                "throughput is a single-machine measurement",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(df.round(3).to_string(index=False))
    print()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
