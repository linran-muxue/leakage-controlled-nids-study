"""Add the journal hard-limit item to the self-check table and bump the totals.
The compliance sweep found that the abstract was 422 words against a 250-word
limit and that the equations were unnumbered; both are now checked by
scripts/check_jisa_format_v22.py, so the table needs an item for them.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC_PATH = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
E10 = ("| E10 | 期刊硬性格式 | 满足 JISA 指南的字数与条数上限 | **通过** | "
       "`scripts/check_jisa_format_v22.py`：摘要 249 词（上限 250）、关键词 7 个（上限 7）、"
       "Highlights 5 条且最长 83 字符（上限 85）、公式按 (1)–(5) 顺序编号、"
       "图形摘要 3300×2280 像素（下限 1328×531）；该检查已接入验证闸门 |")
def main() -> None:
    text = SC_PATH.read_text(encoding="utf-8")
    changed = []
    if "| E10 |" not in text:
        anchor = re.search(r"^\| E9 \|.*$", text, flags=re.M)
        if anchor:
            text = text[:anchor.end()] + "\n" + E10 + text[anchor.end():]
            changed.append("E10 added")
        else:
            print("E9 anchor missing")
    for old, new, label in (
        (r"^\| E 呈现与写作 \| 9 \| 8 \| 1 \| 0 \|$", "| E 呈现与写作 | 10 | 9 | 1 | 0 |", "layer E"),
        (r"^\| \*\*合计\*\* \| \*\*66\*\* \| \*\*62\*\* \| \*\*4\*\* \| \*\*0\*\* \|$",
         "| **合计** | **67** | **63** | **4** | **0** |", "summary"),
        ("**66 项检查中 62 项通过、4 项部分通过、0 项缺失**",
         "**67 项检查中 63 项通过、4 项部分通过、0 项缺失**", "conclusion (header)"),
        ("**66 项检查中 62 项通过、4 项部分通过、0 项缺失。**",
         "**67 项检查中 63 项通过、4 项部分通过、0 项缺失。**", "conclusion (closing)"),
        ("66 项检查中 62 项通过、4 项部分通过、0 项缺失；含每项的证据文件。",
         "67 项检查中 63 项通过、4 项部分通过、0 项缺失；含每项的证据文件。", "status stamp"),
    ):
        new_text, n = re.subn(old, new, text, count=1, flags=re.M) if old.startswith("^") else (text.replace(old, new, 1), text.count(old))
        if n:
            text = new_text
            changed.append(label)
        else:
            print(f"anchor absent: {label}")
    SC_PATH.write_text(text, encoding="utf-8")
    print("updated:", ", ".join(changed) or "nothing")
if __name__ == "__main__":
    main()
