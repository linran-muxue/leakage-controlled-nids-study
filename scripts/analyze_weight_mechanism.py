"""Quantify why validation-score weighting may not change RF decisions."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment_components import WeightedRandomForest, summarize_tree_weights


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--chi2-k", type=int, default=60)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--min-samples-leaf", type=int, default=2)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tr = pd.read_csv(args.processed_dir / "train.csv", low_memory=False)
    va = pd.read_csv(args.processed_dir / "validation.csv", low_memory=False)
    te = pd.read_csv(args.processed_dir / "test.csv", low_memory=False)
    names = [c for c in tr.columns if c != "target"]
    scaler = MinMaxScaler()
    x = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors="raise"))
    xv = scaler.transform(va[names].apply(pd.to_numeric, errors="raise"))
    xt = scaler.transform(te[names].apply(pd.to_numeric, errors="raise"))
    y, yv, yt = tr.target.to_numpy(), va.target.to_numpy(), te.target.to_numpy()
    scores, _ = chi2(x, y)
    idx = np.argsort(-np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max))[:args.chi2_k]
    rf = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=args.min_samples_leaf, class_weight="balanced_subsample", n_jobs=-1, random_state=args.seed).fit(x[:, idx], y)
    weighted = WeightedRandomForest(n_estimators=args.n_estimators, min_samples_leaf=args.min_samples_leaf, random_state=args.seed, weight_metric="balanced_accuracy").fit(x[:, idx], y, xv[:, idx], yv)
    summary = summarize_tree_weights(weighted.tree_scores_, weighted.tree_weights_)
    equal_proba = rf.predict_proba(xt[:, idx])
    weighted_proba = weighted.predict_proba(xt[:, idx])
    equal_pred = rf.classes_[np.argmax(equal_proba, axis=1)]
    weighted_pred = weighted.predict(xt[:, idx])
    summary.update({
        "mean_probability_l1": float(np.abs(equal_proba - weighted_proba).sum(axis=1).mean()),
        "max_probability_l1": float(np.abs(equal_proba - weighted_proba).sum(axis=1).max()),
        "prediction_disagreement_count": int(np.count_nonzero(equal_pred != weighted_pred)),
        "prediction_disagreement_rate": float(np.mean(equal_pred != weighted_pred)),
        "test_samples": int(len(yt)),
    })
    pd.DataFrame([summary]).to_csv(args.output_dir / "weight_mechanism_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"tree_score": weighted.tree_scores_, "tree_weight": weighted.tree_weights_}).to_csv(args.output_dir / "tree_weight_distribution.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"equal_pred": equal_pred, "weighted_pred": weighted_pred, "disagreement": equal_pred != weighted_pred}).to_csv(args.output_dir / "weight_prediction_comparison.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame([summary]).to_string(index=False))


if __name__ == "__main__":
    main()
