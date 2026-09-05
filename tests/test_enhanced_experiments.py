import numpy as np

from src.experiment_components import compute_metrics


def test_compute_metrics_supports_five_class_string_labels():
    y_true = np.array(["Normal", "DoS", "Probe", "R2L", "U2R"])
    y_pred = np.array(["Normal", "DoS", "Probe", "Normal", "U2R"])
    result = compute_metrics(y_true, y_pred)
    assert result["accuracy"] == 0.8
    assert 0.0 <= result["macro_f1"] <= 1.0
