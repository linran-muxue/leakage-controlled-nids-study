import numpy as np

from scripts.tune_all_baselines import build_model, evaluate_config_cv


def test_baseline_cv_fits_scaler_inside_each_fold(monkeypatch):
    calls = []

    class TrackingScaler:
        def fit_transform(self, x):
            calls.append(("fit_transform", len(x)))
            return np.asarray(x, dtype=float)

        def transform(self, x):
            calls.append(("transform", len(x)))
            return np.asarray(x, dtype=float)

    monkeypatch.setattr("scripts.tune_all_baselines.MinMaxScaler", TrackingScaler)
    X = np.arange(40, dtype=float).reshape(20, 2)
    y = np.array(["a", "b"] * 10)
    evaluate_config_cv(X, y, "decision_tree", "all", 2, {"max_depth": 2}, seed=42)
    assert [n for kind, n in calls if kind == "fit_transform"] == [16] * 5
    assert [n for kind, n in calls if kind == "transform"] == [4] * 5


def test_tree_ensemble_tuning_applies_min_samples_leaf():
    rf = build_model("random_forest", {"n_estimators": 10, "min_samples_leaf": 4}, seed=42)
    et = build_model("extra_trees", {"n_estimators": 10, "min_samples_leaf": 2}, seed=42)
    assert rf.min_samples_leaf == 4
    assert et.min_samples_leaf == 2
