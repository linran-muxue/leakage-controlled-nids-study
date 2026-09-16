import json

import pandas as pd

from scripts.run_cfrg_calibration_v1 import run_calibration


def test_calibration_runner_emits_before_after_metrics(tmp_path):
    processed = tmp_path / "processed"; processed.mkdir()
    frame = pd.DataFrame({"f1": [0, 1] * 12, "f2": [1, 0] * 12, "target": ["a", "b"] * 12})
    frame.iloc[:12].to_csv(processed / "train.csv", index=False)
    frame.iloc[12:18].to_csv(processed / "validation.csv", index=False)
    frame.iloc[18:].to_csv(processed / "test.csv", index=False)
    out = tmp_path / "out"
    run_calibration(processed, out, n_estimators=5, chi2_k=2, seeds=[3])
    protocol = json.loads((out / "protocol.json").read_text())
    assert protocol["temperature_fit_on"] == "validation_only"
    metrics = pd.read_csv(out / "metrics.csv")
    assert {"uncalibrated", "temperature_scaled"}.issubset(set(metrics["variant"]))
