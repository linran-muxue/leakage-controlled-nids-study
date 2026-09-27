"""Exact sign-flip tests over the ten seed differences, with Holm correction.

The methods section claims Holm correction; this script produces the adjusted values so
that the claim is backed by a reported result.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results_seeds10_v5"
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load(seed: int, arm: str) -> pd.DataFrame:
    path = (RUN / f"predictions_seed{seed}.csv") if arm == "rccf" else \
        (RUN / "predictions" / f"predictions_{arm}_seed{seed}.csv")
    df = pd.read_csv(path)
    rename = {}
    for src, dst in (("true_label", "y"), ("predicted_label", "yp"),
                     ("y_true", "y"), ("y_pred", "yp")):
        if src in df.columns:
            rename[src] = dst
    return df.rename(columns=rename)[["row_id", "y", "yp"]]


def macro_f1(y, pred) -> float:
    from sklearn.metrics import f1_score
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def signflip_p(diffs: np.ndarray) -> float:
    observed = abs(diffs.mean())
    n = len(diffs)
    count = 0
    total = 0
    for signs in itertools.product((1, -1), repeat=n):
        total += 1
        if abs((diffs * np.array(signs)).mean()) >= observed - 1e-12:
            count += 1
    return count / total


def main() -> None:
    rows = []
    for arm in ["equal_rf_chi2", "equal_rf_all", "extra_trees_chi2"]:
        diffs = []
        for seed in SEEDS:
            a, b = load(seed, "rccf"), load(seed, arm)
            m = a.merge(b, on="row_id", suffixes=("_a", "_b"))
            diffs.append(macro_f1(m["y_a"], m["yp_a"]) - macro_f1(m["y_b"], m["yp_b"]))
        diffs = np.asarray(diffs)
        rows.append({"comparison": f"rccf_minus_{arm}", "mean_difference": diffs.mean(),
                     "n_seeds": len(diffs), "signflip_p": signflip_p(diffs)})
    df = pd.DataFrame(rows).sort_values("signflip_p").reset_index(drop=True)
    m = len(df)
    adjusted = []
    running = 0.0
    for i, p in enumerate(df["signflip_p"]):
        value = min(1.0, p * (m - i))
        running = max(running, value)
        adjusted.append(running)
    df["holm_adjusted_p"] = adjusted
    df.to_csv(RUN / "signflip_holm.csv", index=False, encoding="utf-8-sig")
    (RUN / "signflip_holm.json").write_text(json.dumps({
        "test": "exact sign-flip on the ten seed-level paired differences",
        "correction": "Holm within the family of three comparisons against RCCF",
        "results": df.to_dict(orient="records"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(df.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
