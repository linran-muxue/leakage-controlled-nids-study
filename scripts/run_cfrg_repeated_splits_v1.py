"""Repeated stratified split comparison for CFRG and strong tree baselines."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cfrg_forest import CFRGForest


def run_repeated(processed_dir, output_dir, split_seeds=range(10), n_estimators=100, chi2_k=60):
    processed_dir, output_dir = Path(processed_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    path = processed_dir / "all.csv"
    if path.exists(): frame = pd.read_csv(path)
    else: frame = pd.concat([pd.read_csv(processed_dir / f"{s}.csv") for s in ["train", "validation", "test"]], ignore_index=True)
    features = [c for c in frame.columns if c != "target"]; Xraw = frame[features].to_numpy(float); y = frame.target.to_numpy(); rows = []
    for seed in [int(s) for s in split_seeds]:
        tr, te = train_test_split(np.arange(len(y)), test_size=.3, random_state=seed, stratify=y); scaler = MinMaxScaler().fit(Xraw[tr]); Xtr, Xte = scaler.transform(Xraw[tr]), scaler.transform(Xraw[te]); score, _ = chi2(Xtr, y[tr]); idx = np.argsort(-np.nan_to_num(score, nan=0.0))[: min(int(chi2_k), Xtr.shape[1])]
        models = {"equal_rf": RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, n_jobs=-1), "extra_trees": ExtraTreesClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced", random_state=seed, n_jobs=-1), "cfrg_forest": CFRGForest(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0, n_jobs=-1)}
        for name, model in models.items():
            start = time.perf_counter(); model.fit(Xtr[:, idx], y[tr]); train_s = time.perf_counter() - start; pred = model.predict(Xte[:, idx]); rows.append({"split_seed": seed, "model": name, "macro_f1": float(f1_score(y[te], pred, average="macro", zero_division=0)), "balanced_accuracy": float(balanced_accuracy_score(y[te], pred)), "train_seconds": train_s})
    result = pd.DataFrame(rows); result.to_csv(output_dir / "metrics.csv", index=False, encoding="utf-8-sig"); summary = result.groupby("model")[['macro_f1', 'balanced_accuracy', 'train_seconds']].agg(['mean', 'std', 'count']).reset_index(); summary.to_csv(output_dir / "summary.csv", index=False, encoding="utf-8-sig")
    wide = result.pivot(index="split_seed", columns="model", values="macro_f1"); diff = wide["cfrg_forest"] - wide["equal_rf"]; pd.DataFrame([{"metric": "macro_f1", "mean_delta_cfrg_minus_equal": float(diff.mean()), "std_delta": float(diff.std(ddof=1)), "positive_splits": int((diff > 0).sum()), "zero_splits": int((diff == 0).sum()), "negative_splits": int((diff < 0).sum())}]).to_csv(output_dir / "paired_split_tests.csv", index=False, encoding="utf-8-sig"); return result


def main():
    p = argparse.ArgumentParser(); p.add_argument("--processed-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--split-seeds", type=int, nargs="+", default=list(range(10))); p.add_argument("--n-estimators", type=int, default=100); p.add_argument("--chi2-k", type=int, default=60); args = p.parse_args(); run_repeated(args.processed_dir, args.output_dir, args.split_seeds, args.n_estimators, args.chi2_k)


if __name__ == "__main__": main()
