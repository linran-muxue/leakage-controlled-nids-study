import pandas as pd

from scripts.run_file_external_generalization_v1 import coverage_report, sample_file_frame


def test_coverage_report_separates_known_and_unseen_labels():
    result = coverage_report(["Normal", "Bot", "Web Attack"], ["Normal", "Bot"])
    assert result["known_labels"] == ["Bot", "Normal"]
    assert result["unseen_test_labels"] == ["Web Attack"]
    assert result["known_row_fraction"] == 2 / 3


def test_sample_file_frame_is_deterministic_and_per_class_capped():
    frame = pd.DataFrame({"target": ["Normal"] * 5 + ["Bot"] * 3, "f1": range(8)})
    out = sample_file_frame(frame, per_class_cap=2, seed=42)
    assert out["target"].value_counts().to_dict() == {"Normal": 2, "Bot": 2}
    assert out.equals(sample_file_frame(frame, per_class_cap=2, seed=42))
