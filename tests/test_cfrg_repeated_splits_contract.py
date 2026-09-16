import pandas as pd

from scripts.run_cfrg_repeated_splits_v1 import run_repeated


def test_repeated_runner_emits_split_level_effects(tmp_path):
    processed = tmp_path / "p"; processed.mkdir()
    frame = pd.DataFrame({"f1": [0, 1] * 20, "f2": [1, 0] * 20, "target": ["a", "b"] * 20})
    frame.to_csv(processed / "all.csv", index=False)
    out = tmp_path / "o"
    run_repeated(processed, out, split_seeds=[1, 2], n_estimators=5, chi2_k=2)
    assert (out / "metrics.csv").exists()
    frame_out = pd.read_csv(out / "metrics.csv")
    assert {"equal_rf", "cfrg_forest"}.issubset(set(frame_out.model))
    assert (out / "paired_split_tests.csv").exists()
