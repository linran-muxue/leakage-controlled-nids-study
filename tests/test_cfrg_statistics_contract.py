import numpy as np
import pandas as pd

from scripts.audit_cfrg_results_v1 import audit_pair


def test_identical_prediction_pair_has_zero_effect_and_mcnemar_one():
    y = np.array(["a", "b", "a", "b"])
    p = np.array([[.9, .1], [.1, .9], [.8, .2], [.2, .8]])
    frame = pd.DataFrame({"y_true": y, "y_pred": y, "proba__a": p[:, 0], "proba__b": p[:, 1]})
    result = audit_pair(frame, frame, ["a", "b"], n_bootstrap=100, n_permutations=100, seed=1)
    assert result["delta_macro_f1"] == 0.0
    assert result["mcnemar_p"] == 1.0
    assert result["delta_macro_f1_ci_low"] == 0.0
    assert result["delta_macro_f1_ci_high"] == 0.0


def test_improved_prediction_pair_has_positive_direction():
    y = np.array(["a", "b", "a", "b"])
    poor = np.array(["b", "b", "b", "a"])
    good = y.copy()
    p1 = np.full((4, 2), .5); p2 = p1.copy()
    first = pd.DataFrame({"y_true": y, "y_pred": poor, "proba__a": p1[:, 0], "proba__b": p1[:, 1]})
    second = pd.DataFrame({"y_true": y, "y_pred": good, "proba__a": p2[:, 0], "proba__b": p2[:, 1]})
    result = audit_pair(first, second, ["a", "b"], n_bootstrap=100, n_permutations=100, seed=1)
    assert result["delta_macro_f1"] > 0
    assert result["mcnemar_b10"] > result["mcnemar_b01"]
