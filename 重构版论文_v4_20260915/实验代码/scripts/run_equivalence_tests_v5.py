"""S1: equivalence testing (TOST-style) and effect sizes for the RCCF comparison.

Addresses audit gaps 1.1/1.2/1.3 and 7.1/7.2: a claim of "no difference" requires an
equivalence test against a pre-specified smallest effect size of interest (SESOI),
not merely a non-significant superiority test.

Method: paired bootstrap over test rows. The 100*(1-2*alpha)% interval of the paired
Macro-F1 difference is compared against +/- SESOI. If the whole interval lies inside
the equivalence band, the two models are declared equivalent at level alpha.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parents[1]
LABEL_ORDER = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load_predictions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rename = {}
    if "row_id" not in df.columns:
        df = df.reset_index().rename(columns={"index": "row_id"})
    if "true_label" in df.columns:
        rename["true_label"] = "y_true"
    if "predicted_label" in df.columns:
        rename["predicted_label"] = "y_pred"
    df = df.rename(columns=rename)
    missing = {"row_id", "y_true", "y_pred"} - set(df.columns)
    if missing:
        raise ValueError(f"{path} missing columns {missing}")
    return df[["row_id", "y_true", "y_pred"]].copy()


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(f1_score(y_true, y_pred, average="macro", labels=LABEL_ORDER, zero_division=0))


def paired_bootstrap_delta(y_true, pred_a, pred_b, *, n_boot: int, seed: int):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    deltas = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas[b] = (macro_f1(y_true[idx], pred_a[idx])
                     - macro_f1(y_true[idx], pred_b[idx]))
    return deltas


def mcnemar_exact(y_true, pred_a, pred_b) -> dict:
    a_correct = pred_a == y_true
    b_correct = pred_b == y_true
    n01 = int(np.sum(~a_correct & b_correct))   # A wrong, B right
    n10 = int(np.sum(a_correct & ~b_correct))   # A right, B wrong
    discordant = n01 + n10
    if discordant == 0:
        p = 1.0
    else:
        p = float(binomtest(min(n01, n10), discordant, 0.5).pvalue)
    # paired effect size: McNemar delta (Cohen-style) on correctness
    delta_eff = (n10 - n01) / len(y_true)
    return {"n_a_correct_b_wrong": n10, "n_a_wrong_b_correct": n01,
            "discordant": discordant, "mcnemar_p": p, "paired_effect_delta": delta_eff}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rccf-dir", default="results_rccf_cic_natural_v3b")
    ap.add_argument("--baseline-dir", default="results_cic_natural_baselines_v3b")
    ap.add_argument("--baseline-name", default="equal_rf_chi2")
    ap.add_argument("--output-dir", default="results_equivalence_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--sesoi", nargs="+", type=float, default=[0.005, 0.01])
    ap.add_argument("--n-boot", type=int, default=4000)
    ap.add_argument("--alpha", type=float, default=0.05)
    args = ap.parse_args()

    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    lo_q, hi_q = 100 * args.alpha, 100 * (1 - args.alpha)

    rows, effect_rows = [], []
    per_seed_deltas: list[np.ndarray] = []

    for seed in args.seeds:
        rccf = load_predictions(ROOT / args.rccf_dir / f"predictions_seed{seed}.csv")
        base = load_predictions(ROOT / args.baseline_dir / "predictions" /
                                f"predictions_{args.baseline_name}_seed{seed}.csv")
        merged = rccf.merge(base, on="row_id", suffixes=("_rccf", "_base"), how="inner")
        if merged.empty:
            raise ValueError(f"no aligned rows for seed {seed}")
        y = merged["y_true_rccf"].to_numpy()
        pa = merged["y_pred_rccf"].to_numpy()
        pb = merged["y_pred_base"].to_numpy()

        f1_a, f1_b = macro_f1(y, pa), macro_f1(y, pb)
        delta = f1_a - f1_b
        boot = paired_bootstrap_delta(y, pa, pb, n_boot=args.n_boot, seed=seed)
        per_seed_deltas.append(boot)
        ci_lo, ci_hi = np.percentile(boot, [lo_q, hi_q])
        ci95_lo, ci95_hi = np.percentile(boot, [2.5, 97.5])
        mc = mcnemar_exact(y, pa, pb)

        row = {
            "seed": seed, "n_rows": len(y),
            "macro_f1_rccf": f1_a, "macro_f1_baseline": f1_b,
            "delta": delta,
            "relative_delta_pct": 100 * delta / f1_b if f1_b else np.nan,
            "ci_low": ci_lo, "ci_high": ci_hi,
            "ci95_low": ci95_lo, "ci95_high": ci95_hi,
            **mc,
        }
        for sesoi in args.sesoi:
            row[f"tost_equivalent_at_{sesoi}"] = bool(ci_lo > -sesoi and ci_hi < sesoi)
        rows.append(row)
        effect_rows.append({
            "seed": seed, "delta_macro_f1": delta,
            "paired_effect_delta": mc["paired_effect_delta"],
            "mcnemar_odds_ratio": (mc["n_a_correct_b_wrong"] / mc["n_a_wrong_b_correct"])
                                  if mc["n_a_wrong_b_correct"] else np.inf,
            "discordant_fraction": mc["discordant"] / len(y),
        })

    per_seed = pd.DataFrame(rows)
    pooled_boot = np.concatenate(per_seed_deltas)
    pooled_ci = np.percentile(pooled_boot, [lo_q, hi_q])
    pooled_ci95 = np.percentile(pooled_boot, [2.5, 97.5])
    pooled = {
        "mean_delta": float(per_seed["delta"].mean()),
        "pooled_ci_low": float(pooled_ci[0]), "pooled_ci_high": float(pooled_ci[1]),
        "pooled_ci95_low": float(pooled_ci95[0]), "pooled_ci95_high": float(pooled_ci95[1]),
        "n_seeds": len(args.seeds),
    }
    for sesoi in args.sesoi:
        pooled[f"tost_equivalent_at_{sesoi}"] = bool(pooled_ci[0] > -sesoi and pooled_ci[1] < sesoi)

    per_seed.to_csv(out / "tost_results.csv", index=False)
    pd.DataFrame(effect_rows).to_csv(out / "effect_sizes.csv", index=False)
    summary = {
        "comparison": f"rccf_minus_{args.baseline_name}",
        "protocol": "CIC-IDS2017 natural-prior population, deduplicated and capped",
        "alpha": args.alpha,
        "sesoi_candidates": args.sesoi,
        "n_bootstrap": args.n_boot,
        "pooled": pooled,
    }
    (out / "equivalence_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(per_seed[["seed", "macro_f1_rccf", "macro_f1_baseline", "delta",
                    "ci_low", "ci_high", "mcnemar_p"]].to_string(index=False))
    print(json.dumps(pooled, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
