import numpy as np

from src.nested_statistics import paired_fold_summary, exact_sign_permutation


def test_paired_fold_summary_reports_mean_delta_and_interval():
    a = np.array([0.90, 0.91, 0.92])
    b = np.array([0.92, 0.90, 0.95])
    out = paired_fold_summary(a, b, seed=42, n_bootstrap=300)
    assert out["mean_delta"] == np.mean(b - a)
    assert out["ci_low"] <= out["mean_delta"] <= out["ci_high"]


def test_exact_sign_permutation_is_bounded():
    p = exact_sign_permutation(np.array([0.01, 0.02, -0.01]))
    assert 0.0 <= p <= 1.0
