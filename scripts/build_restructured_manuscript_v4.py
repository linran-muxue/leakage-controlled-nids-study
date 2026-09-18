"""Render the restructured v4 manuscript and the advisor-facing restructure plan to DOCX."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "重构版论文_v4_20260915"

IMAGE_RE = re.compile(r"^!\[(?P<caption>[^\]]*)\]\((?P<path>[^)]+)\)\s*$")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
MATH_BLOCK_RE = re.compile(r"^\$\$.+\$\$\s*$")
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*]|\d+\.)\s+(?P<text>.*)$")

# Word restarts numbering per numId, so every numbered list needs its own. The
# default template defines decimal abstract numbering; we clone a new num per
# list, otherwise Word counts 1..N across the whole document and the fifth
# list starts at 10 (observed in the rendered PDF before this fix).
DECIMAL_ABSTRACT_ID = "7"


def next_num_id(doc: Document) -> str:
    numbering = doc.part.numbering_part.element
    ids = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    return str(max(ids, default=0) + 1)


def start_new_numbering(doc: Document) -> str:
    """Create a fresh numId that restarts at 1 and return it."""
    numbering = doc.part.numbering_part.element
    num_id = next_num_id(doc)
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), num_id)
    abstract = OxmlElement("w:abstractNumId")
    abstract.set(qn("w:val"), DECIMAL_ABSTRACT_ID)
    num.append(abstract)
    # Word keys counters by abstract definition, so a shared abstractNum alone
    # keeps counting across lists; the start override is what restarts it.
    override = OxmlElement("w:lvlOverride")
    override.set(qn("w:ilvl"), "0")
    start = OxmlElement("w:startOverride")
    start.set(qn("w:val"), "1")
    override.append(start)
    num.append(override)
    numbering.append(num)
    return num_id


def apply_numbering(paragraph, num_id: str) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    numPr = OxmlElement("w:numPr")
    level = OxmlElement("w:ilvl")
    level.set(qn("w:val"), "0")
    num = OxmlElement("w:numId")
    num.set(qn("w:val"), num_id)
    numPr.append(level)
    numPr.append(num)
    pPr.append(numPr)


def plan_numbered_lists(doc: Document, lines: list[str]) -> dict[int, str]:
    """Map each line of a numbered list to the numId that owns it.

    Consecutive numbered items share one numId; a blank line, a heading or any
    other content closes the list, so the next one restarts at 1.
    """
    mapping: dict[int, str] = {}
    current: str | None = None
    for index, raw in enumerate(lines):
        match = LIST_RE.match(raw)
        if match and match.group("marker") not in {"-", "*"}:
            if current is None:
                current = start_new_numbering(doc)
            mapping[index] = current
        else:
            current = None
    return mapping


def style_base(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        # Continuous line numbering, as commonly requested for review copies.
        sectPr = section._sectPr
        ln = sectPr.find(qn("w:lnNumType"))
        if ln is None:
            ln = sectPr.makeelement(qn("w:lnNumType"), {})
            sectPr.append(ln)
        ln.set(qn("w:countBy"), "1")
        ln.set(qn("w:restart"), "continuous")
        ln.set(qn("w:distance"), "360")
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.3


def add_runs(paragraph, text: str, base_bold: bool = False) -> None:
    """Render **bold**, *italic*, `code` and $math$ spans without leaking delimiters."""
    tokens = re.split(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\$[^$]+\$)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2]); run.bold = True
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            run = paragraph.add_run(token[1:-1]); run.italic = True
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
    three_line_table(table)
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


BORDER_EDGES = ("top", "bottom", "insideH")
def three_line_table(table) -> None:
    """Horizontal rules only: JISA asks to avoid vertical lines and shading."""
    tblPr = table._tbl.tblPr
    for existing in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(existing)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        if edge in BORDER_EDGES:
            element.set(qn("w:val"), "single")
            element.set(qn("w:sz"), "6")
            element.set(qn("w:space"), "0")
            element.set(qn("w:color"), "000000")
        else:
            element.set(qn("w:val"), "none")
            element.set(qn("w:sz"), "0")
            element.set(qn("w:space"), "0")
            element.set(qn("w:color"), "auto")
        borders.append(element)
    tblPr.append(borders)


def render(doc: Document, source: Path, numbered_ids: dict[int, str] | None = None) -> None:
    numbered_ids = numbered_ids or {}
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
            bullet = checklist.group("marker") in {"-", "*"}
            style = "List Bullet" if bullet else "List Number"
            p = doc.add_paragraph(style=style)
            add_runs(p, checklist.group("text"))
            if not bullet and i in numbered_ids:
                apply_numbering(p, numbered_ids[i])
            i += 1
            continue

        p = doc.add_paragraph()
        add_runs(p, stripped)
        i += 1


def build(source: Path, output: Path) -> Path:
    doc = Document()
    style_base(doc)
    numbered_ids = plan_numbered_lists(doc, source.read_text(encoding="utf-8").splitlines())
    render(doc, source, numbered_ids)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["manuscript", "english", "plan", "audit", "manual", "review", "selfcheck", "both", "all"], default="both")
    args = parser.parse_args()
    jobs = {
        "manuscript": (SRC / "中文SCI论文_v4_重构版.md", SRC / "中文SCI论文_v4_重构版.docx"),
        "plan": (SRC / "论文结构诊断与重构方案.md", SRC / "论文结构诊断与重构方案.docx"),
        "audit": (SRC / "研究缺口审计与优先级清单.md", SRC / "研究缺口审计与优先级清单.docx"),
        "manual": (SRC / "P0_P1执行手册.md", SRC / "P0_P1执行手册.docx"),
        "english": (SRC / "English_SCI_Manuscript_v4.md", SRC / "English_SCI_Manuscript_v4.docx"),
        "review": (SRC / "遗漏问题审查报告.md", SRC / "遗漏问题审查报告.docx"),
        "selfcheck": (SRC / "论文自查表.md", SRC / "论文自查表.docx"),
    }
    if args.only == "both":
        names = ["manuscript", "plan"]
    elif args.only == "all":
        names = ["manuscript", "english", "plan", "audit", "manual", "review", "selfcheck"]
    else:
        names = [args.only]
    for name in names:
        src, out = jobs[name]
        if not src.exists():
            raise FileNotFoundError(src)
        print(f"DOCX_WRITTEN={build(src, out)}")


if __name__ == "__main__":
    main()
