import pandas as pd

from src.parameter_selection import choose_best_k


def test_choose_best_k_uses_validation_macro_f1_only():
    table = pd.DataFrame({
        "k": [10, 20, 30],
        "validation_macro_f1": [0.80, 0.92, 0.90],
        "validation_accuracy": [0.81, 0.91, 0.89],
    })
    assert choose_best_k(table) == 20


def test_choose_best_k_requires_tie_break_metric():
    table = pd.DataFrame({"k": [10], "validation_macro_f1": [0.8]})
    try:
        choose_best_k(table)
    except ValueError:
        return
    raise AssertionError("validation accuracy is required for deterministic tie-breaking")
