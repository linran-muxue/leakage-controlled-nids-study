"""Remove two ambiguities in Section 5.1 of both manuscripts.

1. The feature-degeneracy counts (12 constant, 18 near-zero-variance) belong to
   the balanced control corpus P_bal; the primary natural-prior corpus gives 10
   and 20. Stated without a population, a reader maps them onto the primary
   protocol. Both sets of counts are now named.
2. "in two protocols it produces a small positive difference" contradicted the
   table directly above it, where all three differences are positive. The
   sentence now says which protocols carry the small positive difference and
   which one shrinks to noise.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_QUALITY_OLD = ("The feature-quality audit shows that 12 of the 78 CIC-IDS2017 features are "
                  "constant (a single value across all rows) and 18 are near-zero-variance.")
EN_QUALITY_NEW = ("The feature-quality audit of the balanced control corpus P_bal (2,355 training "
                  "rows) shows that 12 of the 78 CIC-IDS2017 features are constant (a single value "
                  "across all rows) and 18 are near-zero-variance; the primary natural-prior split "
                  "shows 10 constant and 20 near-zero-variance features, so the degeneracy belongs "
                  "to the feature representation rather than to one population.")

EN_PROTOCOL_OLD = ("and in two protocols it produces a small positive difference. Under ten "
                   "repeated splits that difference (+0.00015) is nevertheless two orders of "
                   "magnitude smaller than the split-to-split standard deviation (about 0.011).")
EN_PROTOCOL_NEW = ("The two fixed-split protocols show a small positive difference (+0.00207 and "
                   "+0.00222); under ten repeated splits the difference shrinks to +0.00015, two "
                   "orders of magnitude smaller than the split-to-split standard deviation "
                   "(about 0.011).")

ZH_QUALITY_OLD = ("特征质量审计显示，CIC-IDS2017 的 78 维特征中有 **12 维为恒定列**（全部取值相同），"
                  "18 维为近零方差特征。")
ZH_QUALITY_NEW = ("在平衡控制总体 P_bal 的训练划分（2 355 行）上做特征质量审计，78 维 CIC-IDS2017 "
                  "特征中有 **12 维为恒定列**（全部取值相同），18 维为近零方差特征；主协议的自然先验划分上"
                  "同样有 10 维恒定、20 维近零方差，说明这种退化属于特征表示本身，而不是某个总体特有的现象。")

ZH_PROTOCOL_OLD = ("三个协议的结论一致：**把特征维度从 78 降到 60 没有造成判别能力损失**，"
                   "在两个协议上甚至出现小幅正向差异，但在十次重复划分下该差异（+0.00015）远小于"
                   "划分间的标准差（约 0.011）。")
ZH_PROTOCOL_NEW = ("三个协议的结论一致：**把特征维度从 78 降到 60 没有造成判别能力损失**。"
                   "两个固定划分协议上出现小幅正向差异（+0.00207 与 +0.00222）；在十次重复划分下"
                   "该差异缩小到 +0.00015，比划分间标准差（约 0.011）小两个数量级。")


def fix(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once in {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"updated {path.name}: {old[:40]}...")


def main() -> None:
    en = BASE / "English_SCI_Manuscript_v4.md"
    zh = BASE / "中文SCI论文_v4_重构版.md"
    fix(en, EN_QUALITY_OLD, EN_QUALITY_NEW)
    fix(en, EN_PROTOCOL_OLD, EN_PROTOCOL_NEW)
    fix(zh, ZH_QUALITY_OLD, ZH_QUALITY_NEW)
    fix(zh, ZH_PROTOCOL_OLD, ZH_PROTOCOL_NEW)
    print("SECTION51_WORDING_FIXED")


if __name__ == "__main__":
    main()
