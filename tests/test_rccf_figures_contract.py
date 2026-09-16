from pathlib import Path

from scripts.build_rccf_figures_v1 import expected_figure_names


def test_rccf_figure_contract_is_explicit():
    names = expected_figure_names()
    assert len(names) == 6
    assert all(name.endswith(".png") for name in names)
    assert "fig_rccf_model_performance.png" in names
    assert "fig_rccf_latency_percentiles.png" in names

