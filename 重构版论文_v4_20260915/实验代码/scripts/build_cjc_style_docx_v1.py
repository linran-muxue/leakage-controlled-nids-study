"""Render the 计算机学报-styled Chinese manuscript to DOCX.

Style profile taken from the sample PDF (2025, Vol. 48 No. 9):

  page        A4, two-column body, single-column front matter
  title       黑体 19.7 pt, centred
  level 1     黑体 13.1 pt ("1 引 言")
  level 2     黑体 9.7 pt ("2.1 ...")
  level 3     bold 9.7 pt ("3.3.1 ...")
  body        宋体/Times 9 pt, justified, first-line indent 2 em
  captions    8.2 pt; 图n below the figure, 表n above the table
  tables      three-line (thick top/bottom, thin under the header)
  references  7.5 pt, hanging indent, "[n] ..."
  abstract    8.2 pt with a bold 黑体 label

The journal prints its body at 7.3 pt; this draft uses 9 pt so the Word file
stays readable, with the two-column geometry preserved.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SOURCE = BASE / "中文SCI论文_计算机学报排版版.md"
OUT = BASE / "中文SCI论文_计算机学报排版版.docx"

HEI = "黑体"
SONG = "宋体"
WEST = "Times New Roman"



BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def inline_parts(text: str) -> list[tuple[str, bool]]:
    """Split "plain **bold** plain" into runs so no Markdown marker survives."""
    parts, last = [], 0
    for match in BOLD_RE.finditer(text):
        if match.start() > last:
            parts.append((text[last:match.start()], False))
        parts.append((match.group(1), True))
        last = match.end()
    if last < len(text):
        parts.append((text[last:], False))
    return parts or [(text, False)]


def style_run(run, size: float, cjk: str, bold: bool = False) -> None:
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = WEST
    run.font.color.rgb = RGBColor(0, 0, 0)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    fonts.set(qn("w:eastAsia"), cjk)


def paragraph(doc, text: str, size: float, cjk: str = SONG, bold: bool = False,
              align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent: float = 0.0,
              space_before: float = 0.0, space_after: float = 2.0,
              hanging: float = 0.0, line_spacing: float = 1.15):
    para = doc.add_paragraph()
    para.alignment = align
    fmt = para.paragraph_format
    fmt.space_before = Pt(space_before)
    fmt.space_after = Pt(space_after)
    fmt.line_spacing = line_spacing
    if indent:
        fmt.first_line_indent = Pt(size * indent)
    if hanging:
        fmt.left_indent = Pt(hanging)
        fmt.first_line_indent = Pt(-hanging)
    run = para.add_run(text)
    style_run(run, size, cjk, bold)
    return para


def rich_paragraph(doc, parts, size: float, cjk: str = SONG,
                   align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent: float = 0.0,
                   space_before: float = 0.0, space_after: float = 2.0):
    para = doc.add_paragraph()
    para.alignment = align
    fmt = para.paragraph_format
    fmt.space_before = Pt(space_before)
    fmt.space_after = Pt(space_after)
    fmt.line_spacing = 1.15
    if indent:
        fmt.first_line_indent = Pt(size * indent)
    for text, bold in parts:
        run = para.add_run(text)
        style_run(run, size, cjk, bold)
    return para


def set_columns(section, count: int, space_cm: float = 0.7) -> None:
    cols = section._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        section._sectPr.append(cols)
    cols.set(qn("w:num"), str(count))
    cols.set(qn("w:space"), str(int(space_cm * 567)))
    cols.set(qn("w:equalWidth"), "1")


def three_line_table(doc, rows: list[list[str]], size: float = 7.5) -> None:
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.autofit = True
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = ""
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT if c else WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.line_spacing = 1.0
            for piece, bold in inline_parts(cell_text):
                style_run(para.add_run(piece), size, SONG, bold=(r == 0) or bold)
    # borders: no verticals, thick top/bottom, thin under the header row
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("left", "right", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        borders.append(el)
    for edge, sz in (("top", "12"), ("bottom", "12"), ("insideH", "4")):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tbl_pr.append(borders)
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = None


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.0)
    section.left_margin = section.right_margin = Cm(1.8)
    set_columns(section, 1)

    lines = text.split("\n")
    i = 0
    body_started = False
    in_code = False
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            if stripped:
                paragraph(doc, stripped, 8.0, SONG, False, WD_ALIGN_PARAGRAPH.LEFT,
                          space_after=0.5, line_spacing=1.0)
            i += 1
            continue
        if not stripped or stripped.startswith("<!--") or stripped == "---":
            i += 1
            continue

        if not body_started and re.match(r"^## \d", stripped):
            body_started = True
            new_section = doc.add_section(WD_SECTION.CONTINUOUS)
            new_section.page_width, new_section.page_height = Cm(21.0), Cm(29.7)
            new_section.top_margin = new_section.bottom_margin = Cm(2.0)
            new_section.left_margin = new_section.right_margin = Cm(1.8)
            set_columns(new_section, 2)

        if stripped.startswith("# "):
            paragraph(doc, stripped[2:], 19.7, HEI, True, WD_ALIGN_PARAGRAPH.CENTER,
                      space_before=6, space_after=10)
        elif stripped.startswith("## "):
            title = stripped[3:]
            if not body_started:
                paragraph(doc, title, 13.0, HEI, True, WD_ALIGN_PARAGRAPH.CENTER,
                          space_before=10, space_after=6)
            else:
                paragraph(doc, title.strip("*"), 13.1, HEI, True, WD_ALIGN_PARAGRAPH.LEFT,
                          space_before=8, space_after=4)
        elif stripped.startswith("### "):
            title = stripped[4:]
            level3 = title.split(" ", 1)[0].count(".") >= 2
            paragraph(doc, title, 9.7, HEI if not level3 else SONG, True,
                      WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=3)
        elif stripped.startswith("!["):
            match = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
            if match:
                caption, path = match.group(1), match.group(2)
                image = BASE / path
                if image.exists():
                    para = doc.add_paragraph()
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.add_run().add_picture(str(image), width=Cm(8.4))
                paragraph(doc, caption, 8.2, SONG, False, WD_ALIGN_PARAGRAPH.CENTER,
                          space_before=1, space_after=6)
        elif stripped.startswith("|") and i + 1 < len(lines) and set(lines[i + 1]) <= set("|-: "):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            if rows:
                three_line_table(doc, rows)
                paragraph(doc, "", 6, SONG, space_after=0)
            continue
        elif re.match(r"^\*\*摘　要\*\*", stripped):
            body = stripped.split("**", 2)[2].strip()
            rich_paragraph(doc, [("摘　要  ", True)] + inline_parts(body), 8.2, SONG)
        elif stripped.startswith("**关键词**") or stripped.startswith("**Keywords**"):
            match = re.match(r"\*\*(.+?)\*\*\s*(.*)", stripped)
            label, body = match.group(1), match.group(2)
            rich_paragraph(doc, [(label + "  ", True)] + inline_parts(body), 8.2, SONG)
        elif stripped.startswith("**中图法分类号**"):
            rich_paragraph(doc, inline_parts(stripped), 8.2, SONG,
                           WD_ALIGN_PARAGRAPH.LEFT)
        elif stripped.startswith("**（"):
            paragraph(doc, stripped.strip("*"), 8.2, SONG, False, WD_ALIGN_PARAGRAPH.CENTER)
        elif stripped.startswith("**Abstract**"):
            body = stripped.split("**", 2)[2].strip()
            rich_paragraph(doc, [("Abstract  ", True)] + inline_parts(body), 9.7, SONG)
        elif re.match(r"^\[\d+\] ", stripped):
            paragraph(doc, stripped, 7.5, SONG, False, WD_ALIGN_PARAGRAPH.JUSTIFY,
                      hanging=10, space_after=1.5)
        else:
            body = stripped
            if body:
                rich_paragraph(doc, inline_parts(body), 9.0, SONG,
                               WD_ALIGN_PARAGRAPH.JUSTIFY, indent=2.0, space_after=3)
        i += 1

    doc.save(OUT)
    print(f"CJC_DOCX_WRITTEN={OUT}")


if __name__ == "__main__":
    main()
