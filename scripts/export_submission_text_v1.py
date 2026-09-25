"""Export the title, abstract and keywords as plain text for the submission system.

Journal submission forms ask for the title, the abstract and the keywords as
separate fields, and copy-pasting them out of a Word file is where typographic
damage happens.  This writes both languages as plain text (one file per
language), with the word and character counts recorded at the top so a
copy-paste error is visible at a glance.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = ROOT / "results_publication_final" / "submission_text"


def english() -> str:
    text = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    abstract = text.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].strip()
    keywords = re.search(r"\*\*Keywords:\*\*\s*(.+)", text).group(1).strip()
    body = ("## Title\n\n" + title + "\n\n## Abstract\n\n" + abstract +
            f"\n\n## Keywords\n\n{keywords}\n\n---\n"
            f"abstract {len(abstract.split())} words "
            f"(limit 250); {len(keywords.split(';'))} keywords\n")
    return body


def chinese() -> str:
    text = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    abstract = text.split("## 摘要", 1)[1].split("**关键词", 1)[0].strip()
    keywords = re.search(r"\*\*关键词：\*\*\s*(.+)", text).group(1).strip()
    body = ("## 标题\n\n" + title + "\n\n## 摘要\n\n" + abstract +
            f"\n\n## 关键词\n\n{keywords}\n\n---\n"
            f"摘要 {len(abstract)} 字符；关键词 {len(keywords.split('；'))} 个\n")
    return body


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in (("title_abstract_keywords_EN.md", english()),
                       ("title_abstract_keywords_ZH.md", chinese())):
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"wrote {name} ({len(text)} chars)")
    print(f"output: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
