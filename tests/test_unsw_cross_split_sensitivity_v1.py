import pandas as pd

from scripts.run_unsw_cross_split_sensitivity_v1 import build_overlap_masks, normalize_key_frame


def test_overlap_masks_exclude_only_feature_key_matches_and_ignore_id_label_columns():
    train = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "f": ["1.0000000000001", "2", "3"],
            "proto": ["tcp", "udp", "tcp"],
            "label": [1, 1, 1],
            "attack_cat": ["Normal", "DoS", "Normal"],
        }
    )
    test = pd.DataFrame(
        {
            "id": [1, 9, 10],
            "f": ["1.0000000000002", "2", "8"],
            "proto": ["tcp", "udp", "tcp"],
            "label": [1, 0, 0],
            "attack_cat": ["Normal", "DoS", "Normal"],
        }
    )
    cols = ["f", "proto"]
    train_norm = normalize_key_frame(train, cols)
    test_norm = normalize_key_frame(test, cols)
    train_mask, test_mask, stats = build_overlap_masks(train_norm, test_norm, train["attack_cat"], test["attack_cat"])
    assert train_mask.tolist() == [True, True, False]
    assert test_mask.tolist() == [True, True, False]
    assert stats["common_keys"] == 2
    assert stats["same_label_keys"] == 2


def test_empty_frame_has_stable_key_shape():
    frame = pd.DataFrame(columns=["f", "proto"])
    out = normalize_key_frame(frame, ["f", "proto"])
    assert list(out.columns) == ["f", "proto"]
    assert out.empty
