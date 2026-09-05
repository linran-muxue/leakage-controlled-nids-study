import numpy as np

from src.sci_baselines import build_model_candidates, select_train_features, evaluate_predictions


def test_model_candidates_include_xgboost_and_tree_baselines():
    candidates = build_model_candidates(seed=42)
    names = [name for name, _, _ in candidates]
    assert names == ["random_forest", "extra_trees", "xgboost"]
    assert {mode for _, _, mode in candidates} == {"all", "chi2"}


def test_select_train_features_returns_only_requested_indices():
    x = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [0.0, 2.0, 0.0], [2.0, 0.0, 1.0]])
    y = np.array(["a", "b", "a", "b"])
    idx = select_train_features(x, y, k=2)
    assert idx.shape == (2,)
    assert np.all((idx >= 0) & (idx < x.shape[1]))


def test_evaluate_predictions_returns_probability_metrics():
    y = np.array(["a", "b", "a", "b"])
    pred = np.array(["a", "b", "b", "b"])
    proba = np.array([[.8, .2], [.1, .9], [.4, .6], [.2, .8]])
    out = evaluate_predictions(y, pred, proba, np.array(["a", "b"]))
    assert set(["accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro", "ece"]).issubset(out)
    assert 0 <= out["log_loss"]
