import pandas as pd

from scripts.audit_data_processing_v1 import audit_frame, summarize_split, file_hash


def test_audit_frame_reports_stage_counts_and_invalid_reasons():
    frame = pd.DataFrame({
        "Flow ID": ["a", "b", "c", "d"],
        "f1": [1.0, float("inf"), None, 2.0],
        "f2": [2.0, 3.0, 4.0, 2.0],
        " Label": ["BENIGN", "Bot", "Bot", "PortScan"],
    })
    result = audit_frame(frame)
    assert result["source_rows"] == 4
    assert result["mapped_rows"] == 3
    assert result["invalid_rows"] == 2
    assert result["invalid_infinite_rows"] == 1
    assert result["invalid_missing_rows"] == 1
    assert result["excluded_label_rows"] == 1
    assert result["class_counts"]["Normal"] == 1
    assert result["feature_columns"] == ["f1", "f2"]
    assert set(result["raw_label_counts"]) == {"BENIGN", "Bot", "PortScan"}


def test_summarize_split_reports_schema_and_label_counts():
    frame = pd.DataFrame({"target": ["Normal", "Bot", "Bot"], "f1": [1, 2, 3]})
    result = summarize_split(frame, "train")
    assert result["split"] == "train"
    assert result["rows"] == 3
    assert result["feature_count"] == 1
    assert result["class_counts"]["Bot"] == 2


def test_file_hash_records_size_and_digest(tmp_path):
    path = tmp_path / "x.csv"
    path.write_bytes(b"abc")
    result = file_hash(path)
    assert result["bytes"] == 3
    assert len(result["md5"]) == 32 and len(result["sha256"]) == 64
