"""Add the intra-manuscript consistency item (E11) and refresh the totals."""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC_PATH = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
E11 = ("| E11 | 稿内自洽 | 同一事实不重复、同一对象同一名称 | **通过** | "
       "`scripts/check_duplicate_sentences_v27.py`：两稿均无重复句，且无段落重复同一组小数（曾发现中文 §5.2 "
       "重复陈述平衡控制训练耗时）；全文统一为「聚合规则 / aggregation rule」；该检查已接入验证闸门 |")
def main() -> None:
    text = SC_PATH.read_text(encoding="utf-8")
    changed = []
    if "| E11 |" not in text:
        anchor = re.search(r"^\| E10 \|.*$", text, flags=re.M)
        if anchor:
            text = text[:anchor.end()] + "\n" + E11 + text[anchor.end():]
            changed.append("E11 added")
    for old, new, label in (
        (r"^\| E 呈现与写作 \| 10 \| 9 \| 1 \| 0 \|$", "| E 呈现与写作 | 11 | 10 | 1 | 0 |", "layer E"),
        (r"^\| \*\*合计\*\* \| \*\*67\*\* \| \*\*63\*\* \| \*\*4\*\* \| \*\*0\*\* \|$",
         "| **合计** | **68** | **64** | **4** | **0** |", "summary"),
        ("**67 项检查中 63 项通过、4 项部分通过、0 项缺失**",
         "**68 项检查中 64 项通过、4 项部分通过、0 项缺失**", "conclusion (header)"),
        ("**67 项检查中 63 项通过、4 项部分通过、0 项缺失。**",
         "**68 项检查中 64 项通过、4 项部分通过、0 项缺失。**", "conclusion (closing)"),
        ("67 项检查中 63 项通过、4 项部分通过、0 项缺失；含每项的证据文件。",
         "68 项检查中 64 项通过、4 项部分通过、0 项缺失；含每项的证据文件。", "status stamp"),
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
