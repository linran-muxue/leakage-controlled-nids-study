"""Add external dataset audit artifacts to the canonical manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results_publication_final" / "MANIFEST.json"


def digest(path: Path) -> dict:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": h.hexdigest()}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {item["path"] for item in data.get("artifacts", [])}
    files = [
        ROOT / "results_unsw_nb15_audit" / "audit_v2.json",
        ROOT / "results_unsw_nb15_audit" / "cross_split_overlap_audit.json",
        ROOT / "results_unsw_nb15_independent_v3" / "metrics_aggregate.csv",
        ROOT / "results_unsw_nb15_independent_v3" / "bootstrap_ci_seed2024_1000.csv",
        ROOT / "results_unsw_nb15_cross_split_sensitivity_v1" / "metrics.csv",
        ROOT / "results_unsw_nb15_cross_split_sensitivity_v1" / "metrics_aggregate.csv",
        ROOT / "results_unsw_nb15_cross_split_sensitivity_v1" / "protocol.json",
        ROOT / "results_open_set_matrix_v2" / "open_set_matrix_metrics.csv",
        ROOT / "results_open_set_matrix_v2" / "protocol.json",
        ROOT / "results_publication_final" / "external_data_metadata_template.json",
        ROOT / "results_paper_materials_v3" / "tables" / "table_data_source_provenance_v1.csv",
        ROOT / "docs" / "data_source_audit_report_2026-09-05.md",
        ROOT / "docs" / "source_records" / "screenshot_observations_2026-09-05.md",
        ROOT / "docs" / "source_records" / "cic_ids2017_source_2026-09-05.png",
        ROOT / "docs" / "source_records" / "nsl_kdd_mirror_2026-09-05.png",
        ROOT / "docs" / "source_records" / "unsw_nb15_source_2026-09-05.png",
        ROOT / "results_paper_materials_v3" / "english_sci_manuscript_v1.md",
        ROOT / "results_paper_materials_v3" / "english_sci_manuscript_v1.docx",
        ROOT / "results_paper_materials_v3" / "cover_letter_template_en.md",
        ROOT / "requirements-direct.txt",
        ROOT / "docs" / "sci_submission_readiness_checklist_v1.md",
    ]
    for path in files:
        item = digest(path)
        if item["path"] not in existing:
            data["artifacts"].append(item)
    data["external_data_audits"] = {
        "UNSW-NB15": "results_unsw_nb15_audit/cross_split_overlap_audit.json",
        "NSL-KDD": "results_nsl_kdd_fair_v2/metrics.csv",
    }
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MANIFEST_UPDATED={MANIFEST}")


if __name__ == "__main__":
    main()
