"""Create a Chinese-organized full research archive.

Human-facing archive directories and selected documents use Chinese names.
Technical source/data filenames are retained where scripts or manifests depend
on them, so the extracted archive remains runnable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__"}
CANONICAL_DATA = {"data_processed_cic_natural_v3b", "data_processed_cic_balanced_v3b"}
CANONICAL_RESULTS = {
    "results_rccf_cic_natural_v3b", "results_rccf_cic_balanced_v3b",
    "results_cic_natural_baselines_v3b", "results_cic_balanced_baselines_v3b",
    "results_rccf_evidence_v3b", "results_file_external_generalization_v3b",
    "results_rccf_nsl_v2_final", "results_rccf_unsw_v2_final", "results_publication_final",
}
EXTERNAL_PREFIXES = ("results_nsl_", "results_unsw_", "results_cfrg_nsl", "results_cfrg_unsw", "results_drc_nsl", "results_drc_unsw")

CATEGORY_NAMES = {
    "00_project_root": "00_项目根目录",
    "01_submission_and_publication": "01_投稿与出版材料",
    "02_canonical_data": "02_核心数据",
    "03_canonical_results": "03_核心实验结果",
    "04_external_benchmarks": "04_外部数据集基准",
    "05_audits_and_evidence": "05_审计与证据",
    "06_code_and_tools": "06_代码与工具",
    "07_protocols_literature_and_journal": "07_协议文献与期刊材料",
    "08_historical_experiments": "08_历史实验记录",
    "09_loose_research_materials": "09_其他研究材料",
}

FILE_NAMES = {
    "README.md": "项目说明_README.md",
    "FULL_RESEARCH_ARCHIVE_README_20260912.md": "全量研究档案说明.md",
    "release_package_contents_v3b.md": "v3b发布包内容说明.md",
    "canonical_protocol_v2.md": "核心实验协议_v3b.md",
    "sci_claims_matrix_v1.md": "SCI主张与证据矩阵.md",
    "supplementary_materials_index.md": "补充材料目录.md",
    "cover_letter_template_en.md": "英文投稿附信模板.md",
    "Highlights_JISA.txt": "期刊亮点_Highlights.txt",
    "english_sci_manuscript_final.docx": "英文SCI论文_最终稿.docx",
    "english_sci_manuscript_final.md": "英文SCI论文_最终稿.md",
    "chinese_sci_manuscript_final.docx": "中文SCI论文_最终稿.docx",
    "chinese_sci_manuscript_final.md": "中文SCI论文_最终稿.md",
    "Graphical_Abstract_JISA.png": "图形摘要.png",
    "Graphical_Abstract_JISA.pdf": "图形摘要.pdf",
    "MANIFEST.json": "发布清单_MANIFEST.json",
    "requirements-direct.txt": "直接依赖_requirements.txt",
    "requirements-lock.txt": "锁定依赖_requirements-lock.txt",
    "LICENSE": "许可证_LICENSE.txt",
}


def excluded(path: Path, output: Path) -> bool:
    rel = path.relative_to(ROOT)
    if output.resolve() in path.resolve().parents or output.resolve() == path.resolve():
        return True
    if set(rel.parts) & EXCLUDE_DIRS:
        return True
    text = rel.as_posix()
    return (
        text.startswith("data/raw/")
        or text.startswith("data_external/UNSW-NB15/")
        or path.name.endswith((".zip", ".tar.gz", ".tgz"))
        or path.name.startswith("tmp_")
        or "/tmp_" in text
    )


def category(rel: Path) -> str:
    top = rel.parts[0]
    if top in {"results_paper_materials_v3", "results_publication_final"}:
        return "01_submission_and_publication"
    if top in CANONICAL_DATA:
        return "02_canonical_data/" + top
    if top in CANONICAL_RESULTS:
        return "03_canonical_results/" + top
    if top in {"data_external_nsl_kdd_processed", "data_external_nsl_kdd_processed_v2"}:
        return "04_external_benchmarks/processed_data/" + top
    if top.startswith(EXTERNAL_PREFIXES):
        return "04_external_benchmarks/results/" + top
    if top.startswith("results_data_") or top.startswith("results_file_"):
        return "05_audits_and_evidence/" + top
    if top in {"src", "scripts", "tests"}:
        return "06_code_and_tools/" + top
    if top == "docs":
        return "07_protocols_literature_and_journal/docs"
    if top.startswith("data_processed_"):
        return "08_historical_experiments/data/" + top
    if top.startswith("results_"):
        return "08_historical_experiments/results/" + top
    if top in {"README.md", "requirements-direct.txt", "requirements-lock.txt", "LICENSE", ".gitignore"}:
        return "00_project_root"
    return "09_loose_research_materials"


def archive_name(rel: Path, cat: str) -> str:
    cat_root = cat.split("/", 1)[0]
    translated = CATEGORY_NAMES[cat_root]
    suffix = cat.split("/", 1)[1] if "/" in cat else ""
    dest_dir = translated + ("/" + suffix if suffix else "")
    filename = FILE_NAMES.get(rel.name, rel.name)
    # Avoid flattening technical files; keep their project-relative location
    # below the translated category for traceability.
    return f"RCCF_完整研究档案_v2_20260912/{dest_dir}/{filename}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "RCCF_完整研究档案_v2_20260912.tar.gz")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    categories: Counter[str] = Counter()
    entries: list[dict[str, object]] = []
    with tarfile.open(args.output, "w:gz") as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or excluded(path, args.output):
                continue
            rel = path.relative_to(ROOT)
            cat = category(rel)
            arcname = archive_name(rel, cat)
            info = archive.gettarinfo(str(path), arcname=arcname)
            with path.open("rb") as handle:
                archive.addfile(info, handle)
            categories[cat] += 1
            entries.append({"source": rel.as_posix(), "archive_path": arcname, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "archive": args.output.name,
        "generated_date": "2026-09-12",
        "language": "Chinese-organized archive; technical filenames retained where required for reproducibility",
        "file_count": len(entries),
        "category_file_counts": dict(sorted(categories.items())),
        "canonical_data": sorted(CANONICAL_DATA),
        "canonical_results": sorted(CANONICAL_RESULTS),
        "excluded": ["data/raw/**", "data_external/UNSW-NB15/**", ".git/**", ".venv/**", "**/__pycache__/**", "**/.pytest_cache/**", "existing archives", "temporary tmp_* paths"],
        "entries": entries,
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    digest = sha256(args.output)
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {args.output.name}\n", encoding="utf-8")
    print(json.dumps({"archive": str(args.output), "manifest": str(manifest_path), "checksum": digest, "file_count": len(entries), "categories": dict(sorted(categories.items()))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
