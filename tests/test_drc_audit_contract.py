import pandas as pd

from scripts.audit_drc_results_v1 import paired_bootstrap_delta, summarize_comparisons


def test_paired_bootstrap_delta_is_deterministic_and_has_interval():
    truth = pd.Series(["a", "a", "b", "b"])
    pred_a = pd.Series(["a", "a", "b", "a"])
    pred_b = pd.Series(["a", "b", "b", "a"])
    first = paired_bootstrap_delta(truth, pred_a, pred_b, n_bootstrap=100, seed=7)
    second = paired_bootstrap_delta(truth, pred_a, pred_b, n_bootstrap=100, seed=7)
    assert first == second
    assert {"estimate", "ci_low", "ci_high", "p_value"} <= set(first)
    assert first["ci_low"] <= first["estimate"] <= first["ci_high"]


def test_comparison_summary_applies_holm_adjustment():
    rows = summarize_comparisons(
        [
            {"comparison": "drc_vs_equal", "p_value": 0.01},
            {"comparison": "drc_vs_extra", "p_value": 0.20},
        ]
    )
    assert "p_holm" in rows[0]
    assert all(0.0 <= row["p_holm"] <= 1.0 for row in rows)

