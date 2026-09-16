import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cic_manifest_has_complete_population_and_fit_boundaries():
    manifest = json.loads((ROOT / "results_rccf_cic_v1" / "run_manifest.json").read_text(encoding="utf-8"))
    required = {
        "dataset", "protocol_name", "balanced_research_subset_rows",
        "train_rows", "validation_rows", "test_rows", "calibration_rows",
        "class_counts", "feature_count_before_selection", "feature_count_after_selection",
        "deduplication_before_split", "feature_selection_fit_on", "risk_fit_on",
        "calibration_fit_on", "test_labels_used_for_fitting", "processed_hashes",
    }
    assert required <= manifest.keys()
    assert manifest["train_rows"] + manifest["validation_rows"] + manifest["test_rows"] == 3365
    assert manifest["feature_count_before_selection"] >= manifest["feature_count_after_selection"] >= 1
    assert set(manifest["class_counts"]) == {"train", "validation", "test"}
    assert all(len(value) == 5 for value in manifest["class_counts"].values())
    assert manifest["test_labels_used_for_fitting"] is False

