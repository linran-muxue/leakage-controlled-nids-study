"""Leave-one-source-out evaluation on the grouped modern corpora.

For every group (an IoT device in Gotham, a Cooja run in 6TiSCHSet) the model is
trained on all *other* groups and tested on the held-out one.  The same two arms
as everywhere else are compared: conditional weighting and the unweighted mean of
the same four experts.  The point is not to win - a leave-one-source-out split is
far harder than a random split, and the drop is the quantity being reported, in
the same role the day-level holdout plays for CIC-IDS2017.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from run_native_label_benchmark_v1 import split_with_minimum  # noqa: E402
import src.rccf_forest as rccf  # noqa: E402
from src.rccf_forest import RCCFForest  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--max-groups", type=int, default=12,
                    help="evaluate this many held-out groups (spread over the corpus)")
    ap.add_argument("--max-rows-per-group", type=int, default=6000)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--experts", nargs="+", default=["full", "chi2", "anova"])
    args = ap.parse_args()

    frame = pd.read_csv(ROOT / args.processed_dir / "all.csv", low_memory=False)
    features = [c for c in frame.columns if c not in ("target", "group")]
    groups = sorted(frame["group"].unique())
    step = max(1, len(groups) // args.max_groups)
    held_out = groups[::step][:args.max_groups]
    rccf.RCCFForest.expert_names = tuple(args.experts)
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"{len(groups)} groups; holding out {len(held_out)}: {held_out}", flush=True)
    for group in held_out:
        test = frame[frame["group"] == group]
        if len(test) > args.max_rows_per_group:
            test = test.sample(args.max_rows_per_group, random_state=args.seed)
        train = frame[frame["group"] != group]
        if len(train) > 200_000:
            train = train.sample(200_000, random_state=args.seed)
        X_train = train[features].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        X_test = test[features].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        y_train = train["target"].astype(str).to_numpy()
        y_test = test["target"].astype(str).to_numpy()
        # A held-out device can carry a class that the rest of the corpus shows
        # only a handful of times.  Both the five-fold split inside RCCFForest
        # and the conformal calibration slice need a few rows of every class, so
        # classes with fewer than five training rows are pruned exactly as the
        # main benchmark prunes them.
        counts = pd.Series(y_train).value_counts()
        rare = [label for label, count in counts.items() if count < 5]
        if rare:
            keep_rare = ~np.isin(y_train, rare)
            X_train, y_train = X_train.loc[keep_rare], y_train[keep_rare]
            keep_rare = ~np.isin(y_test, rare)
            X_test, y_test = X_test.loc[keep_rare], y_test[keep_rare]
            print(f"  {group}: pruned classes with fewer than five rows: {rare}",
                  flush=True)
        labels = np.unique(y_train)
        keep = np.isin(y_test, labels)
        y_test = y_test[keep]
        X_test = X_test.loc[keep]
        if len(y_test) < 50 or len(labels) < 2:
            print(f"  {group}: skipped (test {len(y_test)}, classes {len(labels)})", flush=True)
            continue
        start = time.perf_counter()
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           cv=5, random_state=args.seed)
        # The calibration slice must be stratified, and must move at least two
        # rows of every class across, or the Mondrian conformal rejector raises
        # "calibration set lacks class ..." - which is how both holdouts exited
        # with code 1 on 2026-10-04 19:42, leaving zero recorded metrics.
        train_idx, cal_idx = split_with_minimum(y_train, 0.15, args.seed)
        dense = X_train.to_numpy(dtype=np.float32)
        model.fit(dense[train_idx], y_train[train_idx],
                  dense[cal_idx], y_train[cal_idx])
        probability = model.predict_proba(X_test.to_numpy(dtype=np.float32))
        prediction = model.classes_[probability.argmax(axis=1)]
        members = np.mean([model._expert_proba(e, X_test.to_numpy(dtype=np.float32))
                           for e in model.experts_], axis=0)
        equal = model.classes_[members.argmax(axis=1)]
        macro = float(f1_score(y_test, prediction, average="macro", zero_division=0))
        equal_macro = float(f1_score(y_test, equal, average="macro", zero_division=0))
        rows.append({"group": group, "train_rows": int(len(X_train)),
                     "test_rows": int(len(y_test)), "classes": int(len(labels)),
                     "rccf_macro_f1": macro, "equal_fusion_macro_f1": equal_macro,
                     "difference": macro - equal_macro,
                     "train_seconds": time.perf_counter() - start})
        print(f"  {group}: test {len(y_test):,} rccf {macro:.4f} equal {equal_macro:.4f} "
              f"diff {macro - equal_macro:+.6f} ({rows[-1]['train_seconds']:.0f}s)",
              flush=True)
    frame_out = pd.DataFrame(rows)
    frame_out.to_csv(out / "holdout_metrics.csv", index=False, encoding="utf-8-sig")
    summary = {"processed_dir": args.processed_dir, "groups_total": len(groups),
               "groups_evaluated": len(rows),
               "rccf_macro_f1_mean": float(frame_out["rccf_macro_f1"].mean()),
               "rccf_macro_f1_min": float(frame_out["rccf_macro_f1"].min()),
               "rccf_macro_f1_max": float(frame_out["rccf_macro_f1"].max()),
               "equal_fusion_macro_f1_mean": float(frame_out["equal_fusion_macro_f1"].mean()),
               "mean_difference": float(frame_out["difference"].mean())}
    (out / "holdout_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("SOURCE_HOLDOUT_DONE")


if __name__ == "__main__":
    main()
