import numpy as np

from src.open_set import reject_by_threshold, open_set_scores


def test_reject_by_threshold_marks_low_confidence_as_unknown():
    p = np.array([[0.8, 0.2], [0.55, 0.45], [0.1, 0.9]])
    labels = np.array(["a", "b"])
    out = reject_by_threshold(p, labels, threshold=0.7, unknown_label="unknown")
    assert out.tolist() == ["a", "unknown", "b"]


def test_open_set_scores_contains_unknown_recall_and_auc():
    y = np.array(["a", "unknown", "b", "unknown"])
    p = np.array([[.9, .1], [.6, .4], [.2, .8], [.55, .45]])
    out = open_set_scores(y, p, known_labels=np.array(["a", "b"]), threshold=.7)
    assert 0 <= out["unknown_recall"] <= 1
    assert 0 <= out["unknown_auroc"] <= 1
