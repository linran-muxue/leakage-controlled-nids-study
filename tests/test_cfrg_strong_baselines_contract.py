import pandas as pd

from scripts.run_cfrg_strong_baselines_v1 import run_strong_baselines


def test_strong_baseline_runner_has_common_protocol_and_models(tmp_path):
    processed = tmp_path / "p"; processed.mkdir()
    frame = pd.DataFrame({"f1": [0, 1] * 20, "f2": [1, 0] * 20, "target": ["a", "b"] * 20})
    frame.iloc[:24].to_csv(processed / "train.csv", index=False)
    frame.iloc[24:32].to_csv(processed / "validation.csv", index=False)
    frame.iloc[32:].to_csv(processed / "test.csv", index=False)
    out = tmp_path / "o"
    run_strong_baselines(processed, out, seeds=[3], n_estimators=5, chi2_k=2, use_xgboost=False)
    metrics = pd.read_csv(out / "metrics.csv")
    assert {"equal_rf", "extra_trees", "cfrg_forest"}.issubset(set(metrics.model))
    assert {"accuracy", "balanced_accuracy", "macro_f1", "log_loss"}.issubset(metrics.columns)
