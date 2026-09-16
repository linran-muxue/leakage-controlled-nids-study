import json

import numpy as np
import pandas as pd

from scripts.run_drc_forest_cic_v1 import build_protocol, write_prediction_artifact


def test_protocol_records_locked_data_boundary_and_method_parameters(tmp_path):
    args = type(
        "Args",
        (),
        {
            "processed_dir": tmp_path / "processed",
            "output_dir": tmp_path / "results",
            "chi2_k": 60,
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_leaf": 2,
            "seeds": [42, 2024, 3407],
            "cost_beta": 0.5,
            "cost_min": 0.5,
            "cost_max": 2.0,
        },
    )()
    protocol = build_protocol(args, n_train=10, n_valid=3, n_test=4, n_features=78, selected_count=60)
    assert protocol["data_boundary"] == "train_validation_test"
    assert protocol["feature_selection_fit_on"] == "training_only"
    assert protocol["reliability_fit_on"] == "validation_only"
    assert protocol["class_cost_fit_on"] == "training_only"
    assert protocol["chi2_k"] == 60
    assert protocol["n_estimators"] == 100


def test_prediction_artifact_preserves_row_alignment_and_probability_columns(tmp_path):
    out = tmp_path / "pred.csv"
    y_true = np.array(["Normal", "Bot"])
    y_pred = np.array(["Normal", "Bot"])
    classes = np.array(["Bot", "Normal"])
    proba = np.array([[0.1, 0.9], [0.8, 0.2]])
    write_prediction_artifact(out, y_true, y_pred, proba, classes)

    frame = pd.read_csv(out)
    assert list(frame.columns) == ["row_id", "y_true", "y_pred", "proba__Bot", "proba__Normal"]
    assert frame["row_id"].tolist() == [0, 1]
    np.testing.assert_allclose(frame[["proba__Bot", "proba__Normal"]].sum(axis=1), [1.0, 1.0])

