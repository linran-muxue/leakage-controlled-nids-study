import json

import pandas as pd

from scripts.run_cfrg_nsl_v1 import run_nsl


def test_nsl_runner_preserves_native_labels_and_metrics(tmp_path):
    train = pd.DataFrame({"f1": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1], "f2": [1, 1, 0, 0, 1, 1, 0, 0, 1, 1], "target": ["Normal", "DoS", "Normal", "DoS", "Probe", "R2L", "Probe", "R2L", "U2R", "Normal"]})
    test = pd.DataFrame({"f1": [0, 1, 0, 1, 0], "f2": [1, 0, 0, 1, 1], "target": ["Normal", "DoS", "Probe", "R2L", "U2R"]})
    raw = tmp_path / "processed"; raw.mkdir(); train.to_csv(raw / "train.csv", index=False); test.to_csv(raw / "test.csv", index=False)
    out = tmp_path / "out"
    run_nsl(raw, out, k=2, n_estimators=5, seeds=[3])
    protocol = json.loads((out / "seed_3" / "protocol.json").read_text())
    assert protocol["native_labels"] is True and protocol["cross_dataset_transfer"] is False
    metrics = pd.read_csv(out / "seed_3" / "metrics.csv")
    assert {"balanced_accuracy", "log_loss", "brier_macro"}.issubset(metrics.columns)
    assert (out / "seed_3" / "predicted_class_counts_cfrg_forest_chi2.csv").exists()
