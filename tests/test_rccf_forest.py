import numpy as np
from sklearn.datasets import make_classification

from src.rccf_forest import RCCFForest


def test_rccf_returns_normalized_probabilities_and_native_labels():
    X, y = make_classification(n_samples=120, n_features=8, n_classes=3,
                               n_informative=5, random_state=7)
    labels = np.array([f"c{i}" for i in y])
    model = RCCFForest(n_estimators=15, cv=3, random_state=7, n_jobs=1)
    model.fit(X[:90], labels[:90], X[90:105], labels[90:105])
    p = model.predict_proba(X[105:])
    assert p.shape == (15, 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert set(model.predict(X[105:])).issubset(set(labels))


def test_rccf_keeps_test_rows_out_of_risk_fit():
    X, y = make_classification(n_samples=150, n_features=6, n_classes=3,
                               n_informative=4, random_state=11)
    model = RCCFForest(n_estimators=10, cv=3, random_state=11, n_jobs=1)
    model.fit(X[:100], y[:100], X[100:125], y[100:125])
    assert model.risk_training_rows_ == 100
    assert model.final_test_rows_seen_ == 0


def test_rccf_selective_prediction_has_consistent_shape():
    X, y = make_classification(n_samples=90, n_features=7, n_classes=3,
                               n_informative=4, random_state=5)
    model = RCCFForest(n_estimators=8, feature_k=4, cv=3, random_state=5, n_jobs=1)
    model.fit(X[:60], y[:60], X[60:75], y[60:75])
    labels, rejected = model.predict_selective(X[75:])
    assert labels.shape == rejected.shape == (15,)


def test_mutual_information_expert_is_reproducible_for_fixed_seed():
    X, y = make_classification(n_samples=120, n_features=12, n_classes=3,
                               n_informative=7, random_state=19)
    labels = np.array([f"c{i}" for i in y])
    a = RCCFForest(n_estimators=8, feature_k=6, cv=3, random_state=19, n_jobs=1)
    b = RCCFForest(n_estimators=8, feature_k=6, cv=3, random_state=19, n_jobs=1)
    a.fit(X[:90], labels[:90], X[90:105], labels[90:105])
    b.fit(X[:90], labels[:90], X[90:105], labels[90:105])
    a_mi = next(expert for expert in a.experts_ if expert["name"] == "mutual_info")
    b_mi = next(expert for expert in b.experts_ if expert["name"] == "mutual_info")
    assert np.array_equal(a_mi["selector"].get_support(), b_mi["selector"].get_support())
    assert np.allclose(a.predict_proba(X[105:]), b.predict_proba(X[105:]))
