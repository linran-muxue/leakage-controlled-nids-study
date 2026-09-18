"""Verify that Word will restart numbering for every numbered list.
The rendered PDF showed the third numbered list starting at 10, because all
list paragraphs shared one style-level counter. The builder now gives each list
its own numId with a start override; this check keeps that property.
"""
from __future__ import annotations
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DOCS = ["English_SCI_Manuscript_v4.docx", "中文SCI论文_v4_重构版.docx",
        "论文自查表.docx", "遗漏问题审查报告.docx", "论文结构诊断与重构方案.docx",
        "研究缺口审计与优先级清单.docx", "P0_P1执行手册.docx"]
def num_id(paragraph) -> str | None:
    element = paragraph._p.find(".//" + qn("w:numId"))
    return element.get(qn("w:val")) if element is not None else None
def main() -> int:
    problems: list[str] = []
    for name in DOCS:
        path = BASE / name
        if not path.exists():
            problems.append(f"{name} missing")
            continue
        document = Document(str(path))
        blocks: list[tuple[str, int]] = []
        previous = None
        for paragraph in document.paragraphs:
            if paragraph.style.name != "List Number":
                previous = None
                continue
            current = num_id(paragraph)
            if current is None:
                problems.append(f"{name}: a numbered paragraph has no numId")
                break
            if current != previous:
                blocks.append((current, 1))
            else:
                blocks[-1] = (current, blocks[-1][1] + 1)
            previous = current
        used = [block[0] for block in blocks]
        if len(set(used)) != len(used):
            problems.append(f"{name}: a numId is reused by two separate lists")
        overrides = set()
        numbering = document.part.numbering_part.element
        for num in numbering.findall(qn("w:num")):
            override = num.find(qn("w:lvlOverride"))
            if override is not None and override.find(qn("w:startOverride")) is not None:
                overrides.add(num.get(qn("w:numId")))
        missing_override = [n for n in used if n not in overrides]
        if missing_override:
            problems.append(f"{name}: lists without a start override {missing_override}")
        print(f"  {name}: {len(blocks)} list(s), numIds {used[:8]}{' ...' if len(used) > 8 else ''}, "
              f"all with start override: {not missing_override}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("DOCX_NUMBERING_BROKEN")
        return 1
    print("DOCX_NUMBERING_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
