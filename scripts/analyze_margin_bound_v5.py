"""S6: explicit perturbation bound and the fraction of provably invariant rows.

Audit gap 5.2. Proposition 2 in the manuscript was stated existentially ("if the
margin exceeds the maximum possible weighted perturbation, the hard label is
unchanged"). This script makes the bound explicit and computable.

Bound. Let p_bar = (1/Q) sum_e p_e be equal-weight averaging and p_w = sum_e w_e p_e
the gated fusion, with w a probability vector. Because every expert posterior lies on
the simplex (||p_e||_1 = 1),

    ||p_w - p_bar||_1  <=  sum_e |w_e - 1/Q|  =: Delta_bound(x).

If 2 * Delta_actual(x) < m(x), where Delta_actual = ||p_w - p_bar||_inf and
m(x) = p_bar_(1) - p_bar_(2) is the equal-weight margin, then the argmax of p_w must
equal the argmax of p_bar: the conditional weighting cannot change that row's label.

The script reports the empirical disagreement rate, the fraction of rows satisfying
the provable condition under the a priori bound, and the fraction under the realised
perturbation.
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
from sklearn.metrics import f1_score

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_margin_bound_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--cv", type=int, default=5)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")

    summaries = []
    for seed in args.seeds:
        start = time.perf_counter()
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           cv=args.cv, random_state=seed, n_jobs=-1)
        model.fit(Xtr, ytr, Xva, yva)
        expert_probs = np.stack([model._expert_proba(e, Xte) for e in model.experts_], axis=1)
        p_equal = expert_probs.mean(axis=1)
        p_gated = model._raw_predict_proba(Xte)
        weights = model.expert_weights_
        q = weights.shape[1]

        delta_bound = np.abs(weights - 1.0 / q).sum(axis=1)
        delta_actual = np.abs(p_gated - p_equal).max(axis=1)
        ordered = np.sort(p_equal, axis=1)
        margin = ordered[:, -1] - ordered[:, -2]

        argmax_equal = np.argmax(p_equal, axis=1)
        argmax_gated = np.argmax(p_gated, axis=1)
        changed = argmax_equal != argmax_gated
        provable_bound = margin > 2 * delta_bound
        provable_actual = margin > 2 * delta_actual

        per_row = pd.DataFrame({
            "seed": seed, "row_id": np.arange(len(yte)), "true_label": yte,
            "margin_equal_weight": margin,
            "delta_bound_l1": delta_bound,
            "delta_actual_linf": delta_actual,
            "prediction_changed": changed,
            "provably_invariant_by_bound": provable_bound,
            "provably_invariant_by_actual": provable_actual,
        })
        per_row.to_csv(out / f"margin_bound_per_row_seed{seed}.csv",
                       index=False, encoding="utf-8-sig")

        summaries.append({
            "seed": seed,
            "n_rows": int(len(yte)),
            "empirical_changed_rows": int(changed.sum()),
            "empirical_changed_rate": float(changed.mean()),
            "provable_by_bound_rows": int(provable_bound.sum()),
            "provable_by_bound_rate": float(provable_bound.mean()),
            "provable_by_actual_rows": int(provable_actual.sum()),
            "provable_by_actual_rate": float(provable_actual.mean()),
            "median_margin": float(np.median(margin)),
            "median_delta_bound": float(np.median(delta_bound)),
            "median_delta_actual": float(np.median(delta_actual)),
            "margin_to_bound_ratio_median": float(np.median(margin / np.maximum(delta_bound, 1e-12))),
            "equal_weight_macro_f1": macro_f1(yte, model.classes_[argmax_equal]),
            "gated_macro_f1": macro_f1(yte, model.classes_[argmax_gated]),
            "mean_weight_entropy": float(
                (-(weights * np.log(np.clip(weights, 1e-12, 1.0))).sum(axis=1) / np.log(q)).mean()),
            "elapsed_seconds": time.perf_counter() - start,
        })
        pd.DataFrame(summaries).to_csv(out / "margin_bound_summary.csv",
                                       index=False, encoding="utf-8-sig")
        print(f"seed={seed} changed={int(changed.sum())} "
              f"provable_bound={provable_bound.mean():.4f} "
              f"provable_actual={provable_actual.mean():.4f}", flush=True)

    df = pd.DataFrame(summaries)
    pooled = {
        "n_seeds": len(args.seeds),
        "total_rows": int(df["n_rows"].sum()),
        "empirical_changed_rows": int(df["empirical_changed_rows"].sum()),
        "provable_by_bound_rate_mean": float(df["provable_by_bound_rate"].mean()),
        "provable_by_actual_rate_mean": float(df["provable_by_actual_rate"].mean()),
        "median_delta_bound_mean": float(df["median_delta_bound"].mean()),
        "median_margin_mean": float(df["median_margin"].mean()),
        "derivation": "||p_w - p_bar||_1 <= sum_e |w_e - 1/Q|; argmax invariant if 2*Delta < margin",
    }
    (out / "margin_bound_summary.json").write_text(
        json.dumps(pooled, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(pooled, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
