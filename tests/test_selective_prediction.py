import numpy as np

from src.selective_prediction import (
    apply_rejection,
    fit_rejection_threshold,
    open_set_metrics,
    risk_coverage_curve,
)


def test_threshold_hits_requested_known_coverage():
    p = np.array([[0.9, 0.1], [0.8, 0.2], [0.6, 0.4], [0.55, 0.45]])
    threshold = fit_rejection_threshold(p, target_coverage=0.75)
    labels = apply_rejection(p, np.array(["a", "b"]), threshold)
    assert np.mean(labels != "unknown") >= 0.75


def test_risk_coverage_is_monotone_and_finite():
    y = np.array(["a", "a", "b", "b"])
    p = np.array([[.9, .1], [.6, .4], [.4, .6], [.2, .8]])
    curve = risk_coverage_curve(y, p, np.array(["a", "b"]))
    assert list(curve.columns) == ["coverage", "selective_risk", "threshold"]
    assert np.all(np.diff(curve["coverage"]) >= 0)
    assert np.isfinite(curve.to_numpy()).all()


def test_open_set_metrics_return_counts_and_auc():
    known = np.array([.05, .1, .2, .25])
    unknown = np.array([.6, .7, .8])
    result = open_set_metrics(known, unknown, threshold=.4)
    assert result["unknown_recall"] == 1.0
    assert result["known_false_rejection_rate"] == 0.0
    assert 0.0 <= result["auroc"] <= 1.0
    assert result["known_count"] == 4 and result["unknown_count"] == 3
