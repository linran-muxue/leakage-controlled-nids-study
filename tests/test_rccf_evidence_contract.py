import json

import numpy as np
import pandas as pd

from scripts.analyze_rccf_evidence_v1 import _paired_bootstrap, _shared_perturbations


def test_shared_perturbations_are_reproducible_and_full_dimensional():
    x = np.ones((4, 6))
    a = _shared_perturbations(x, x, seed=9, repeats=2)
    b = _shared_perturbations(x, x, seed=9, repeats=2)
    assert len(a) == 2
    assert np.array_equal(a[0][0], b[0][0])
    assert np.array_equal(a[0][1], b[0][1])
    assert a[0][0].shape == a[0][1].shape == x.shape


def test_paired_bootstrap_returns_interval():
    y = np.array(["a", "b", "a", "b"] * 5)
    a = np.array(["a", "b", "a", "b"] * 5)
    b = np.array(["b", "b", "a", "b"] * 5)
    result = _paired_bootstrap(y, a, b, seed=2, n_resamples=50)
    assert {"estimate", "lower", "upper"} <= result.keys()
    assert result["lower"] <= result["upper"]
