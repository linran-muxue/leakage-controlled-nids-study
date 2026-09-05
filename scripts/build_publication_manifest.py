"""Build a SHA-256 manifest for canonical publication artifacts."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results_publication_final" / "MANIFEST.json"
TARGETS = [
    ROOT / "data_processed_audit_v4" / "dedup_audit.json",
    ROOT / "data_processed_audit_v4" / "train.csv",
    ROOT / "data_processed_audit_v4" / "validation.csv",
    ROOT / "data_processed_audit_v4" / "test.csv",
    ROOT / "results_publication_final" / "final_config.json",
    ROOT / "results_publication_final" / "external_data_metadata_template.json",
    ROOT / "results_publication_final" / "metrics_3seeds.csv",
    ROOT / "results_publication_final" / "metrics_aggregate.csv",
    ROOT / "results_publication_final" / "bootstrap_confidence_intervals.csv",
    ROOT / "results_publication_final" / "paired_significance_tests.csv",
    ROOT / "results_repeated_splits_v3" / "metrics.csv",
    ROOT / "results_repeated_splits_v3" / "paired_split_tests.csv",
    ROOT / "results_imbalanced_v3" / "metrics_3seeds.csv",
    ROOT / "results_weight_mechanism_v3" / "weight_mechanism_summary.csv",
    ROOT / "results_nsl_kdd_fair_v2" / "metrics.csv",
    ROOT / "results_additional_evidence_v4" / "method_comparison_summary.csv",
    ROOT / "results_additional_evidence_v4" / "deployment_latency_percentiles.csv",
    ROOT / "results_additional_evidence_v4" / "robustness_shared_perturbations.csv",
    ROOT / "results_additional_evidence_v4" / "calibration_curve_points.csv",
    ROOT / "results_paper_materials_v3" / "english_sci_manuscript_v1.md",
    ROOT / "results_paper_materials_v3" / "english_sci_manuscript_v1.docx",
    ROOT / "results_paper_materials_v3" / "Highlights_JISA.docx",
    ROOT / "results_paper_materials_v3" / "Highlights_JISA.txt",
    ROOT / "results_paper_materials_v3" / "Graphical_Abstract_JISA.png",
    ROOT / "results_paper_materials_v3" / "Graphical_Abstract_JISA.pdf",
    ROOT / "results_paper_materials_v3" / "supplementary_materials_index.md",
    ROOT / "results_paper_materials_v3" / "sci_strict_audit_v1.md",
    ROOT / "docs" / "sci_submission_readiness_checklist_v1.md",
    ROOT / "docs" / "jisa_submission_checklist_v1.md",
    ROOT / "docs" / "jisa_requirements_verified_2026-09-05.md",
    ROOT / "docs" / "data_terms_confirmation_2026-09-05.md",
    ROOT / "docs" / "public_code_release_plan.md",
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "docs" / "manual_verification_procedure_v1.md",
    ROOT / "results_paper_materials_v2" / "publication_readiness_audit.md",
    ROOT / "results_data_evidence_v1" / "data_evidence_summary.json",
    ROOT / "results_data_evidence_v1" / "data_evidence_report_v1.md",
    ROOT / "results_data_evidence_v1" / "cic_processing_retention.csv",
    ROOT / "results_data_evidence_v1" / "cic_file_label_coverage_with_fractions.csv",
    ROOT / "results_data_evidence_v1" / "cic_balanced_class_support.csv",
    ROOT / "results_data_evidence_v1" / "nsl_kdd_class_support.csv",
    ROOT / "results_data_evidence_v1" / "unsw_nb15_class_support.csv",
    ROOT / "results_unsw_nb15_independent_v4" / "metrics_3seeds.csv",
    ROOT / "results_unsw_nb15_independent_v4" / "metrics_aggregate.csv",
    ROOT / "results_unsw_nb15_independent_v4_seed2024" / "bootstrap_confidence_intervals.csv",
    ROOT / "results_unsw_nb15_independent_v4_seed42" / "bootstrap_confidence_intervals.csv",
    ROOT / "results_unsw_nb15_independent_v4_seed3407" / "bootstrap_confidence_intervals.csv",
    ROOT / "results_unsw_nb15_independent_v4_seed2024" / "predictions_rf_all.csv",
    ROOT / "results_unsw_nb15_independent_v4_seed2024" / "predictions_xgboost_chi2.csv",
    ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics.csv",
    ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics_aggregate.csv",
    ROOT / "results_paper_materials_v3" / "chapter4_unsw_revised.md",
    ROOT / "results_paper_materials_v3" / "full_paper_body_v6_data_processing.md",
    ROOT / "requirements-direct.txt",
    ROOT / "requirements-lock.txt",
]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    missing = [str(path) for path in TARGETS if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing canonical artifacts: " + ", ".join(missing))
    entries = []
    for path in TARGETS:
        entries.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)})
    document = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_repository": "https://github.com/linran-muxue/leakage-controlled-nids-study",
        "public_release_tag": "v1.0.2",
        "canonical_data": "data_processed_audit_v4",
        "canonical_main_results": "results_publication_final",
        "canonical_unsw_results": "results_unsw_nb15_independent_v4",
        "canonical_unsw_cross_split_sensitivity": "results_unsw_nb15_cross_split_sensitivity_v2",
        "canonical_manuscript": "results_paper_materials_v3/english_sci_manuscript_v1.docx",
        "artifacts": entries,
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MANIFEST_WRITTEN={OUTPUT}")


if __name__ == "__main__":
    main()
