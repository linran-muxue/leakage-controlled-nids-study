import numpy as np

from scripts.run_additional_evidence_v4 import build_selector, percentile_latency, make_shared_perturbations


def test_selector_factory_has_four_fair_modes():
    assert build_selector("chi2", 5) is not None
    assert build_selector("mutual_info", 5) is not None
    assert build_selector("anova", 5) is not None
    assert build_selector("all", 5) is None


def test_percentile_latency_reports_p50_before_p95():
    result = percentile_latency([1.0, 2.0, 3.0, 4.0, 5.0])
    assert result["count"] == 5
    assert result["p50_ms"] <= result["p95_ms"]
    assert result["p99_ms"] >= result["p95_ms"]


def test_shared_perturbations_are_reproducible_and_full_dimension():
    x = np.zeros((4, 6), dtype=float)
    a = make_shared_perturbations(x, seed=7, repeats=2)
    b = make_shared_perturbations(x, seed=7, repeats=2)
    assert len(a) == 2 and a[0][0].shape == x.shape and a[0][1].shape == x.shape
    assert np.array_equal(a[0][0], b[0][0])
    assert np.array_equal(a[1][1], b[1][1])
