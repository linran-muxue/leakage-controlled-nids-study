import numpy as np
from src.publication_additional import bootstrap_probability_metrics, paired_bootstrap_delta

def test_probability_bootstrap_returns_requested_metrics_and_bounds():
    y = np.array(["a", "b", "a", "b"])
    classes = np.array(["a", "b"])
    p = np.array([[.9,.1],[.2,.8],[.8,.2],[.3,.7]])
    out = bootstrap_probability_metrics(y, p, classes, n_bootstrap=20, seed=1)
    assert set(out) == {"log_loss", "brier_macro", "ece"}
    assert all(len(v) == 3 for v in out.values())
    assert all(0 <= v[0] <= v[1] <= v[2] for v in out.values())

def test_paired_bootstrap_delta_has_point_and_interval():
    y = np.array([0, 1, 0, 1, 0, 1])
    a = np.array([0, 1, 1, 1, 0, 0])
    b = np.array([0, 1, 0, 1, 0, 1])
    out = paired_bootstrap_delta(y, a, b, n_bootstrap=50, seed=2)
    assert out["point"] > 0
    assert out["low"] <= out["point"] <= out["high"]
