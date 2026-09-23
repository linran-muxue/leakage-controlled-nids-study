"""Unit tests for the audit scripts added during the release hardening.

The four scripts run as gate checks, but until now their detection logic was
only ever exercised against the repository's own (healthy) data, so nothing
proved they fail when they should. These tests drive the importable parts with
synthetic inputs, including the exact failure each script was written to catch.
The end-to-end runs stay in the gate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from src.audit_utils import count_shared_rows, feature_row_hashes  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aggregation = _load("check_metrics_aggregation_v1")
released = _load("audit_released_evidence_v1")
checksums = _load("record_cic_csv_hashes_v1")


# ---------------------------------------------------------------- record_cic_csv_hashes_v1

def test_sha256_streams_the_whole_file(tmp_path: Path) -> None:
    payload = b"abc" * 400_000  # crosses the 1 MiB read block
    path = tmp_path / "sample.csv"
    path.write_bytes(payload)
    assert checksums.sha256(path) == hashlib.sha256(payload).hexdigest()


def test_sha256_matches_the_published_vector(tmp_path: Path) -> None:
    path = tmp_path / "abc.csv"
    path.write_bytes(b"abc")
    assert checksums.sha256(path) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


# ---------------------------------------------------------------- audit_released_evidence_v1

def _rccf_run(tmp_path: Path, *, macro_f1_delta: float = 0.0) -> Path:
    directory = tmp_path / "results_fake_v1"
    directory.mkdir()
    frame = pd.DataFrame({
        "true_label": ["A", "A", "B", "B"],
        "predicted_label": ["A", "B", "B", "B"],
    })
    frame.to_csv(directory / "predictions_seed42.csv", index=False)
    stored = {
        "macro_f1": f1_score(frame["true_label"], frame["predicted_label"],
                             average="macro", zero_division=0) + macro_f1_delta,
        "accuracy": accuracy_score(frame["true_label"], frame["predicted_label"]),
    }
    pd.DataFrame([stored]).to_csv(directory / "metrics_seed42.csv", index=False)
    return directory


def test_released_evidence_accepts_matching_metrics(tmp_path: Path) -> None:
    released.problems.clear()
    released.check_rccf(_rccf_run(tmp_path))
    assert released.problems == []


def test_released_evidence_flags_a_stale_macro_f1(tmp_path: Path) -> None:
    released.problems.clear()
    released.check_rccf(_rccf_run(tmp_path, macro_f1_delta=0.01))
    assert released.problems, "a metrics file that disagrees with its predictions must be flagged"
    assert "macro_f1" in released.problems[0]


def test_released_evidence_flags_a_stale_baseline_accuracy(tmp_path: Path) -> None:
    directory = tmp_path / "results_fake_baselines_v1"
    directory.mkdir()
    frame = pd.DataFrame({"y_true": ["A", "B", "B"], "y_pred": ["A", "A", "B"]})
    frame.to_csv(directory / "predictions_equal_rf_chi2_seed42.csv", index=False)
    pd.DataFrame([{
        "model": "equal_rf_chi2",
        "seed": 42,
        "macro_f1": f1_score(frame["y_true"], frame["y_pred"], average="macro", zero_division=0),
        "accuracy": accuracy_score(frame["y_true"], frame["y_pred"]) - 0.05,
    }]).to_csv(directory / "metrics_by_seed.csv", index=False)
    released.problems.clear()
    released.check_baselines(directory)
    assert released.problems, "a baseline accuracy that disagrees with its predictions must be flagged"
    assert "accuracy" in released.problems[0]


# ---------------------------------------------------------------- check_metrics_aggregation_v1

def _metrics_tree(tmp_path: Path, aggregate_rows: int) -> Path:
    directory = tmp_path / "results_fake_v1"
    directory.mkdir()
    for seed in (42, 2024, 3407):
        (directory / f"metrics_seed{seed}.csv").write_text("macro_f1\n0.9\n", encoding="utf-8")
    pd.DataFrame([{"macro_f1": 0.9} for _ in range(aggregate_rows)]).to_csv(
        directory / "metrics_by_seed.csv", index=False)
    return tmp_path


def test_metrics_aggregation_detects_a_truncated_aggregate(tmp_path: Path) -> None:
    rows, problems = aggregation.scan(_metrics_tree(tmp_path, aggregate_rows=1))
    assert rows == [("results_fake_v1", 3, 1, "TRUNCATED")]
    assert problems and "3 per-seed files" in problems[0]


def test_metrics_aggregation_accepts_a_complete_aggregate(tmp_path: Path) -> None:
    rows, problems = aggregation.scan(_metrics_tree(tmp_path, aggregate_rows=3))
    assert rows == [("results_fake_v1", 3, 3, "ok")]
    assert problems == []


def test_metrics_aggregation_ignores_directories_without_per_seed_files(tmp_path: Path) -> None:
    (tmp_path / "results_empty_v1").mkdir()
    rows, problems = aggregation.scan(tmp_path)
    assert rows == [] and problems == []


# ---------------------------------------------------------------- audit_full_corpus_data_v1

def test_exact_hashes_keep_rows_that_rounding_would_merge() -> None:
    """The audit hashes float64 bits because rounding reported phantom overlaps."""
    train = pd.DataFrame({"x": [1.0000001], "target": ["A"]})
    test = pd.DataFrame({"x": [1.0000002], "target": ["B"]})
    exact = count_shared_rows(set(feature_row_hashes(train, ["x"])),
                              feature_row_hashes(test, ["x"]))
    rounded = count_shared_rows(set(feature_row_hashes(train.round(6), ["x"])),
                                feature_row_hashes(test.round(6), ["x"]))
    assert exact == 0
    assert rounded == 1


def test_count_shared_rows_counts_only_shared_values() -> None:
    assert count_shared_rows({1, 2, 3}, [3, 4, 3]) == 2
    assert count_shared_rows(set(), [1, 2]) == 0
