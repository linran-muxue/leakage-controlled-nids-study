import numpy as np

from src.statistical_analysis import bootstrap_metric_ci, paired_permutation_accuracy


def test_bootstrap_metric_ci_is_deterministic_and_bounded():
    y = np.array([0, 1, 1, 0])
    pred = np.array([0, 1, 0, 0])
    a = bootstrap_metric_ci(y, pred, metric="accuracy", n_bootstrap=200, seed=7)
    b = bootstrap_metric_ci(y, pred, metric="accuracy", n_bootstrap=200, seed=7)
    assert a == b
    assert 0 <= a[0] <= a[1] <= a[2] <= 1


def test_paired_permutation_accuracy_returns_valid_p_value():
    y = np.array([0, 1, 1, 0])
    pred_a = np.array([0, 1, 0, 0])
    pred_b = np.array([0, 1, 1, 0])
    delta, p = paired_permutation_accuracy(y, pred_a, pred_b, n_permutations=500, seed=3)
    assert delta == 0.25
    assert 0 <= p <= 1
