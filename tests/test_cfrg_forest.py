import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from src.cfrg_forest import (
    CFRGForest,
    tree_descriptor_tensor,
    tree_oob_mask,
    tree_probability_tensor,
)


def _toy_data():
    rng = np.random.default_rng(123)
    X = rng.normal(size=(80, 4))
    y = np.array(["normal"] * 40 + ["attack"] * 40)
    X[40:, 0] += 1.5
    return X, y


def test_tree_tensor_shapes_and_descriptors_are_finite():
    X, y = _toy_data()
    base = RandomForestClassifier(n_estimators=7, random_state=4, n_jobs=1).fit(X, y)
    probs = tree_probability_tensor(base, X)
    desc = tree_descriptor_tensor(probs)
    assert probs.shape == (80, 7, 2)
    assert desc.shape == (80, 7, 4)
    np.testing.assert_allclose(probs.sum(axis=2), np.ones((80, 7)))
    assert np.isfinite(desc).all()


def test_oob_mask_is_deterministic_and_has_oob_rows():
    X, y = _toy_data()
    base = RandomForestClassifier(n_estimators=11, random_state=4, n_jobs=1).fit(X, y)
    first = tree_oob_mask(base, len(X))
    second = tree_oob_mask(base, len(X))
    assert first.shape == (80, 11)
    np.testing.assert_array_equal(first, second)
    assert first.sum(axis=1).min() >= 1


def test_descriptor_agreement_respects_optional_tree_mask():
    probs = np.array(
        [
            [[0.9, 0.1], [0.1, 0.9], [0.9, 0.1]],
        ],
        dtype=float,
    )
    full = tree_descriptor_tensor(probs)
    masked = tree_descriptor_tensor(probs, valid_mask=np.array([[True, False, True]]))
    assert full[0, 1, 3] == 0.0
    assert masked[0, 0, 3] == 1.0
    assert masked[0, 2, 3] == 1.0


def test_cfrg_gate_is_sample_conditional_and_deterministic():
    X, y = _toy_data()
    first = CFRGForest(n_estimators=17, random_state=9, n_jobs=1, temperature=1.0).fit(X, y)
    second = CFRGForest(n_estimators=17, random_state=9, n_jobs=1, temperature=1.0).fit(X, y)
    p1 = first.predict_proba(X[:12])
    p2 = second.predict_proba(X[:12])
    np.testing.assert_allclose(p1, p2)
    np.testing.assert_allclose(p1.sum(axis=1), np.ones(12))
    assert np.isfinite(p1).all()
    assert first.gate_diagnostics_["changed_weight_fraction"] > 0.0
    assert first.gate_diagnostics_["oob_coverage_min"] >= 1


def test_cfrg_cost_beta_zero_has_unit_costs_and_original_labels():
    X, y = _toy_data()
    model = CFRGForest(n_estimators=9, random_state=2, n_jobs=1, cost_beta=0.0).fit(X, y)
    assert set(model.predict(X[:3])).issubset(set(y))
    np.testing.assert_allclose(model.class_costs_, np.ones(2))


def test_cfrg_rejects_non_bootstrap_forest():
    X, y = _toy_data()
    with pytest.raises(ValueError, match="bootstrap"):
        CFRGForest(n_estimators=3, random_state=1, bootstrap=False).fit(X, y)


def test_tree_probability_tensor_aligns_string_forest_and_integer_tree_labels():
    """Regression guard for sklearn trees exposing encoded integer classes."""
    X, y = _toy_data()
    forest = RandomForestClassifier(n_estimators=5, random_state=12, n_jobs=1).fit(X, y)
    # Simulate the encoded class metadata observed in some sklearn versions.
    original = forest.estimators_[0].classes_.copy()
    forest.estimators_[0].classes_ = np.arange(len(original), dtype=float)
    tensor = tree_probability_tensor(forest, X[:10])
    assert tensor.shape == (10, 5, len(forest.classes_))
    np.testing.assert_allclose(tensor.sum(axis=2), np.ones((10, 5)))
    assert list(forest.classes_) == ["attack", "normal"]
    forest.estimators_[0].classes_ = original
