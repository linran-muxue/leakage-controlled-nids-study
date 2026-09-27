"""Cost-sensitive evaluation (residual gap: no false-negative/false-positive trade-off).

Binary view of the closed-set task: attack = any class other than Normal. For a cost
ratio c = C_FN / C_FP the decision threshold on P(attack) is swept and the operating
point minimising the normalised expected cost (NEC) is reported. NEC is normalised by
the cost of the trivial all-attack and all-normal strategies so that 1.0 is the cost of
always predicting the majority class.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]
RUN = ROOT / "results_seeds10_v5"


def load(seed: int, arm: str) -> pd.DataFrame:
    path = (RUN / f"predictions_seed{seed}.csv") if arm == "rccf" else \
        (RUN / "predictions" / f"predictions_{arm}_seed{seed}.csv")
    df = pd.read_csv(path)
    rename = {}
    for src, dst in (("true_label", "y"), ("predicted_label", "yp"),
                     ("y_true", "y"), ("y_pred", "yp")):
        if src in df.columns:
            rename[src] = dst
    df = df.rename(columns=rename)
    prob_cols = [c for c in df.columns if c.startswith(("prob_", "proba__"))]
    df = df.rename(columns={c: c.split("_", 1)[1].split("__")[-1] for c in prob_cols})
    return df


def nec(y_attack: np.ndarray, p_attack: np.ndarray, ratio: float) -> tuple[float, float]:
    """Return (best NEC, threshold achieving it)."""
    n = len(y_attack)
    pos = int(y_attack.sum())
    neg = n - pos
    thresholds = np.unique(np.round(p_attack, 4))
    best, best_t = np.inf, 0.5
    for t in thresholds:
        pred = p_attack >= t
        fn = int((y_attack & ~pred).sum())
        fp = int((~y_attack & pred).sum())
        cost = ratio * fn + fp
        normaliser = min(ratio * pos, neg) if min(ratio * pos, neg) > 0 else 1.0
        value = cost / normaliser
        if value < best:
            best, best_t = value, float(t)
    return best, best_t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="results_cost_v5")
    ap.add_argument("--ratios", nargs="+", type=float, default=[1, 5, 10, 50, 100])
    args = ap.parse_args()
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    arms = ["rccf", "equal_rf_chi2", "extra_trees_chi2"]
    rows = []
    for arm in arms:
        for seed in SEEDS:
            df = load(seed, arm)
            y_attack = (df["y"].to_numpy() != "Normal")
            p_attack = 1.0 - df["Normal"].to_numpy()
            for ratio in args.ratios:
                value, threshold = nec(y_attack, p_attack, ratio)
                rows.append({"model": arm, "seed": seed, "cost_ratio_fn_fp": ratio,
                             "nec": value, "threshold": threshold})
    df = pd.DataFrame(rows)
    df.to_csv(out / "cost_sensitive_by_seed.csv", index=False, encoding="utf-8-sig")
    summary = (df.groupby(["model", "cost_ratio_fn_fp"])[["nec", "threshold"]]
               .mean().round(5).reset_index())
    summary.to_csv(out / "cost_sensitive_summary.csv", index=False, encoding="utf-8-sig")
    (out / "cost_sensitive_summary.json").write_text(json.dumps({
        "task": "binary view: attack versus Normal",
        "n_seeds": len(SEEDS),
        "normalisation": "NEC = cost / min(ratio * positives, negatives)",
        "summary": summary.to_dict(orient="records"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
