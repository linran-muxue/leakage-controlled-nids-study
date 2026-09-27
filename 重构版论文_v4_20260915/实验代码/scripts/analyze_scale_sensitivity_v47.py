"""Paired analysis of the scale-sensitivity experiment.
Compares the conditional mechanism with the equal-weight chi-square forest on
the 413,209-flow population, using the same statistics as the primary
protocol: per-seed macro-F1, the paired seed-level interval, TOST against the
pre-specified margins, a test-row paired bootstrap and an exact McNemar test.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import f1_score

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.paired_tests import mcnemar_exact


def load_predictions(directory: Path, pattern: str, seeds: list[int]):
    frames = {}
    for seed in seeds:
        path = directory / pattern.format(seed=seed)
        if not path.exists():
            continue
        frames[seed] = pd.read_csv(path)
    return frames


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rccf-dir", type=Path, required=True)
    ap.add_argument("--baseline-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--sesoi", type=float, nargs="+", default=[0.005, 0.01])
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rccf = load_predictions(args.rccf_dir, "predictions_seed{seed}.csv", args.seeds)
    control = load_predictions(args.baseline_dir, "predictions_equal_rf_chi2_seed{seed}.csv", args.seeds)
    seeds = sorted(set(rccf) & set(control))
    print(f"seeds with both arms: {seeds}")

    rows = []
    for seed in seeds:
        left, right = rccf[seed], control[seed]
        assert (left["true_label"].to_numpy() == right["y_true"].to_numpy()).all(), \
            f"row misalignment at seed {seed}"
        y_true = left["true_label"].to_numpy()
        f_rccf = f1_score(y_true, left["predicted_label"], average="macro", zero_division=0)
        f_ctrl = f1_score(y_true, right["y_pred"], average="macro", zero_division=0)
        agree = (left["predicted_label"].to_numpy() == right["y_pred"].to_numpy())
        rows.append({
            "seed": seed,
            "rccf_macro_f1": f_rccf,
            "control_macro_f1": f_ctrl,
            "difference": f_rccf - f_ctrl,
            "disagreements": int((~agree).sum()),
            "rows": int(len(y_true)),
        })
    frame = pd.DataFrame(rows)
    frame.to_csv(args.output_dir / "paired_by_seed.csv", index=False, encoding="utf-8-sig")

    differences = frame["difference"].to_numpy()
    n = len(differences)
    mean_diff = float(differences.mean())
    sd = float(differences.std(ddof=1)) if n > 1 else float("nan")
    sem = sd / np.sqrt(n) if n > 1 else float("nan")
    t_crit = stats.t.ppf(0.95, n - 1) if n > 1 else float("nan")
    interval_90 = [mean_diff - t_crit * sem, mean_diff + t_crit * sem]
    t_crit95 = stats.t.ppf(0.975, n - 1) if n > 1 else float("nan")
    interval_95 = [mean_diff - t_crit95 * sem, mean_diff + t_crit95 * sem]

    tost = {}
    for margin in args.sesoi:
        if n < 2:
            tost[str(margin)] = None
            continue
        lower = stats.ttest_1samp(differences, -margin, alternative="greater")
        upper = stats.ttest_1samp(differences, margin, alternative="less")
        tost[str(margin)] = {
            "p_greater_than_minus_margin": float(lower.pvalue),
            "p_less_than_margin": float(upper.pvalue),
            "equivalent": bool(lower.pvalue < 0.05 and upper.pvalue < 0.05),
        }

    # test-row paired bootstrap on the 505-row scale of the primary protocol is
    # not needed here; the test partition is much larger, so resample rows.
    seed_for_bootstrap = np.random.default_rng(20260919)
    bootstrap = []
    for seed in seeds:
        y_true = rccf[seed]["true_label"].to_numpy()
        a = rccf[seed]["predicted_label"].to_numpy()
        b = control[seed]["y_pred"].to_numpy()
        diffs = []
        n_rows = len(y_true)
        for _ in range(200):
            idx = seed_for_bootstrap.integers(0, n_rows, n_rows)
            diffs.append(f1_score(y_true[idx], a[idx], average="macro", zero_division=0)
                         - f1_score(y_true[idx], b[idx], average="macro", zero_division=0))
        bootstrap.append({"seed": seed, "low": float(np.percentile(diffs, 5)),
                          "high": float(np.percentile(diffs, 95))})
    pd.DataFrame(bootstrap).to_csv(args.output_dir / "paired_bootstrap_by_seed.csv",
                                   index=False, encoding="utf-8-sig")

    mcnemar = {}
    for seed in seeds:
        y_true = rccf[seed]["true_label"].to_numpy()
        a = rccf[seed]["predicted_label"].to_numpy()
        b = control[seed]["y_pred"].to_numpy()
        result = mcnemar_exact(y_true, a, b)
        mcnemar[str(seed)] = result if isinstance(result, dict) else float(result)

    summary = {
        "population_rows": int(frame["rows"].iloc[0]),
        "seeds": seeds,
        "mean_difference": mean_diff,
        "sd": sd,
        "seed_level_90_interval": interval_90,
        "seed_level_95_interval": interval_95,
        "tost": tost,
        "bootstrap_90_intervals": bootstrap,
        "mcnemar": mcnemar,
    }
    (args.output_dir / "scale_sensitivity_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(frame.to_string(index=False))
    print(json.dumps({k: summary[k] for k in ("mean_difference", "sd",
                                              "seed_level_90_interval", "tost")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
