"""Build the canonical SHA-256 manifest for the RCCF publication package."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results_publication_final" / "MANIFEST.json"

TARGETS = [
    ROOT / "data_processed_cic_natural_v3b" / "dedup_audit.json",
    ROOT / "data_processed_cic_natural_v3b" / "preprocess_config.json",
    ROOT / "data_processed_cic_natural_v3b" / "dataset_summary.csv",
    ROOT / "data_processed_cic_natural_v3b" / "train.csv",
    ROOT / "data_processed_cic_natural_v3b" / "validation.csv",
    ROOT / "data_processed_cic_natural_v3b" / "test.csv",
    ROOT / "data_processed_cic_natural_v3b" / "train_source_provenance.csv",
    ROOT / "data_processed_cic_natural_v3b" / "validation_source_provenance.csv",
    ROOT / "data_processed_cic_natural_v3b" / "test_source_provenance.csv",
    ROOT / "results_rccf_cic_natural_v3b" / "run_manifest.json",
    ROOT / "results_rccf_cic_natural_v3b" / "metrics_by_seed.csv",
    ROOT / "results_rccf_cic_natural_v3b" / "metrics_aggregate.csv",
    ROOT / "results_cic_natural_baselines_v3b" / "metrics_3seeds.csv",
    ROOT / "results_cic_natural_baselines_v3b" / "metrics_aggregate_flat.csv",
    ROOT / "results_data_audit_cic_natural_v3b" / "data_processing_audit.json",
    ROOT / "results_data_audit_cic_natural_v3b" / "raw_file_stage_counts.csv",
    ROOT / "results_data_audit_cic_natural_v3b" / "source_file_split_label_counts.csv",
    ROOT / "results_data_quality_cic_natural_v3b" / "data_quality_summary.json",
    ROOT / "results_data_quality_cic_natural_v3b" / "data_quality_summary.csv",
    ROOT / "results_data_quality_cic_natural_v3b" / "class_support.csv",
    ROOT / "data_processed_cic_balanced_v3b" / "dedup_audit.json",
    ROOT / "data_processed_cic_balanced_v3b" / "preprocess_config.json",
    ROOT / "data_processed_cic_balanced_v3b" / "dataset_summary.csv",
    ROOT / "data_processed_cic_balanced_v3b" / "train.csv",
    ROOT / "data_processed_cic_balanced_v3b" / "validation.csv",
    ROOT / "data_processed_cic_balanced_v3b" / "test.csv",
    ROOT / "results_data_audit_cic_balanced_v3b" / "data_processing_audit.json",
    ROOT / "results_data_quality_cic_balanced_v3b" / "data_quality_summary.json",
    ROOT / "results_data_quality_cic_balanced_v3b" / "class_support.csv",
    ROOT / "docs" / "canonical_protocol_v2.md",
    ROOT / "results_rccf_cic_balanced_v3b" / "run_manifest.json",
    ROOT / "results_rccf_cic_balanced_v3b" / "metrics_by_seed.csv",
    ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv",
    ROOT / "results_cic_balanced_baselines_v3b" / "metrics_3seeds.csv",
    ROOT / "results_cic_balanced_baselines_v3b" / "metrics_aggregate_flat.csv",
    ROOT / "results_rccf_nsl_v2_final" / "run_manifest.json",
    ROOT / "results_rccf_nsl_v2_final" / "metrics_by_seed.csv",
    ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv",
    ROOT / "results_rccf_nsl_v2_final" / "class_counts_seed2024.csv",
    ROOT / "results_rccf_unsw_v2_final" / "run_manifest.json",
    ROOT / "results_rccf_unsw_v2_final" / "metrics_by_seed.csv",
    ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv",
    ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "protocol.json",
    ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics.csv",
    ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics_aggregate.csv",
    ROOT / "results_rccf_evidence_v3b" / "evidence_manifest.json",
    ROOT / "results_rccf_evidence_v3b" / "model_metrics.csv",
    ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv",
    ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv",
    ROOT / "results_rccf_evidence_v3b" / "paired_bootstrap_macro_f1.csv",
    ROOT / "results_rccf_evidence_v3b" / "macro_f1_paired_tests.csv",
    ROOT / "results_rccf_evidence_v3b" / "file_label_coverage.csv",
    ROOT / "results_rccf_evidence_v3b" / "file_label_matrix.csv",
    ROOT / "results_file_external_generalization_v3b" / "file_external_results.csv",
    ROOT / "results_file_external_generalization_v3b" / "protocol.json",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_model_performance.png",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_calibration.png",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_robustness.png",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_latency_percentiles.png",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_file_label_coverage.png",
    ROOT / "results_publication_final" / "figures" / "fig_rccf_confusion_matrix.png",
    ROOT / "src" / "rccf_forest.py",
    ROOT / "src" / "rccf_metrics.py",
    ROOT / "src" / "conformal_rejection.py",
    ROOT / "scripts" / "run_rccf_cic_v1.py",
    ROOT / "scripts" / "run_rccf_external_v1.py",
    ROOT / "scripts" / "analyze_rccf_evidence_v1.py",
    ROOT / "scripts" / "build_rccf_figures_v1.py",
    ROOT / "scripts" / "build_final_manuscripts_v1.py",
    ROOT / "results_paper_materials_v3" / "english_sci_manuscript_final.md",
    ROOT / "results_paper_materials_v3" / "english_sci_manuscript_final.docx",
    ROOT / "results_paper_materials_v3" / "chinese_sci_manuscript_final.md",
    ROOT / "results_paper_materials_v3" / "chinese_sci_manuscript_final.docx",
    ROOT / "docs" / "final_submission_gate_v2_2026-09-11.md",
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "requirements-direct.txt",
    ROOT / "requirements-lock.txt",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    missing = [str(path) for path in TARGETS if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing canonical RCCF artifacts: " + ", ".join(missing))
    entries = [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)} for path in TARGETS]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_repository": "https://github.com/linran-muxue/leakage-controlled-nids-study",
        "public_release_tag": "v1.0.2",
        "canonical_data": "data_processed_cic_natural_v3b",
        "canonical_main_results": "results_rccf_cic_natural_v3b",
        "canonical_control_data": "data_processed_cic_balanced_v3b",
        "canonical_control_results": "results_rccf_cic_balanced_v3b",
        "canonical_external_results": ["results_rccf_nsl_v2_final", "results_rccf_unsw_v2_final"],
        "canonical_evidence": "results_rccf_evidence_v3b",
        "canonical_manuscript": "results_paper_materials_v3/english_sci_manuscript_final.docx",
        "method": "RCCF (Risk-Calibrated Conformal Forest)",
        "claim_boundary": "No universal superiority claim; external datasets are independent native-label benchmarks",
        "artifacts": entries,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MANIFEST_WRITTEN={OUTPUT}")


if __name__ == "__main__":
    main()
