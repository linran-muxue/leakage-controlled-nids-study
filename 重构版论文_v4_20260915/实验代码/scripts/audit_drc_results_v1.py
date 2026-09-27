"""Paired statistical audit for the locked DRC-Forest CIC outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import holm_adjust
from src.paired_tests import mcnemar_exact


def paired_bootstrap_delta(y_true, pred_a, pred_b, n_bootstrap=2000, seed=42):
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    if not (len(y_true) == len(pred_a) == len(pred_b) and len(y_true) > 0):
        raise ValueError("paired arrays must have equal non-zero length")
    observed = float(f1_score(y_true, pred_b, average="macro", zero_division=0) - f1_score(y_true, pred_a, average="macro", zero_division=0))
    rng = np.random.default_rng(seed)
    values = np.empty(int(n_bootstrap), dtype=float)
    for i in range(int(n_bootstrap)):
        idx = rng.integers(0, len(y_true), size=len(y_true))
        values[i] = f1_score(y_true[idx], pred_b[idx], average="macro", zero_division=0) - f1_score(y_true[idx], pred_a[idx], average="macro", zero_division=0)
    p_value = min(1.0, 2.0 * min(np.mean(values <= 0.0), np.mean(values >= 0.0)))
    return {"estimate": observed, "ci_low": float(np.quantile(values, 0.025)), "ci_high": float(np.quantile(values, 0.975)), "p_value": float(p_value)}


def summarize_comparisons(rows):
    result = [dict(row) for row in rows]
    adjusted = holm_adjust([row["p_value"] for row in result])
    for row, p_holm in zip(result, adjusted):
        row["p_holm"] = p_holm
        row["significant_alpha_0_05"] = bool(p_holm < 0.05)
    return result


def run(results_dir: Path, output_dir: Path, n_bootstrap: int = 2000):
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in [42, 2024, 3407]:
        def read(name):
            return pd.read_csv(results_dir / "predictions" / f"predictions_{name}_seed{seed}.csv")
        drc = read("drc_forest_chi2")
        equal = read("equal_rf_chi2")
        assert drc["row_id"].equals(equal["row_id"])
        boot = paired_bootstrap_delta(drc["y_true"], equal["y_pred"], drc["y_pred"], n_bootstrap=n_bootstrap, seed=seed)
        mc = mcnemar_exact(drc["y_true"], equal["y_pred"], drc["y_pred"])
        rows.append({"seed": seed, **boot, "mcnemar_p": mc["p_value"], "mcnemar_equal_only": mc["a_only_correct"], "mcnemar_drc_only": mc["b_only_correct"]})
    comparisons = summarize_comparisons([{"comparison": "DRC_vs_equal_macro_f1", "p_value": float(np.mean([row["p_value"] for row in rows]))}, {"comparison": "DRC_vs_equal_mcnemar", "p_value": float(np.mean([row["mcnemar_p"] for row in rows]))}])
    pd.DataFrame(rows).to_csv(output_dir / "paired_drc_vs_equal_by_seed.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(comparisons).to_csv(output_dir / "paired_drc_vs_equal_summary.csv", index=False, encoding="utf-8-sig")
    (output_dir / "audit_summary.json").write_text(json.dumps({"comparison": comparisons, "interpretation": "Hard-label superiority is not established when paired predictions are identical or McNemar is non-significant."}, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    args = parser.parse_args()
    run(args.results_dir, args.output_dir, n_bootstrap=args.n_bootstrap)


if __name__ == "__main__":
    main()
