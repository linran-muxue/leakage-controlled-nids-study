import numpy as np

from src.rccf_metrics import classification_metrics, holm_adjust, paired_sign_flip, selective_metrics


def test_metrics_include_probability_and_selective_endpoints():
    y = np.array(["a", "b", "a", "b"])
    p = np.array([[.9,.1],[.2,.8],[.6,.4],[.4,.6]])
    out = classification_metrics(y, p, np.array(["a", "b"]))
    assert {"macro_f1", "log_loss", "brier", "ece", "mce"} <= out.keys()
    curve = selective_metrics(y, p, np.array(["a", "b"]))
    assert {"aurc", "risk_at_90", "risk_at_95"} <= curve.keys()


def test_holm_adjustment_is_monotone_in_sorted_order():
    adjusted = holm_adjust([.01, .04, .03])
    assert np.allclose(adjusted, [.03, .06, .06])


def test_sign_flip_detects_zero_difference():
    out = paired_sign_flip([0, 0, 0])
    assert out["estimate"] == 0
    assert out["p_value"] == 1
