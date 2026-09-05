import numpy as np

from src.nested_evaluation import nested_split_indices, select_features_fold, make_candidate_specs


def test_nested_split_indices_are_disjoint_and_cover_rows():
    y = np.array(["a", "b"] * 15)
    folds = nested_split_indices(y, outer_splits=3, inner_splits=2, seed=42)
    assert len(folds) == 3
    covered = []
    for outer_train, outer_test, inner_folds in folds:
        assert set(outer_train).isdisjoint(set(outer_test))
        covered.extend(outer_test.tolist())
        assert len(inner_folds) == 2
        for inner_train, inner_valid in inner_folds:
            assert set(inner_train).isdisjoint(set(inner_valid))
            assert set(inner_train).issubset(set(outer_train))
            assert set(inner_valid).issubset(set(outer_train))
    assert sorted(covered) == list(range(len(y)))


def test_select_features_fold_uses_only_requested_training_rows():
    x = np.array([[0, 1, 2], [1, 0, 1], [0, 2, 0], [2, 0, 1]], dtype=float)
    y = np.array(["a", "b", "a", "b"])
    idx = select_features_fold(x, y, k=2)
    assert idx.shape == (2,)
    assert np.all((idx >= 0) & (idx < 3))


def test_candidate_specs_have_explicit_feature_modes():
    specs = make_candidate_specs(seed=42, n_classes=2)
    assert {name for name, _, mode, _ in specs} == {"random_forest", "extra_trees", "xgboost"}
    assert {mode for _, _, mode, _ in specs} == {"all", "chi2"}
