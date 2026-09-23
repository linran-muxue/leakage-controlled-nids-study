"""Replace the misattribution of the full-corpus deficit with its mechanism.

Section 5.7 attributed the -0.005533 deficit to "the aggregation-rule
difference".  Section 5.3 shows the weights never move a label, so that cannot
be right.  The deficit is the cost of averaging over feature views whose quality
has diverged: the full-feature forest is 0.021397 behind the chi-square forest
on this corpus, and carrying one such expert inside a four-way average costs
about a quarter of that gap, 0.005349 - within 4% of the measurement.  The same
arithmetic predicts the capped-population result (0.002068 / 4 = 0.000517
against a measured -0.000456).  One mechanism, both numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_OLD = ("The aggregation-rule difference is therefore negligible on capped populations and only "
          "becomes measurable - and negative - once the corpus is left completely unbalanced, which "
          "is the regime in which the mechanism would actually be deployed. Per-seed paired statistics")
EN_NEW = ("**The deficit is dilution, not weighting.** On this corpus the four feature views are no "
          "longer interchangeable. The full-feature forest reaches 0.738143 Macro-F1 against 0.759540 "
          "for the chi-square forest, a gap of 0.021397; carrying one such expert inside a four-way "
          "average costs roughly a quarter of that gap, 0.005349, which is within 4% of the measured "
          "-0.005533. The same arithmetic accounts for the capped-population result, where the two "
          "views differ by only 0.002068 and the predicted dilution is 0.000517 against a measured "
          "-0.000456. What changes with scale is therefore not the aggregation rule - Section 5.3 "
          "shows the weights never move a label - but the price of averaging over feature views whose "
          "quality has diverged. This is the practical form of Condition 1: an equal-weight fusion is "
          "bounded by its weakest expert, and the capped populations hide that bound because there "
          "all four views score within 0.002 of one another.\n\nPer-seed paired statistics")

ZH_OLD = ("也就是说，聚合规则的差异在截断总体上可以忽略，只有把语料完全放开、进入真实部署会遇到的强不平衡状态时才变得可测"
          "——而且是负的。三次运行的逐种子配对统计")
ZH_NEW = ("**这个差异来自稀释，而不是加权。** 在全语料上，四个特征视图不再可以互相替代：全特征森林的 Macro-F1 为 "
          "0.738143，卡方森林为 0.759540，差距 0.021397；把这样一个较弱的专家放进四路平均，代价约为该差距的四分之一，"
          "即 0.005349，与实测的 −0.005533 相差不到 4%。同一算式也解释了截断总体上的结果：那里两个视图只差 0.002068，"
          "预测稀释为 0.000517，而实测为 −0.000456。因此随规模变化的不是聚合规则——5.3 节已表明权重从不改变任何一条预测"
          "——而是对质量已经分化的特征视图做平均的代价。这正是命题 1 的实践形态：等权融合的上限由最弱专家决定，"
          "而截断总体掩盖了这一上限，因为在那些总体上四个视图的得分相差不到 0.002。\n\n三次运行的逐种子配对统计")


def main() -> int:
    en = BASE / "English_SCI_Manuscript_v4.md"
    text = en.read_text(encoding="utf-8")
    if "The deficit is dilution, not weighting" in text:
        print("  English: dilution account already present")
    elif EN_OLD in text:
        en.write_text(text.replace(EN_OLD, EN_NEW, 1), encoding="utf-8")
        print("  English: dilution account added")
    else:
        raise SystemExit("English anchor missing")

    zh = BASE / "中文SCI论文_v4_重构版.md"
    text = zh.read_text(encoding="utf-8")
    if "这个差异来自稀释，而不是加权" in text:
        print("  Chinese: dilution account already present")
    elif ZH_OLD in text:
        zh.write_text(text.replace(ZH_OLD, ZH_NEW, 1), encoding="utf-8")
        print("  Chinese: dilution account added")
    else:
        raise SystemExit("Chinese anchor missing")

    print("DILUTION_ACCOUNT_ADDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
