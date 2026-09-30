"""Measure how much the four experts actually disagree on the primary test set.

The manuscript used to say the experts "disagree on no test row", which is not
what the data show: on the natural-prior population the four views disagree on
about a quarter of a percent of test rows.  What is true is that the *gate* still
reproduces equal voting on all but one of 79,860 predictions, because those
disagreements sit far from the decision boundary.  This script records the
measured disagreement so the distinction can be stated with numbers.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    X = frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy()
    return X, frame["target"].to_numpy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_expert_disagreement_v1")
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_test, y_test = load(data / "test.csv")
    labels = np.unique(y_train)

    rows = []
    for seed in args.seeds:
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           random_state=seed)
        predictions = []
        for index, name in enumerate(model.expert_names):
            expert = model._fit_expert(name, X_train, y_train, seed + index)
            probability = model._expert_proba(expert, X_test)
            predictions.append(expert["forest"].classes_[probability.argmax(axis=1)])
        predictions = np.stack(predictions)
        row = {"seed": seed, "test_rows": int(len(y_test))}
        for a, b in itertools.combinations(range(len(model.expert_names)), 2):
            name = f"{model.expert_names[a]}_vs_{model.expert_names[b]}"
            differing = int((predictions[a] != predictions[b]).sum())
            row[f"disagree_{name}"] = differing
            row[f"disagree_pct_{name}"] = 100 * differing / len(y_test)
        row["any_expert_differs_from_first"] = int(
            (predictions != predictions[0]).any(axis=0).sum())
        for index, name in enumerate(model.expert_names):
            row[f"macro_f1_{name}"] = float(
                f1_score(y_test, predictions[index], average="macro", labels=labels,
                         zero_division=0))
        rows.append(row)
        pairs = [row[f"disagree_pct_{n}"] for n in
                 (f"{a}_vs_{b}" for a, b in itertools.combinations(model.expert_names, 2))]
        print(f"seed {seed}: pairwise disagreement {min(pairs):.3f}%-{max(pairs):.3f}%, "
              f"any-expert rows {row['any_expert_differs_from_first']}", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(out / "disagreement_by_seed.csv", index=False, encoding="utf-8-sig")
    percent_columns = [c for c in metrics.columns if c.startswith("disagree_pct_")]
    summary = {
        "population": args.processed_dir,
        "seeds": [int(seed) for seed in args.seeds],
        "test_rows_per_seed": int(metrics["test_rows"].iloc[0]),
        "pairwise_disagreement_pct_min": float(metrics[percent_columns].min().min()),
        "pairwise_disagreement_pct_max": float(metrics[percent_columns].max().max()),
        "pairwise_disagreement_pct_mean": float(metrics[percent_columns].mean().mean()),
        "rows_differing_min": int(metrics[[c for c in metrics.columns
                                           if c.startswith("disagree_") and not c.startswith("disagree_pct_")]]
                                  .min().min()),
        "rows_differing_max": int(metrics[[c for c in metrics.columns
                                           if c.startswith("disagree_") and not c.startswith("disagree_pct_")]]
                                  .max().max()),
        "seed_42_pairs_pct_range": [
            float(metrics[percent_columns].iloc[0].min()),
            float(metrics[percent_columns].iloc[0].max())],
    }
    (out / "expert_disagreement_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
