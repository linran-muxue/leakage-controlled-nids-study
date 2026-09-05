import numpy as np
import pandas as pd

from scripts.run_unsw_nb15_independent_v1 import probability_metrics, load_native


def test_unsw_probability_metrics_returns_probability_quality_fields():
    y = np.array(["a", "b", "a", "b"])
    p = np.array([[.8, .2], [.1, .9], [.7, .3], [.2, .8]])
    out = probability_metrics(y, p, np.array(["a", "b"]))
    assert {"log_loss", "brier_macro", "ece"}.issubset(out)
    assert out["log_loss"] >= 0


def test_unsw_encoding_fits_categorical_levels_on_training_only(tmp_path):
    columns = ["id", "proto", "attack_cat"]
    train = pd.DataFrame([[1, "tcp", "Normal"], [2, "udp", "DoS"]], columns=columns)
    test = pd.DataFrame([[3, "icmp", "Normal"], [4, "tcp", "DoS"]], columns=columns)
    train.to_csv(tmp_path / "UNSW-NB15_training-set.csv", index=False)
    test.to_csv(tmp_path / "UNSW-NB15_testing-set.csv", index=False)
    x_train, y_train, x_test, y_test = load_native(tmp_path)
    assert x_train.shape[1] == x_test.shape[1]
    # The test-only category must not create a feature column.
    assert x_train.shape[1] == 3


def test_unsw_loader_excludes_binary_label_when_attack_cat_is_target(tmp_path):
    columns = ["id", "proto", "attack_cat", "label"]
    train = pd.DataFrame(
        [[1, "tcp", "Normal", 0], [2, "udp", "DoS", 1]],
        columns=columns,
    )
    test = pd.DataFrame(
        [[3, "tcp", "Normal", 0], [4, "udp", "DoS", 1]],
        columns=columns,
    )
    train.to_csv(tmp_path / "UNSW-NB15_training-set.csv", index=False)
    test.to_csv(tmp_path / "UNSW-NB15_testing-set.csv", index=False)

    x_train, _, x_test, _ = load_native(tmp_path)

    # Only proto should be encoded: two levels plus the dummy-NA column.
    # If the binary target label leaks into the feature matrix, this shape
    # becomes larger than three columns.
    assert x_train.shape == (2, 3)
    assert x_test.shape == (2, 3)


def test_unsw_label_encoder_does_not_use_test_only_classes():
    # This test documents the protocol requirement: test labels must be
    # checked against, not used to fit, the training label encoder.
    from scripts.run_unsw_nb15_independent_v1 import fit_label_encoder
    with np.testing.assert_raises(ValueError):
        fit_label_encoder(np.array(["Normal"]), np.array(["Unknown"]))
