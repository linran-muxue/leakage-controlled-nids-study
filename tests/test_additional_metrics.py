import numpy as np

from src.additional_metrics import (
    calibration_errors,
    holm_adjust,
    relative_metric_drop,
    percentile_latency,
)


def test_calibration_errors_are_bounded_and_zero_for_perfect_binary_probabilities():
    y = np.array([1, 1, 0, 0])
    p = np.array([1.0, 1.0, 0.0, 0.0])
    result = calibration_errors(y, p, n_bins=2)
    assert result["ece"] == 0.0
    assert result["mce"] == 0.0


def test_calibration_errors_align_multiclass_string_labels():
    y = np.array(["Bot", "Normal"])
    p = np.array([[1.0, 0.0], [0.0, 1.0]])
    result = calibration_errors(y, p, n_bins=2, class_labels=["Bot", "Normal"])
    assert result["ece"] == 0.0
    assert result["mce"] == 0.0


def test_holm_adjust_controls_ordered_p_values():
    adjusted = holm_adjust([0.01, 0.04, 0.20])
    assert adjusted == [0.03, 0.08, 0.2]


def test_relative_metric_drop_and_latency_percentiles():
    assert np.isclose(relative_metric_drop(0.8, 0.6), 0.25)
    result = percentile_latency([1.0, 2.0, 3.0, 4.0])
    assert result["p50"] == 2.5
    assert np.isclose(result["p95"], 3.85)
    assert np.isclose(result["p99"], 3.97)
