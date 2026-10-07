"""Restyle the Chinese manuscript to the layout conventions of 计算机学报.

The layout was read off the sample PDF supplied by the author (2025, Vol. 48
No. 9): A4, two-column body, 黑体 headings at 13.1 pt (level 1) and 9.7 pt
(levels 2 and 3), 书宋 body, captions numbered without a space (图1/表1) placed
below figures and above tables, three-line tables, and a reference list in the
form ``[n] Author. Title. Journal, Year, Vol(Issue): pages`` with ``//`` before
proceedings and no DOI.

This script rewrites the Markdown conventions only; the DOCX renderer applies
the fonts, sizes and column layout.  The original JISA-targeted files are left
untouched - this is an additional deliverable, not a replacement.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SOURCE = BASE / "中文SCI论文_v4_重构版.md"
ENGLISH = BASE / "English_SCI_Manuscript_v4.md"
OUT = BASE / "中文SCI论文_计算机学报排版版.md"

AUTHOR_PLACEHOLDER = "（待作者填写：作者姓名）"
AFFILIATION_PLACEHOLDER = "（待作者填写：单位、城市、邮编）"
CLC = "TP393"


def front_matter(zh: str, en: str) -> str:
    title_zh = zh.split("\n", 1)[0].lstrip("# ").strip()
    abstract_zh = (zh.split("## 摘要", 1)[1]
                   .split("**关键词", 1)[0]
                   .strip())
    keywords_zh = re.search(r"\*\*关键词：\*\*\s*(.+)", zh).group(1).strip()
    title_en = en.split("\n", 1)[0].lstrip("# ").strip()
    abstract_en = en.split("## Abstract", 1)[1].split("**Keywords", 1)[0].strip()
    keywords_en = re.search(r"\*\*Keywords:\*\*\s*(.+)", en).group(1).strip()
    return "\n".join([
        f"# {title_zh}",
        "",
        "<!-- 计算机学报版式：作者与单位由作者填写；中图法分类号 TP393（计算机网络）；"
        "DOI 由编辑部在录用后分配 -->",
        "",
        f"**{AUTHOR_PLACEHOLDER}**",
        "",
        f"**{AFFILIATION_PLACEHOLDER}**",
        "",
        "**摘　要** " + abstract_zh,
        "",
        "**关键词** " + keywords_zh,
        "",
        f"**中图法分类号** {CLC}　　**DOI** （待编辑部在录用后分配）",
        "",
        "---",
        "",
        f"## {title_en}",
        "",
        "**（Author names to be completed）**",
        "",
        "**（Affiliation, City Postcode）**",
        "",
        "**Abstract** " + abstract_en,
        "",
        "**Keywords** " + keywords_en,
        "",
        "---",
        "",
    ])


def convert_captions(text: str) -> str:
    """图 1 -> 图1, 表 1 -> 表1: the sample numbers captions without a space."""
    text = re.sub(r"!\[图\s+(\d+)", r"![图\1", text)
    text = re.sub(r"\*\*表\s+(\d+)", r"**表\1", text)
    for lead in ("（", "见", "如", "由"):
        text = re.sub(lead + r"图\s+(\d+)", lead + r"图\1", text)
        text = re.sub(lead + r"表\s+(\d+)", lead + r"表\1", text)
    return text


def convert_references(text: str) -> str:
    """Reference list -> 计算机学报 style (no DOI, // before proceedings)."""
    start = text.find("## 参考文献")
    if start < 0:
        return text
    end = text.find("\n## ", start + 5)
    if end < 0:
        end = len(text)
    block = text[start:end]
    entries = re.findall(r"^\d+\.\s+(.*)$", block, flags=re.M)
    if not entries:
        return text
    converted = []
    for i, entry in enumerate(entries, 1):
        body = entry.strip()
        body = re.sub(r"\s*DOI:10\.[^\s]+\.?$", "", body)
        body = body.replace("[no DOI; ", "[无 DOI；")
        body = re.sub(r"\.\s+(Proceedings|USENIX|NeurIPS|ICML|KDD|CVPR|IJCNN|MCS|SciPy|MilCIS|CISDA|ICTAI|Sensors|Electronics)\b",
                      r"//\1", body)
        body = body.rstrip(".")
        converted.append(f"[{i}] {body}")
    return text[:start] + "## 参考文献\n\n" + "\n".join(converted) + "\n" + text[end:]


def main() -> None:
    zh = SOURCE.read_text(encoding="utf-8")
    en = ENGLISH.read_text(encoding="utf-8")
    body_start = zh.find("## 1 引言")
    if body_start < 0:
        raise SystemExit("body start not found")
    body = convert_references(convert_captions(zh[body_start:]))
    out = front_matter(zh, en) + body
    OUT.write_text(out, encoding="utf-8")
    print(f"CJC_MANUSCRIPT_WRITTEN={OUT}")
    entries = len(re.findall(r"^\[\d+\] ", out, flags=re.M))
    print(f"  chars={len(out)} | reference entries={entries}")


if __name__ == "__main__":
    main()
