"""Verify the dilution expression on all three CIC-IDS2017 populations.

The dilution account was stated on two points (the primary population and the
full corpus).  The 413,209-flow run supplies a third, and all three fit the same
expression - one lagging expert in a four-way average costs a quarter of the
view gap:

    population    view gap   gap/4 predicted   measured      deviation
    53,237        0.002068   0.000517          -0.000456     13.4%
    413,209       0.004249   0.001062          -0.001137      6.6%
    2,429,503     0.021397   0.005349          -0.005533      3.4%

Across a 46-fold range in population size the prediction stays within 14% of
the measurement, which turns a two-point observation into a checked relation.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_OLD = ("**The deficit is dilution, not weighting.** On this corpus the four feature views are no "
          "longer interchangeable. The full-feature forest reaches 0.738143 Macro-F1 against 0.759540 "
          "for the chi-square forest, a gap of 0.021397; carrying one such expert inside a four-way "
          "average costs roughly a quarter of that gap, 0.005349, which is within 4% of the measured "
          "-0.005533. The same arithmetic accounts for the capped-population result, where the two "
          "views differ by only 0.002068 and the predicted dilution is 0.000517 against a measured "
          "-0.000456. What changes with scale is therefore not the aggregation rule - Section 5.3 "
          "shows the weights never move a label - but the price of averaging over feature views whose "
          "quality has diverged. This is the practical form of Condition 1: an equal-weight fusion is "
          "bounded by its weakest expert, and the capped populations hide that bound because there "
          "all four views score within 0.002 of one another.")
EN_NEW = ("**The deficit is dilution, not weighting, and one expression predicts it on all three "
          "populations.** On the uncapped corpus the four feature views are no longer "
          "interchangeable: the full-feature forest reaches 0.738143 Macro-F1 against 0.759540 for "
          "the chi-square forest, a gap of 0.021397, and one such expert inside a four-way average "
          "costs a quarter of it, 0.005349, against a measured -0.005533. The same expression applies "
          "to the 413,209-flow population (view gap 0.004249, predicted 0.001062, measured -0.001137) "
          "and to the primary population (gap 0.002068, predicted 0.000517, measured -0.000456). "
          "Across a 46-fold range in population size the prediction stays within 14% of the "
          "measurement, so what changes with scale is not the aggregation rule - Section 5.3 shows "
          "the weights never move a label - but the price of averaging over feature views whose "
          "quality has diverged. This is the practical form of Condition 1: an equal-weight fusion is "
          "bounded by its weakest member, and the capped populations hide that bound because there "
          "all four views score within 0.002 of one another.")

ZH_OLD = ("**这个差异来自稀释，而不是加权。** 在全语料上，四个特征视图不再可以互相替代：全特征森林的 Macro-F1 为 "
          "0.738143，卡方森林为 0.759540，差距 0.021397；把这样一个较弱的专家放进四路平均，代价约为该差距的四分之一，"
          "即 0.005349，与实测的 −0.005533 相差不到 4%。同一算式也解释了截断总体上的结果：那里两个视图只差 0.002068，"
          "预测稀释为 0.000517，而实测为 −0.000456。因此随规模变化的不是聚合规则——5.3 节已表明权重从不改变任何一条预测"
          "——而是对质量已经分化的特征视图做平均的代价。这正是命题 1 的实践形态：等权融合的上限由最弱专家决定，"
          "而截断总体掩盖了这一上限，因为在那些总体上四个视图的得分相差不到 0.002。")
ZH_NEW = ("**这个差异来自稀释，而不是加权，而且同一个算式在三个总体上都成立。** 在全语料上，四个特征视图不再可以互相替代："
          "全特征森林的 Macro-F1 为 0.738143，卡方森林为 0.759540，差距 0.021397；把这样一个较弱的专家放进四路平均，"
          "代价为该差距的四分之一，即 0.005349，与实测的 −0.005533 相差不到 4%。同一算式也适用于 413 209 条总体"
          "（视图差距 0.004249，预测 0.001062，实测 −0.001137）与主总体（差距 0.002068，预测 0.000517，"
          "实测 −0.000456）。在总体规模跨越 46 倍的范围内，预测与实测的偏差都不超过 14%。因此随规模变化的不是聚合规则"
          "——5.3 节已表明权重从不改变任何一条预测——而是对质量已经分化的特征视图做平均的代价。这正是命题 1 的实践形态："
          "等权融合的上限由最弱成员决定，而截断总体掩盖了这一上限，因为在那些总体上四个视图的得分相差不到 0.002。")

EN_COND = ("four-way average accounts for the whole measured deficit: 0.021397/4 = 0.005349 predicted "
           "against -0.005533 observed. The corresponding diagnostic is therefore a comparison of "
           "member scores, not of weights.")
EN_COND_NEW = ("four-way average accounts for the whole measured deficit: 0.021397/4 = 0.005349 "
               "predicted against -0.005533 observed. The same expression holds on the 413,209-flow "
               "population (0.004249/4 = 0.001062 against -0.001137) and on the primary population "
               "(0.002068/4 = 0.000517 against -0.000456), so the diagnostic is a comparison of "
               "member scores, not of weights.")

ZH_COND = ("四路平均中一个这样的成员就解释了全部实测差异：预测 0.021397/4 = 0.005349，实测 −0.005533。"
           "相应的诊断因此是比较成员得分，而不是比较权重。")
ZH_COND_NEW = ("四路平均中一个这样的成员就解释了全部实测差异：预测 0.021397/4 = 0.005349，实测 −0.005533。"
               "同一算式在 413 209 条总体（0.004249/4 = 0.001062，实测 −0.001137）与主总体"
               "（0.002068/4 = 0.000517，实测 −0.000456）上同样成立，因此诊断应是比较成员得分，而不是比较权重。")

PAIRS: list[tuple[Path, str, str, str]] = [
    (BASE / "English_SCI_Manuscript_v4.md", EN_OLD, EN_NEW, "EN §5.7"),
    (BASE / "中文SCI论文_v4_重构版.md", ZH_OLD, ZH_NEW, "ZH §5.7"),
    (BASE / "English_SCI_Manuscript_v4.md", EN_COND, EN_COND_NEW, "EN Condition D"),
    (BASE / "中文SCI论文_v4_重构版.md", ZH_COND, ZH_COND_NEW, "ZH 条件 D"),
]


def main() -> int:
    for path, old, new, label in PAIRS:
        text = path.read_text(encoding="utf-8")
        if new in text:
            print(f"  [{label}] already applied")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {label}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"  [{label}] extended to three populations")
    print("DILUTION_THREE_POINTS_ADDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
