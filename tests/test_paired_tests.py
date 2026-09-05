import numpy as np

from src.paired_tests import mcnemar_exact


def test_mcnemar_exact_counts_discordant_pairs():
    result = mcnemar_exact(np.array([0, 1, 1, 0]), np.array([0, 1, 0, 0]), np.array([0, 1, 1, 1]))
    assert result["a_only_correct"] == 1
    assert result["b_only_correct"] == 1
    assert 0 <= result["p_value"] <= 1
