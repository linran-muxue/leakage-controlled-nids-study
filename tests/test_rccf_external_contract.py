import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _check_manifest(path, dataset):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "dataset", "independent_native_label_benchmark", "cross_dataset_transfer",
        "training_rows", "test_rows", "calibration_rows_per_seed",
        "native_labels", "training_label_counts", "test_label_counts",
        "source", "file_sha256", "test_labels_used_for_fitting",
    }
    assert required <= manifest.keys()
    assert manifest["dataset"] == dataset
    assert manifest["independent_native_label_benchmark"] is True
    assert manifest["cross_dataset_transfer"] is False
    assert sum(manifest["training_label_counts"].values()) == manifest["training_rows"]
    assert sum(manifest["test_label_counts"].values()) == manifest["test_rows"]
    assert len(manifest["native_labels"]) >= 2
    assert manifest["source"]["provider_url"].startswith("http")
    assert manifest["test_labels_used_for_fitting"] is False


def test_nsl_manifest_has_native_label_audit():
    _check_manifest(ROOT / "results_rccf_nsl_v1" / "run_manifest.json", "nsl")


def test_unsw_manifest_has_native_label_audit():
    _check_manifest(ROOT / "results_rccf_unsw_v1" / "run_manifest.json", "unsw")

