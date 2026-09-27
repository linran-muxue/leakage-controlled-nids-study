"""Build a reorganized full research archive without copying raw datasets.

The archive is created directly from the working tree, so no temporary 1--2 GB
staging copy is required. Existing files are never removed or modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DATA = {
    "data_processed_cic_natural_v3b",
    "data_processed_cic_balanced_v3b",
}
CANONICAL_RESULTS = {
    "results_rccf_cic_natural_v3b",
    "results_rccf_cic_balanced_v3b",
    "results_cic_natural_baselines_v3b",
    "results_cic_balanced_baselines_v3b",
    "results_rccf_evidence_v3b",
    "results_file_external_generalization_v3b",
    "results_rccf_nsl_v2_final",
    "results_rccf_unsw_v2_final",
    "results_publication_final",
}
EXTERNAL_RESULTS_PREFIXES = (
    "results_nsl_",
    "results_unsw_",
    "results_cfrg_nsl",
    "results_cfrg_unsw",
    "results_drc_nsl",
    "results_drc_unsw",
)
EXCLUDE_DIR_NAMES = {".git", ".venv", ".pytest_cache", "__pycache__"}


def is_excluded(path: Path, output: Path) -> bool:
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)
    if output.resolve() == path.resolve() or output.resolve() in path.resolve().parents:
        return True
    if parts & EXCLUDE_DIR_NAMES:
        return True
    rel_text = rel.as_posix()
    if rel_text.startswith("data/raw/") or rel_text.startswith("data_external/UNSW-NB15/"):
        return True
    if path.name.endswith((".zip", ".tar.gz", ".tgz")):
        return True
    if path.name.startswith("tmp_") or "/tmp_" in rel_text:
        return True
    return False


def category(rel: Path) -> str:
    top = rel.parts[0]
    if top in {"results_paper_materials_v3", "results_publication_final"}:
        return "01_submission_and_publication"
    if top in CANONICAL_DATA:
        return f"02_canonical_data/{top}"
    if top in CANONICAL_RESULTS:
        return f"03_canonical_results/{top}"
    if top == "data_external_nsl_kdd_processed" or top == "data_external_nsl_kdd_processed_v2":
        return f"04_external_benchmarks/processed_data/{top}"
    if top.startswith(EXTERNAL_RESULTS_PREFIXES):
        return f"04_external_benchmarks/results/{top}"
    if top.startswith("results_data_") or top.startswith("results_file_"):
        return f"05_audits_and_evidence/{top}"
    if top in {"src", "scripts", "tests"}:
        return f"06_code_and_tools/{top}"
    if top == "docs":
        return "07_protocols_literature_and_journal/docs"
    if top.startswith("data_processed_"):
        return f"08_historical_experiments/data/{top}"
    if top.startswith("results_"):
        return f"08_historical_experiments/results/{top}"
    if top in {"requirements-direct.txt", "requirements-lock.txt", "LICENSE", "README.md", ".gitignore"}:
        return "00_project_root"
    return "09_loose_research_materials"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build(output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    bytes_by_category: Counter[str] = Counter()
    entries: list[dict[str, object]] = []
    with tarfile.open(output, mode="w:gz") as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or is_excluded(path, output):
                continue
            rel = path.relative_to(ROOT)
            cat = category(rel)
            arcname = f"RCCF_FULL_RESEARCH_ARCHIVE_v2_20260912/{cat}/{rel.as_posix()}"
            info = archive.gettarinfo(str(path), arcname=arcname)
            with path.open("rb") as handle:
                archive.addfile(info, handle)
            counts[cat] += 1
            bytes_by_category[cat] += path.stat().st_size
            entries.append({"source": rel.as_posix(), "archive_path": arcname, "bytes": path.stat().st_size, "sha256": digest(path)})
    manifest = {
        "archive": output.name,
        "generated_date": "2026-09-12",
        "protocol": "v3b",
        "file_count": len(entries),
        "category_file_counts": dict(sorted(counts.items())),
        "category_source_bytes": dict(sorted(bytes_by_category.items())),
        "excluded": [
            "data/raw/**",
            "data_external/UNSW-NB15/**",
            ".git/**",
            ".venv/**",
            "**/__pycache__/**",
            "**/.pytest_cache/**",
            "existing *.zip and *.tar.gz archives",
            "temporary tmp_* paths",
        ],
        "canonical": {
            "data": sorted(CANONICAL_DATA),
            "results": sorted(CANONICAL_RESULTS),
        },
        "entries": entries,
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "RCCF_FULL_RESEARCH_ARCHIVE_v2_20260912.tar.gz")
    args = parser.parse_args()
    manifest = build(args.output)
    checksum = digest(args.output)
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    checksum_path.write_text(f"{checksum}  {args.output.name}\n", encoding="utf-8")
    print(json.dumps({"archive": str(args.output), "manifest": str(args.output.with_suffix(args.output.suffix + '.manifest.json')), "checksum": checksum, "file_count": manifest["file_count"], "categories": manifest["category_file_counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
