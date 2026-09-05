import numpy as np
import pandas as pd

from src.experiment_components import (
    WeightedRandomForest,
    compute_metrics,
    select_chi2_features,
    summarize_tree_weights,
)


def test_chi2_selection_returns_requested_features_and_rankings():
    X = pd.DataFrame({"strong": [0, 0, 10, 10], "weak": [1, 2, 1, 2], "constant": [1, 1, 1, 1]})
    y = np.array([0, 0, 1, 1])
    selected, scores = select_chi2_features(X, y, k=2)
    assert selected[0] == "strong"
    assert len(selected) == 2
    assert list(scores.columns) == ["feature", "chi2", "p_value", "rank"]
    assert scores.iloc[0]["feature"] == "strong"


def test_weighted_random_forest_weights_sum_to_one_and_predicts():
    X_train = np.array([[0], [1], [2], [3], [4], [5]])
    y_train = np.array([0, 0, 0, 1, 1, 1])
    X_valid = np.array([[0], [1], [4], [5]])
    y_valid = np.array([0, 0, 1, 1])
    model = WeightedRandomForest(n_estimators=7, random_state=42, max_depth=3)
    model.fit(X_train, y_train, X_valid, y_valid)
    assert np.isclose(model.tree_weights_.sum(), 1.0)
    assert len(model.tree_weights_) == 7
    assert model.predict(np.array([[0], [5]])).tolist() == [0, 1]


def test_weighted_random_forest_preserves_string_labels():
    X_train = np.array([[0], [1], [2], [3], [4], [5]])
    y_train = np.array(["Normal", "Normal", "Normal", "Bot", "Bot", "Bot"])
    X_valid = np.array([[0], [1], [4], [5]])
    y_valid = np.array(["Normal", "Normal", "Bot", "Bot"])
    model = WeightedRandomForest(n_estimators=7, random_state=42, max_depth=3)
    model.fit(X_train, y_train, X_valid, y_valid)
    assert set(model.predict(np.array([[0], [5]]))) == {"Normal", "Bot"}


def test_weighted_random_forest_supports_weight_metrics():
    X = np.array([[0], [1], [2], [3], [4], [5]])
    y = np.array([0, 0, 0, 1, 1, 1])
    model = WeightedRandomForest(n_estimators=3, random_state=42, weight_metric="macro_f1").fit(X, y, X, y)
    assert np.isclose(model.tree_weights_.sum(), 1.0)


def test_compute_metrics_contains_macro_f1_and_accuracy():
    result = compute_metrics(np.array([0, 1, 1, 0]), np.array([0, 1, 0, 0]))
    assert set(["accuracy", "balanced_accuracy", "macro_precision", "macro_recall", "macro_f1"]).issubset(result)
    assert result["accuracy"] == 0.75
    assert result["balanced_accuracy"] == 0.75


def test_summarize_tree_weights_reports_uniformity():
    scores = np.array([0.8, 0.8, 0.8, 0.8])
    weights = np.array([0.25, 0.25, 0.25, 0.25])
    result = summarize_tree_weights(scores, weights)
    assert result["tree_count"] == 4
    assert np.isclose(result["weight_cv"], 0.0)
    assert np.isclose(result["normalized_weight_entropy"], 1.0)
