import numpy as np
from src.journal_upgrade_experiment import choose_best_config, cv_rf


def test_choose_best_config_prefers_macro_f1_then_accuracy_then_simplicity():
    rows = [
        {"config_id": "b", "cv_macro_f1": 0.90, "cv_accuracy": 0.91, "complexity": 200},
        {"config_id": "a", "cv_macro_f1": 0.90, "cv_accuracy": 0.91, "complexity": 100},
        {"config_id": "c", "cv_macro_f1": 0.89, "cv_accuracy": 0.99, "complexity": 1},
    ]
    assert choose_best_config(rows)["config_id"] == "a"


def test_cv_rf_fits_scaler_inside_each_fold(monkeypatch):
    calls = []

    class TrackingScaler:
        def fit_transform(self, x):
            calls.append(("fit_transform", len(x)))
            return np.asarray(x, dtype=float)

        def transform(self, x):
            calls.append(("transform", len(x)))
            return np.asarray(x, dtype=float)

    monkeypatch.setattr("src.journal_upgrade_experiment.MinMaxScaler", TrackingScaler)
    X = np.arange(40, dtype=float).reshape(20, 2)
    y = np.array(["a", "b"] * 10)
    cv_rf(X, y, k=1, n_estimators=2, max_depth=2, min_samples_leaf=1, seed=42)
    fit_calls = [n for kind, n in calls if kind == "fit_transform"]
    transform_calls = [n for kind, n in calls if kind == "transform"]
    assert len(fit_calls) == 5
    assert fit_calls == [16] * 5
    assert transform_calls == [4] * 5
