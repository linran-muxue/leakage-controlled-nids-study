import numpy as np

from src.conformal_rejection import MondrianConformalRejector


def test_mondrian_rejector_returns_known_or_unknown_and_records_coverage():
    classes = np.array(["a", "b"])
    p_cal = np.array([[.9, .1], [.8, .2], [.2, .8], [.1, .9]])
    y_cal = np.array(["a", "a", "b", "b"])
    rejector = MondrianConformalRejector(alpha=0.5).fit(p_cal, y_cal, classes)
    p_test = np.array([[.9, .1], [.5, .5]])
    labels = rejector.predict(p_test)
    assert labels[0] in {"a", "b", "unknown"}
    assert labels[1] == "unknown"
    assert 0.0 < rejector.alpha <= 1.0


def test_mondrian_rejector_is_deterministic():
    p = np.array([[.7, .3], [.3, .7], [.6, .4], [.4, .6]])
    y = np.array(["a", "b", "a", "b"])
    a = MondrianConformalRejector(alpha=0.2).fit(p, y, np.array(["a", "b"]))
    b = MondrianConformalRejector(alpha=0.2).fit(p, y, np.array(["a", "b"]))
    np.testing.assert_array_equal(a.predict(p), b.predict(p))
