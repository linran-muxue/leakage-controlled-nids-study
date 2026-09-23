"""Carry the dilution mechanism into the Conclusion.

The deficit on the uncapped corpus is the paper's sharpest explanatory result;
the conclusion should say what causes it rather than only that it exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_OLD = ("comparison turns into a consistent deficit of -0.005533 across all ten seeds, at a 175-fold "
          "training cost.")
EN_NEW = (EN_OLD + " The cause is not the weighting - Section 5.3 shows the weights never move a "
          "label - but the price of averaging over feature views whose quality diverges at scale: the "
          "full-feature view falls 0.021397 behind the chi-square view, and one such expert inside a "
          "four-way average accounts for the whole gap (0.005349 predicted against -0.005533 "
          "measured).")

# The earlier repair consumed the tail of this sentence and left a dangling
# comma plus a paragraph whose colon introduced unrelated content; both are
# repaired by replacing the whole tail.
ZH_OLD = ("（十种子方向一致，0.01 边界等价、0.005 边界不等价），\n\n"
          "**该等价性的限定条件。** 它取决于总体构造而非机制本身：训练代价 175 倍，十种子方向一致。")
ZH_NEW = ("（十种子方向一致，0.01 边界等价、0.005 边界不等价），训练代价 175 倍。\n\n"
          "**该等价性的限定条件。** 它取决于总体构造而非机制本身。这个劣势的原因不是加权"
          "——5.3 节已表明权重从不改变任何一条预测——而是在质量随规模分化的特征视图上取平均的代价："
          "全特征视图比卡方视图低 0.021397，一个这样的较弱专家进入四路平均即可解释全部差距"
          "（预测 0.005349，实测 −0.005533）。")


def main() -> int:
    en = BASE / "English_SCI_Manuscript_v4.md"
    text = en.read_text(encoding="utf-8")
    if "accounts for the whole gap" in text:
        print("  English: conclusion already carries the dilution account")
    elif EN_OLD in text:
        en.write_text(text.replace(EN_OLD, EN_NEW, 1), encoding="utf-8")
        print("  English: conclusion updated")
    else:
        raise SystemExit("English anchor missing")

    zh = BASE / "中文SCI论文_v4_重构版.md"
    text = zh.read_text(encoding="utf-8")
    if "即可解释全部差距" in text:
        print("  Chinese: conclusion already carries the dilution account")
    elif ZH_OLD in text:
        zh.write_text(text.replace(ZH_OLD, ZH_NEW, 1), encoding="utf-8")
        print("  Chinese: conclusion updated")
    else:
        raise SystemExit("Chinese anchor missing")

    print("CONCLUSION_DILUTION_ADDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
