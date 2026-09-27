"""Make the third contribution list the same five sources in both languages.
The Chinese sentence listed class prior and file-level extrapolation in place of
the tuning budget, so the two manuscripts enumerated different sets. The same
paragraph in Section 5.4 also said "four magnitudes" while listing five.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_OLD = "tuning budget (+0.0078) and class prior (+0.072)."
EN_NEW = "tuning budget (+0.0078) and class prior (+0.0725)."
ZH_OLD = ("我们在同一批数据上测量五类差异来源并给出量级：聚合策略（0.0005）、特征视图（+0.0021）、"
          "类别先验（+0.0725）、去重顺序（至多 +0.0060）、文件外推（0.33–1.00）。"
          "结论是协议效应比聚合策略差异高出一个数量级。")
ZH_NEW = ("我们在同一批数据上测量五类差异来源并给出量级：聚合策略（0.0005）、特征视图（+0.0021）、"
          "去重顺序（至多 +0.0060）、调参预算（+0.0078）与类别先验（+0.0725）；文件外推跨度为 0.33–1.00。"
          "结论是协议效应比聚合策略差异高出一个数量级。")
ZH_FOUR = "把四个量级并列："
ZH_FIVE = "把五个量级并列："
def apply(path: Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            print(f"  [{path.name}] anchor absent: {old[:60]}...")
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: {applied}/{len(edits)} applied")
def main() -> None:
    apply(BASE / "English_SCI_Manuscript_v4.md", [(EN_OLD, EN_NEW)])
    apply(BASE / "中文SCI论文_v4_重构版.md", [(ZH_OLD, ZH_NEW), (ZH_FOUR, ZH_FIVE)])
if __name__ == "__main__":
    main()
