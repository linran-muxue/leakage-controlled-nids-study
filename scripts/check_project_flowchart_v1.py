"""Verify the project flowchart the way the manuscripts are verified.

The chart is a deliverable in its own right and it quotes numbers about the
repository (gate size, archive size, figure and table counts), so a stale copy
would quietly disagree with the artefacts it describes.  Three things are
checked: the builder still runs and its text-fit assertions hold, the committed
PNG and Markdown are byte-for-byte what the builder produces today, and the Word
copy still names all six stages.

Rebuild with ``scripts/build_project_flowchart_v1.py`` followed by
``scripts/build_restructured_manuscript_v4.py --only flowchart`` on a mismatch.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402
from docx import Document  # noqa: E402

STAGES = ("① 数据获取", "② 数据处理", "③ 建模与对照", "④ 评估", "⑤ 机制分析", "⑥ 论文与交付")


def main() -> int:
    problems: list[str] = []
    png = BASE / "figures_project" / "flow_project.png"
    pdf = BASE / "figures_project" / "flow_project.pdf"
    markdown = BASE / "项目流程图.md"
    word = BASE / "项目流程图.docx"
    for path in (png, pdf, markdown, word):
        if not path.exists():
            problems.append(f"missing artefact: {path.name}")
    if problems:
        print("FLOWCHART_FAILED: " + "; ".join(problems))
        return 1
    if pdf.read_bytes()[:4] != b"%PDF":
        problems.append(f"{pdf.name} does not start with %PDF")
    if png.stat().st_size < 100_000:
        problems.append(f"{png.name} is only {png.stat().st_size} bytes")

    # Re-render into a scratch directory.  The builder asserts that all 32 text
    # blocks fit their panels and reads its numbers from the artefacts, so a
    # successful run is also the freshness proof for the committed files.
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run([PY, str(ROOT / "scripts" / "build_project_flowchart_v1.py"),
                               "--outdir", tmp], cwd=ROOT, capture_output=True, text=True,
                              errors="replace")
        combined = proc.stdout + proc.stderr
        if proc.returncode != 0:
            problems.append("the builder failed: " + " ".join(combined.split())[-260:])
        else:
            fresh = Path(tmp)
            if (fresh / "flow_project.png").read_bytes() != png.read_bytes():
                problems.append("figures_project/flow_project.png is stale: rebuild it with "
                                "scripts/build_project_flowchart_v1.py")
            if (fresh / "项目流程图.md").read_text("utf-8") != markdown.read_text("utf-8"):
                problems.append("项目流程图.md is stale: rebuild it with "
                                "scripts/build_project_flowchart_v1.py")

    document = Document(str(word))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                text += "\n" + cell.text
    for stage in STAGES:
        if stage not in text:
            problems.append(f"项目流程图.docx does not name the stage {stage}")
    if "figures_project/flow_project.pdf" not in text:
        problems.append("项目流程图.docx does not point at the vector version")

    if problems:
        print("FLOWCHART_FAILED: " + "; ".join(problems))
        return 1
    print(f"FLOWCHART_OK stages={len(STAGES)} gate={counts.gate_checks()} "
          f"png={png.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
