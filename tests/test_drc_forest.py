import numpy as np
import pandas as pd

from src.drc_forest import DRCForest


def _toy_data():
    X = pd.DataFrame(
        {
            "x1": [0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "x2": [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1],
        }
    )
    y = np.array(["a", "a", "b", "b", "a", "b", "a", "b", "a", "b", "a", "b"])
    return X.iloc[:8], y[:8], X.iloc[8:], y[8:]


def test_class_conditional_reliability_and_weights_have_expected_shape():
    X, y, X_valid, y_valid = _toy_data()
    model = DRCForest(n_estimators=9, random_state=7, n_jobs=1)
    model.fit(X, y, X_valid, y_valid)

    assert model.reliability_.shape == (9, 2)
    assert model.tree_class_weights_.shape == (9, 2)
    np.testing.assert_allclose(model.tree_class_weights_.sum(axis=0), np.ones(2))
    assert np.isfinite(model.reliability_).all()


def test_predict_proba_is_finite_and_row_normalized_and_deterministic():
    X, y, X_valid, y_valid = _toy_data()
    first = DRCForest(n_estimators=11, random_state=11, n_jobs=1).fit(X, y, X_valid, y_valid)
    second = DRCForest(n_estimators=11, random_state=11, n_jobs=1).fit(X, y, X_valid, y_valid)

    p1 = first.predict_proba(X_valid)
    p2 = second.predict_proba(X_valid)
    assert p1.shape == (len(X_valid), 2)
    assert np.isfinite(p1).all()
    np.testing.assert_allclose(p1.sum(axis=1), np.ones(len(X_valid)))
    np.testing.assert_allclose(p1, p2)
    np.testing.assert_array_equal(first.predict(X_valid), second.predict(X_valid))


def test_balanced_training_counts_make_costs_near_one():
    X, y, X_valid, y_valid = _toy_data()
    model = DRCForest(n_estimators=5, random_state=3, n_jobs=1, cost_beta=1.0)
    model.fit(X, y, X_valid, y_valid)

    np.testing.assert_allclose(model.class_costs_, np.ones(2), atol=1e-12)

