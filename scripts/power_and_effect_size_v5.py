"""Post-hoc power analysis and standardised effect sizes (self-check items D10, D12).

Paired design over seeds. For n paired observations with standard deviation s of the
paired differences:

  minimum detectable effect (80% power, two-sided alpha = 0.05)
      MDE = (t_{1-alpha/2, n-1} + t_{1-beta, n-1}) * s / sqrt(n)
  achievable equivalence margin (TOST at alpha = 0.05)
      margin > t_{1-alpha, n-1} * s / sqrt(n) = half-width of the 90% interval
  standardised effect size
      d_z = mean difference / s
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load_pred(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rename = {}
    if "true_label" in df.columns:
        rename["true_label"] = "y"
    if "predicted_label" in df.columns:
        rename["predicted_label"] = "yp"
    if "y_true" in df.columns:
        rename["y_true"] = "y"
    if "y_pred" in df.columns:
        rename["y_pred"] = "yp"
    df = df.rename(columns=rename)
    keep = ["row_id", "y", "yp"] + [c for c in df.columns if c.startswith(("prob_", "proba__"))]
    return df[keep].copy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def cliffs_delta_from_paired(a_correct: np.ndarray, b_correct: np.ndarray) -> float:
    """Paired dominance measure: (#A wins - #B wins) / n."""
    n = len(a_correct)
    return float(((a_correct & ~b_correct).sum() - (~a_correct & b_correct).sum()) / n)


def main() -> None:
    run = ROOT / "results_seeds10_v5"
    manifest = json.loads((run / "run_manifest.json").read_text("utf-8"))
    seeds = manifest["seeds"]
    arms = ["rccf", "equal_rf_all", "equal_rf_chi2", "extra_trees_chi2"]

    per_seed = {}
    for seed in seeds:
        frames = {}
        frames["rccf"] = load_pred(run / f"predictions_seed{seed}.csv")
        for arm in arms[1:]:
            frames[arm] = load_pred(run / "predictions" / f"predictions_{arm}_seed{seed}.csv")
        per_seed[seed] = frames

    rows = []
    effect_rows = []
    for name in arms:
        rows.append({
            "model": name,
            "macro_f1_mean": float(np.mean([
                macro_f1(per_seed[s][name]["y"], per_seed[s][name]["yp"]) for s in seeds])),
            "macro_f1_std": float(np.std([
                macro_f1(per_seed[s][name]["y"], per_seed[s][name]["yp"]) for s in seeds], ddof=1)),
        })
    performance = pd.DataFrame(rows).to_csv(
        run / "metrics_aggregate_10seeds.csv", index=False, encoding="utf-8-sig")

    # pairwise paired comparisons against RCCF
    analysis = []
    for arm in ["equal_rf_chi2", "equal_rf_all", "extra_trees_chi2"]:
        diffs, cliff, dz_input = [], [], []
        for seed in seeds:
            a = per_seed[seed]["rccf"]
            b = per_seed[seed][arm]
            merged = a.merge(b, on="row_id", suffixes=("_a", "_b"))
            if merged.empty:
                continue
            f1a = macro_f1(merged["y_a"], merged["yp_a"])
            f1b = macro_f1(merged["y_b"], merged["yp_b"])
            diffs.append(f1a - f1b)
            cliff.append(cliffs_delta_from_paired(merged["y_a"] == merged["yp_a"],
                                                  merged["y_b"] == merged["yp_b"]))
        diffs = np.asarray(diffs)
        n = len(diffs)
        mean, sd = float(diffs.mean()), float(diffs.std(ddof=1))
        t_crit = stats.t.ppf(0.975, n - 1)
        t_power = stats.t.ppf(0.80, n - 1)
        t_90 = stats.t.ppf(0.95, n - 1)
        mde = (t_crit + t_power) * sd / np.sqrt(n)
        margin = t_90 * sd / np.sqrt(n)
        ci = (mean - t_crit * sd / np.sqrt(n), mean + t_crit * sd / np.sqrt(n))
        analysis.append({
            "comparison": f"rccf_minus_{arm}", "n_seeds": n,
            "mean_difference": round(mean, 6),
            "sd_difference": round(sd, 6),
            "ci95_low": round(ci[0], 6), "ci95_high": round(ci[1], 6),
            "min_detectable_effect_80pct": round(float(mde), 6),
            "achievable_tost_margin": round(float(margin), 6),
            "ci90_low": round(mean - margin, 6),
            "ci90_high": round(mean + margin, 6),
            "tost_equivalent_at_0.005": bool(mean - margin > -0.005 and mean + margin < 0.005),
            "tost_equivalent_at_0.01": bool(mean - margin > -0.01 and mean + margin < 0.01),
        })
        effect_rows.append({
            "comparison": f"rccf_minus_{arm}",
            "cohens_dz": round(mean / sd, 4) if sd else float("nan"),
            "cliffs_delta_mean": round(float(np.mean(cliff)), 6),
            "relative_difference_pct": round(100 * mean / np.mean([
                macro_f1(per_seed[s][arm]["y"], per_seed[s][arm]["yp"]) for s in seeds]), 4),
            "seeds_favouring_rccf": int((diffs > 0).sum()),
            "seeds_favouring_baseline": int((diffs < 0).sum()),
            "seeds_tied": int((diffs == 0).sum()),
        })

    pd.DataFrame(analysis).to_csv(run / "power_analysis.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(effect_rows).to_csv(run / "effect_sizes.csv", index=False, encoding="utf-8-sig")
    (run / "power_analysis.json").write_text(json.dumps({
        "design": "paired across seeds, two-sided alpha = 0.05, target power = 0.80",
        "n_seeds": len(seeds),
        "results": analysis,
        "effect_sizes": effect_rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(pd.DataFrame(analysis).to_string(index=False))
    print()
    print(pd.DataFrame(effect_rows).to_string(index=False))


if __name__ == "__main__":
    main()
