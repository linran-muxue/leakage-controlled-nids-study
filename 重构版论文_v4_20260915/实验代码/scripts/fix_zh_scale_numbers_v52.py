"""Use digit notation for the scale-run counts in the Chinese section.
The English writes 200,000 / 180,000 / 60,000; the Chinese used 20 万 / 18 万 /
6 万, which the cross-language number check reports as missing values.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"
EDITS = [
    ("仅把每类上限提高到 20 万条", "仅把每类上限提高到 200 000 条"),
    ("最终得到 18 万条、三分类的基准（每类 6 万；", "最终得到 180 000 条、三分类的基准（每类 60 000；"),
]
def main() -> None:
    text = ZH.read_text(encoding="utf-8")
    for old, new in EDITS:
        if old in text:
            text = text.replace(old, new, 1)
            print(f"replaced: {old[:40]}")
        else:
            print(f"anchor absent: {old[:40]}")
    ZH.write_text(text, encoding="utf-8")
if __name__ == "__main__":
    main()
