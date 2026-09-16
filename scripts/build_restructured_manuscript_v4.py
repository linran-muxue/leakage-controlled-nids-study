"""Render the restructured v4 manuscript and the advisor-facing restructure plan to DOCX."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "重构版论文_v4_20260915"

IMAGE_RE = re.compile(r"^!\[(?P<caption>[^\]]*)\]\((?P<path>[^)]+)\)\s*$")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
MATH_BLOCK_RE = re.compile(r"^\$\$.+\$\$\s*$")
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*]|\d+\.)\s+(?P<text>.*)$")


def style_base(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.3


def add_runs(paragraph, text: str, base_bold: bool = False) -> None:
    """Render **bold**, `code` and $math$ spans without leaking delimiters."""
    tokens = re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\$[^$]+\$)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2]); run.bold = True
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1]); run.font.name = "Consolas"
        elif token.startswith("$") and token.endswith("$") and len(token) > 1:
            run = paragraph.add_run(token[1:-1]); run.font.name = "Cambria Math"
        else:
            run = paragraph.add_run(token)
        if base_bold:
            run.bold = True


def add_caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(9)
    run.italic = True
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)


def add_markdown_table(doc: Document, rows: list[list[str]]) -> None:
    cols = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=cols)
    table.style = "Table Grid"
    for r_index, row in enumerate(rows):
        cells = table.add_row().cells
        for c_index in range(cols):
            text = row[c_index] if c_index < len(row) else ""
            cells[c_index].text = ""
            para = cells[c_index].paragraphs[0]
            para.paragraph_format.space_after = Pt(0)
            add_runs(para, text, base_bold=(r_index == 0))
            for run in para.runs:
                run.font.size = Pt(8)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def render(doc: Document, source: Path) -> None:
    lines = source.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            for text in block:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                run = p.add_run(text)
                run.font.name = "Consolas"
                run.font.size = Pt(8.5)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue

        image = IMAGE_RE.match(stripped)
        if image:
            path = (source.parent / image.group("path")).resolve()
            if path.exists():
                doc.add_picture(str(path), width=Inches(6.3))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_caption(doc, image.group("caption"))
            else:
                add_caption(doc, f"[缺图] {image.group('caption')} -> {path}")
            i += 1
            continue

        if TABLE_ROW_RE.match(stripped):
            rows: list[list[str]] = []
            while i < len(lines) and TABLE_ROW_RE.match(lines[i].strip()):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                add_markdown_table(doc, rows)
            continue

        if MATH_BLOCK_RE.match(stripped):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped.strip("$").strip())
            run.font.name = "Cambria Math"
            run.font.size = Pt(11)
            i += 1
            continue

        if line.startswith("# "):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
            i += 1
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
            i += 1
            continue
        if stripped == "---":
            i += 1
            continue

        checklist = LIST_RE.match(line)
        if checklist:
            style = "List Bullet" if checklist.group("marker") in {"-", "*"} else "List Number"
            p = doc.add_paragraph(style=style)
            add_runs(p, checklist.group("text"))
            i += 1
            continue

        p = doc.add_paragraph()
        add_runs(p, stripped)
        i += 1


def build(source: Path, output: Path) -> Path:
    doc = Document()
    style_base(doc)
    render(doc, source)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["manuscript", "english", "plan", "audit", "manual", "review", "both", "all"], default="both")
    args = parser.parse_args()
    jobs = {
        "manuscript": (SRC / "中文SCI论文_v4_重构版.md", SRC / "中文SCI论文_v4_重构版.docx"),
        "plan": (SRC / "论文结构诊断与重构方案.md", SRC / "论文结构诊断与重构方案.docx"),
        "audit": (SRC / "研究缺口审计与优先级清单.md", SRC / "研究缺口审计与优先级清单.docx"),
        "manual": (SRC / "P0_P1执行手册.md", SRC / "P0_P1执行手册.docx"),
        "english": (SRC / "English_SCI_Manuscript_v4.md", SRC / "English_SCI_Manuscript_v4.docx"),
        "review": (SRC / "遗漏问题审查报告.md", SRC / "遗漏问题审查报告.docx"),
    }
    if args.only == "both":
        names = ["manuscript", "plan"]
    elif args.only == "all":
        names = ["manuscript", "english", "plan", "audit", "manual", "review"]
    else:
        names = [args.only]
    for name in names:
        src, out = jobs[name]
        if not src.exists():
            raise FileNotFoundError(src)
        print(f"DOCX_WRITTEN={build(src, out)}")


if __name__ == "__main__":
    main()
