import pandas as pd

from src.data_pipeline import map_attack_label, clean_numeric_features
from src.prepare_dataset import collect_balanced_sample


def test_map_attack_label_main_five_class_scheme():
    labels = [
        "BENIGN", "DDoS", "DoS Hulk", "FTP-Patator", "SSH-Patator",
        "Web Attack – XSS", "Bot", "PortScan", "Infiltration", "Heartbleed"
    ]
    result = [map_attack_label(label, include_other=False) for label in labels]
    assert result == [
        "Normal", "DoS/DDoS", "DoS/DDoS", "Brute Force", "Brute Force",
        "Web Attack", "Bot", None, None, None
    ]


def test_map_attack_label_extension_maps_unselected_to_other():
    assert map_attack_label("PortScan", include_other=True) == "Other"
    assert map_attack_label("Infiltration", include_other=True) == "Other"
    assert map_attack_label("Heartbleed", include_other=True) == "Other"


def test_clean_numeric_features_replaces_infinite_and_drops_invalid_rows():
    frame = pd.DataFrame({
        "a": [1.0, float("inf"), 3.0, None],
        "b": [4.0, 5.0, float("-inf"), 8.0],
    })
    cleaned = clean_numeric_features(frame)
    assert len(cleaned) == 1
    assert cleaned.iloc[0].to_dict() == {"a": 1.0, "b": 4.0}


def test_collect_balanced_sample_deduplicates_globally_before_balancing(tmp_path):
    columns = ["f1", "f2", " Label"]
    first = pd.DataFrame([[1, 2, "BENIGN"], [3, 4, "BENIGN"], [5, 6, "Bot"]], columns=columns)
    second = pd.DataFrame([[1, 2, "BENIGN"], [3, 4, "Bot"], [7, 8, "Bot"]], columns=columns)
    first.to_csv(tmp_path / "a.csv", index=False)
    second.to_csv(tmp_path / "b.csv", index=False)
    # The current protocol removes cross-label conflicts before balancing.
    # With balancing disabled, the two exact duplicates and the conflicting
    # feature vector leave three unique, non-conflicting records.
    frame, _, audit = collect_balanced_sample(
        tmp_path,
        per_class_cap=10,
        include_other=False,
        seed=42,
        chunksize=10,
        balance=False,
    )
    assert len(frame) == 3
    assert audit["duplicate_rows"] == 2
    assert audit["cross_label_conflicts"] == 1
    assert audit["cross_label_conflict_hashes"] == 1
    assert audit["unique_rows_before_conflict"] == 4
    assert audit["unique_rows_after_conflict"] == 3
    assert audit["same_label_duplicate_rows"] == 1
    assert audit["cross_label_mismatch_rows"] == 1
    assert audit["conflicting_feature_hash_count"] == 1
    assert audit["rows_in_conflicting_groups"] == 2
    assert audit["unique_rows_removed_for_conflicts"] == 1
    assert audit["dedup_fingerprint_bits"] == 128
    assert audit["dedup_fingerprint_method"] == "pandas_hash_forward_and_reversed_columns"
    assert frame.drop(columns=["target"]).duplicated().sum() == 0


def test_conflict_audit_counts_all_rows_in_a_conflicting_group(tmp_path):
    columns = ["f1", "f2", " Label"]
    frame = pd.DataFrame(
        [
            [1, 2, "BENIGN"],
            [1, 2, "BENIGN"],
            [1, 2, "Bot"],
            [1, 2, "Bot"],
            [3, 4, "BENIGN"],
        ],
        columns=columns,
    )
    frame.to_csv(tmp_path / "a.csv", index=False)
    sampled, _, audit = collect_balanced_sample(
        tmp_path,
        per_class_cap=10,
        include_other=False,
        seed=42,
        chunksize=2,
        balance=False,
    )
    assert len(sampled) == 1
    assert audit["duplicate_rows"] == 3
    assert audit["same_label_duplicate_rows"] == 1
    assert audit["cross_label_mismatch_rows"] == 2
    assert audit["conflicting_feature_hash_count"] == 1
    assert audit["rows_in_conflicting_groups"] == 4
    assert audit["unique_rows_removed_for_conflicts"] == 1


def test_collect_sample_can_preserve_unequal_class_sizes(tmp_path):
    columns = ["f1", "f2", " Label"]
    frame = pd.DataFrame([[i, i + 1, "BENIGN"] for i in range(5)] + [[20, 21, "Bot"]], columns=columns)
    frame.to_csv(tmp_path / "a.csv", index=False)
    sampled, _, audit = collect_balanced_sample(tmp_path, per_class_cap=10, include_other=False, seed=42, chunksize=10, balance=False)
    counts = sampled["target"].value_counts().to_dict()
    assert counts["Normal"] == 5 and counts["Bot"] == 1
    assert audit["balanced_rows"] == 6


def test_per_class_cap_is_global_across_chunks(tmp_path):
    columns = ["f1", "f2", " Label"]
    frame = pd.DataFrame([[i, i + 1, "BENIGN"] for i in range(6)] + [[100 + i, 101 + i, "Bot"] for i in range(6)], columns=columns)
    frame.to_csv(tmp_path / "a.csv", index=False)
    sampled, _, _ = collect_balanced_sample(tmp_path, per_class_cap=3, include_other=False, seed=42, chunksize=2, balance=False)
    counts = sampled["target"].value_counts().to_dict()
    assert counts["Normal"] == 3 and counts["Bot"] == 3


def test_source_row_ids_are_global_within_each_file(tmp_path):
    columns = ["f1", "f2", " Label"]
    frame = pd.DataFrame([[i, i + 1, "BENIGN"] for i in range(6)], columns=columns)
    frame.to_csv(tmp_path / "a.csv", index=False)
    sampled, _, _ = collect_balanced_sample(tmp_path, per_class_cap=10, include_other=False, seed=42, chunksize=2, balance=False)
    ids = sampled["_source_row_id"].tolist()
    assert sorted(ids) == list(range(6))
