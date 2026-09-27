"""Verify the material index covers the project and matches the shipped archive.

The index claims three things: every top-level item of the workspace is
accounted for, the archive really carries the groups it promises, and the Word
copy is the current document.  All three are checked here; a new top-level file
or directory that nobody classified fails the gate.

Rebuild with ``scripts/build_material_index_v1.py`` (after repackaging) and
``scripts/build_restructured_manuscript_v4.py --only materials`` on a mismatch.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DOC = BASE / "材料完整性清单.md"
WORD = BASE / "材料完整性清单.docx"
ARCHIVE = ROOT / "submission_package" / "论文投稿包_v1.11.0.zip"
ANCHORS = ("材料完整性清单", "随投稿包分发", "本地保留", "明确排除",
           "docs/source_records", "figures_experiments")
# groups the archive must carry beyond the documents themselves
REQUIRED_FOLDERS = ("07_复现材料/元数据", "07_复现材料/ci", "07_复现材料/docs",
                    "07_复现材料/tests", "07_复现材料/退役材料", "07_复现材料/发布快照",
                    "07_复现材料/归档索引", "07_复现材料/实验代码",
                    "07_复现材料/figures_experiments", "07_复现材料/实验日志")


def main() -> int:
    from docx import Document

    problems: list[str] = []
    for path in (DOC, WORD, ARCHIVE):
        if not path.exists():
            problems.append(f"missing artefact: {path.name}")
    if problems:
        print("MATERIAL_INDEX_FAILED: " + "; ".join(problems))
        return 1

    text = DOC.read_text(encoding="utf-8")
    results_dirs = sorted(p.name for p in ROOT.glob("results_*") if p.is_dir())
    local_results = [name for name in results_dirs if name != "results_publication_final"]
    aggregated = f"（{len(local_results)} 个结果目录）"
    if aggregated not in text:
        problems.append(f"the index does not aggregate the {len(local_results)} local "
                        "results_* directories")
    for entry in sorted(ROOT.iterdir()):
        if entry.name in local_results and aggregated in text:
            continue
        if f"`{entry.name}`" not in text:
            problems.append(f"top-level item not accounted for in the index: {entry.name}")

    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
    for folder in REQUIRED_FOLDERS:
        if not any(name.startswith(f"论文投稿包_v1.11.0/{folder}/") for name in names):
            problems.append(f"the archive does not carry {folder}")
    counts: dict[str, int] = {}
    for name in names:
        parts = name.split("/")
        key = parts[1] if len(parts) > 1 else "(root)"
        counts[key] = counts.get(key, 0) + 1
    for folder, count in counts.items():
        if f"| `{folder}` | {count} |" not in text:
            problems.append(f"the index states a wrong entry count for {folder} "
                            f"(archive has {count})")

    body = "\n".join(paragraph.text for paragraph in Document(str(WORD)).paragraphs)
    for table in Document(str(WORD)).tables:
        for row in table.rows:
            for cell in row.cells:
                body += "\n" + cell.text
    for anchor in ANCHORS:
        if anchor not in body:
            problems.append(f"材料完整性清单.docx lost the anchor {anchor!r}")

    if problems:
        print("MATERIAL_INDEX_FAILED: " + "; ".join(problems[:6]))
        return 1
    print(f"MATERIAL_INDEX_OK top_level={len(list(ROOT.iterdir()))} archive_entries={len(names)} "
          f"folders={len(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
