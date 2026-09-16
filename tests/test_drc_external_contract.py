import numpy as np
import pandas as pd

from scripts.run_drc_forest_external_v1 import (
    make_train_validation_split,
    map_nsl_label,
    native_label_summary,
)


def test_training_validation_split_is_stratified_and_disjoint():
    X = pd.DataFrame({"f": np.arange(10)})
    y = np.array(["a"] * 5 + ["b"] * 5)
    train_idx, valid_idx = make_train_validation_split(y, valid_fraction=0.2, seed=3)
    assert set(train_idx).isdisjoint(set(valid_idx))
    assert len(train_idx) + len(valid_idx) == len(y)
    assert set(y[train_idx]) == {"a", "b"}
    assert set(y[valid_idx]) == {"a", "b"}


def test_native_label_summary_does_not_map_to_cic_labels():
    summary = native_label_summary(np.array(["Normal", "DoS", "Probe", "R2L", "U2R"]))
    assert summary["label_set"] == ["DoS", "Normal", "Probe", "R2L", "U2R"]
    assert summary["cross_dataset_transfer"] is False


def test_nsl_mapping_covers_native_attack_families_and_rejects_unknown():
    assert map_nsl_label("normal") == "Normal"
    assert map_nsl_label("neptune") == "DoS"
    assert map_nsl_label("satan") == "Probe"
    assert map_nsl_label("guess_passwd") == "R2L"
    assert map_nsl_label("buffer_overflow") == "U2R"
    try:
        map_nsl_label("unseen_attack_name")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown NSL-KDD attack must not be silently remapped")
