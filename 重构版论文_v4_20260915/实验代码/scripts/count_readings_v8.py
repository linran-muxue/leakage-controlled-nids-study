"""Count the numbered narrative blocks inside each section."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

SECTIONS = {
    "EN 5.2": ("English_SCI_Manuscript_v4.md", "### 5.2", "### 5.3",
               r"^\*\*(First|Second|Third|Fourth|Fifth|Sixth)"),
    "EN 5.3": ("English_SCI_Manuscript_v4.md", "### 5.3", "### 5.4",
               r"^\*\*Measurement (\d)"),
    "EN 6.1": ("English_SCI_Manuscript_v4.md", "### 6.1", "### 6.2",
               r"^\*\*Condition ([ABC])"),
    "EN 7": ("English_SCI_Manuscript_v4.md", "## 7.", "## Data and code",
             r"^\*\*(First|Second|Third|Fourth)"),
    "ZH 5.2": ("中文SCI论文_v4_重构版.md", "### 5.2", "### 5.3",
               r"^\*\*(第一|第二|第三|第四|第五|第六)"),
    "ZH 5.3": ("中文SCI论文_v4_重构版.md", "### 5.3", "### 5.4",
               r"^\*\*测量([一二三四五六])"),
    "ZH 6.1": ("中文SCI论文_v4_重构版.md", "### 6.1", "### 6.2",
               r"^\*\*条件([ABC])"),
    "ZH 7": ("中文SCI论文_v4_重构版.md", "## 7 结论", "## 数据与代码可用性",
             r"^\*\*(第一|第二|第三|第四)"),
}


def main() -> None:
    for label, (name, start, end, pattern) in SECTIONS.items():
        text = (BASE / name).read_text(encoding="utf-8")
        i = text.find(start)
        j = text.find(end, i + 1) if i >= 0 else -1
        block = text[i:j] if i >= 0 and j > i else ""
        found = re.findall(pattern, block, flags=re.M)
        print(f"{label:<8} blocks={len(found):<3} {found}")


if __name__ == "__main__":
    main()
