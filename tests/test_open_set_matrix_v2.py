import numpy as np

from scripts.run_open_set_matrix_v2 import unknown_combinations, fpr_at_tpr, precision_recall_summary


def test_unknown_combinations_include_singletons_pairs_and_all_without_duplicates():
    combos = unknown_combinations(["PortScan", "Infiltration", "Heartbleed"])
    assert combos[0] == ["PortScan"]
    assert ["PortScan", "Infiltration"] in combos
    assert combos[-1] == ["PortScan", "Infiltration", "Heartbleed"]
    assert len({tuple(x) for x in combos}) == 7


def test_fpr_at_tpr_is_bounded_and_precision_recall_summary_is_finite():
    scores = np.array([0.01, 0.02, 0.4, 0.8, 0.9])
    truth = np.array([1, 1, 0, 0, 0])
    value = fpr_at_tpr(truth, scores, target_tpr=0.95)
    assert 0.0 <= value <= 1.0
    ap, recall = precision_recall_summary(truth, scores)
    assert 0.0 <= ap <= 1.0
    assert 0.0 <= recall <= 1.0
