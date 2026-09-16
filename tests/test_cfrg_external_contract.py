import json
from pathlib import Path

import pandas as pd

from scripts.run_cfrg_external_v1 import run_unsw


def test_external_runner_preserves_training_boundary_and_outputs_probability_artifacts(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    train = pd.DataFrame({"id": range(12), "proto": ["tcp", "udp"] * 6, "dur": [0.1, 0.2] * 6, "attack_cat": ["Normal", "DoS"] * 6, "label": [0, 1] * 6})
    test = pd.DataFrame({"id": range(12, 20), "proto": ["tcp", "icmp"] * 4, "dur": [0.3, 0.4] * 4, "attack_cat": ["Normal", "DoS"] * 4, "label": [0, 1] * 4})
    train.to_csv(raw / "UNSW-NB15_training-set.csv", index=False)
    test.to_csv(raw / "UNSW-NB15_testing-set.csv", index=False)
    out = tmp_path / "out"
    run_unsw(raw, out, k=2, n_estimators=7, seeds=[3])
    protocol = json.loads((out / "seed_3" / "protocol.json").read_text(encoding="utf-8"))
    assert protocol["official_train_test_boundary"] is True
    assert protocol["cross_dataset_transfer"] is False
    assert protocol["encoding_fit_on"] == "official_training_only"
    metrics = pd.read_csv(out / "seed_3" / "metrics.csv")
    assert "log_loss" in metrics.columns and "brier_macro" in metrics.columns
    assert (out / "seed_3" / "predicted_class_counts_cfrg_forest_chi2.csv").exists()
