import json
from pathlib import Path

import pandas as pd

from scripts.run_cfrg_cic_v1 import run


def test_cfrg_cic_runner_emits_locked_artifacts(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    frame = pd.DataFrame({"f1": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], "f2": [1, 1, 0, 0] * 3, "target": ["a", "b"] * 6})
    frame.iloc[:6].to_csv(processed / "train.csv", index=False)
    frame.iloc[6:9].to_csv(processed / "validation.csv", index=False)
    frame.iloc[9:].to_csv(processed / "test.csv", index=False)
    out = tmp_path / "out"
    run(processed, out, chi2_k=2, n_estimators=7, min_samples_leaf=1, seeds=[3])
    protocol = json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    metrics = pd.read_csv(out / "metrics_3seeds.csv")
    assert protocol["gate_fit_on"] == "oob_training_predictions_only"
    assert protocol["test_usage"] == "locked_final_evaluation_only"
    assert {"equal_rf_chi2", "cfrg_forest_chi2"}.issubset(set(metrics["model"]))
    pred = pd.read_csv(out / "predictions" / "predictions_cfrg_forest_chi2_seed3.csv")
    assert any(col.startswith("proba__") for col in pred.columns)
