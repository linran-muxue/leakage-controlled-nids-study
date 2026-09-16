import json
import pandas as pd

from scripts.run_cfrg_open_set_v1 import run_open_set


def test_open_set_runner_records_validation_only_threshold(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    known = pd.DataFrame({"f1": [0, 0, 1, 1] * 4, "f2": [1, 1, 0, 0] * 4, "target": ["Normal", "Normal", "Bot", "Bot"] * 4, "raw_label": ["BENIGN"] * 8 + ["Bot"] * 8})
    unknown = pd.DataFrame({"f1": [0.4, 0.6, 0.5, 0.7], "f2": [0.5, 0.4, 0.6, 0.3], "target": ["unknown"] * 4, "raw_label": ["PortScan"] * 4})
    known.to_csv(raw / "known.csv", index=False)
    unknown.to_csv(raw / "unknown.csv", index=False)
    out = tmp_path / "out"
    run_open_set(raw, out, per_group=100, seeds=[3], n_estimators=7)
    protocol = json.loads((out / "seed_3" / "protocol.json").read_text())
    assert protocol["unknown_rows_used_for_threshold"] is False
    assert (out / "seed_3" / "open_set_metrics.csv").exists()
    metrics = pd.read_csv(out / "seed_3" / "open_set_metrics.csv")
    assert {"model", "unknown_recall", "auroc"}.issubset(metrics.columns)
