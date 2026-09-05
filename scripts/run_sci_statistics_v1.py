"""Pairwise SCI statistics for the clean XGBoost baseline comparison."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.paired_tests import mcnemar_exact
from src.publication_additional import paired_bootstrap_delta
from src.statistical_analysis import paired_permutation_accuracy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(); args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in (42, 2024, 3407):
        base_path = args.results_dir / f"seed{seed}" / "predictions" / f"predictions_random_forest_chi2_seed{seed}.csv"
        if not base_path.exists():
            # The clean runner names the control model random_forest_chi2.
            raise FileNotFoundError(base_path)
        base = pd.read_csv(base_path)
        for candidate in ("xgboost_chi2", "extra_trees_chi2"):
            other = pd.read_csv(args.results_dir / f"seed{seed}" / "predictions" / f"predictions_{candidate}_seed{seed}.csv")
            mc = mcnemar_exact(base.y_true, base.y_pred, other.y_pred)
            delta, p_perm = paired_permutation_accuracy(base.y_true, base.y_pred, other.y_pred, n_permutations=20000, seed=seed)
            boot = paired_bootstrap_delta(base.y_true, base.y_pred, other.y_pred, n_bootstrap=3000, seed=seed)
            rows.append({"seed": seed, "comparison": f"{candidate}_vs_random_forest_chi2", "accuracy_delta": delta, "permutation_p": p_perm, "mcnemar_p": mc["p_value"], "macro_f1_delta": boot["point"], "macro_f1_ci_low": boot["low"], "macro_f1_ci_high": boot["high"], "a_only_correct": mc["a_only_correct"], "b_only_correct": mc["b_only_correct"]})
    pd.DataFrame(rows).to_csv(args.output, index=False, encoding="utf-8-sig")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
