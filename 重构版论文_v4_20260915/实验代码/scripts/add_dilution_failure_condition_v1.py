"""Promote the dilution effect to a named failure condition and a checklist item.

Section 6.1 lists three failure conditions, but all three describe an *inert*
gate.  The full-corpus result is a different kind of failure: the combination is
actively harmful at any weights because its members differ in quality.  That
deserves a fourth condition, and the reporting checklist deserves the item that
makes such dilution detectable - member-level scores.  The checklist count is
updated wherever it is stated.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

COND_D_EN = ("\n\n**Condition D: heterogeneous members.** The three conditions above describe an inert gate. "
             "The fourth is different in kind. When the members of a fusion differ in quality, the "
             "combination is bounded by the weighted mean of its members plus whatever diversity gain "
             "they contribute [9], so it cannot be repaired by re-weighting: the bound is a property of "
             "the member set, not of the gate. On the capped populations the four feature views score "
             "within 0.002 of one another (Table 4a) and the bound is slack. On the uncapped corpus the "
             "full-feature view falls 0.021397 behind the chi-square view, and one such member inside a "
             "four-way average accounts for the whole measured deficit: 0.021397/4 = 0.005349 predicted "
             "against -0.005533 observed. The corresponding diagnostic is therefore a comparison of "
             "member scores, not of weights.")

COND_D_ZH = ("\n\n**条件 D：成员异质。** 前三个条件描述的是门控失效，第四类性质不同：当参与融合的成员质量不齐时，"
             "集成的上限由各成员得分的加权平均加上它们提供的多样性收益决定 [9]，因此无法靠重新分配权重修复"
             "——这个界是成员集合的属性，不是门控的属性。在截断总体上，四个特征视图的得分相差不到 0.002（表 4a），"
             "该界很松；而在全语料上，全特征视图比卡方视图低 0.021397，四路平均中一个这样的成员就解释了全部实测差异："
             "预测 0.021397/4 = 0.005349，实测 −0.005533。相应的诊断因此是比较成员得分，而不是比较权重。")

EN: list[tuple[str, str]] = [
    ("### 6.1 Three failure conditions for conditional weighting",
     "### 6.1 Four failure conditions for conditional weighting"),
    ("The conditions of Section 4.3 and the measurements of Section 5.3 together characterise three "
     "failure modes. They are not mutually exclusive but form a hierarchy from strongest to weakest.",
     "The conditions of Section 4.3 and the measurements of Section 5.3 together characterise four "
     "failure modes. The first three describe an inert gate, whose weights cannot move a label; the "
     "fourth describes a combination that is harmful at any weights. They are not mutually exclusive "
     "but form a hierarchy from strongest to weakest."),
    ("The measured normalised weight entropy is 0.99998, squarely inside this regime.",
     "The measured normalised weight entropy is 0.99998, squarely inside this regime." + COND_D_EN),
    ("The three conditions yield an operational diagnostic sequence: **first measure the weight "
     "entropy, then the prediction-disagreement rate, and only then look at the performance "
     "difference.** If entropy is close to 1 and the disagreement count is 0, further tuning of the "
     "gate will not help, because the problem does not lie in the gate.",
     "The four conditions yield an operational diagnostic sequence: **first measure the weight "
     "entropy, then the prediction-disagreement rate, then the spread across member scores, and only "
     "then look at the performance difference.** If entropy is close to 1 and the disagreement count "
     "is 0, further tuning of the gate will not help, because the problem does not lie in the gate. If "
     "the member scores span more than the difference you care about, the fusion is bounded by its "
     "weakest member and no weighting scheme will recover it."),
    ("we recommend that studies on public intrusion-detection datasets report at least the following "
     "eight items.",
     "we recommend that studies on public intrusion-detection datasets report at least the following "
     "nine items."),
    ("8. **Release of per-row predictions**: publishing the prediction and probability for every test "
     "row lets third parties recompute every aggregate.",
     "8. **Release of per-row predictions**: publishing the prediction and probability for every test "
     "row lets third parties recompute every aggregate.\n"
     "9. **Member-level scores for every fusion**: report the score of each member alongside the fused "
     "result. An equal-weight fusion is bounded by its members, so a fusion reported without them "
     "cannot be checked for the dilution failure of Condition D."),
]

ZH: list[tuple[str, str]] = [
    ("### 6.1 条件加权失效的三类条件", "### 6.1 条件加权失效的四类条件"),
    ("第 4.3 节的命题与第 5.3 节的测量共同刻画了三类失效条件。它们不是互斥的，而是从强到弱的三个层次。",
     "第 4.3 节的命题与第 5.3 节的测量共同刻画了四类失效条件。前三类描述的是门控失效——无论权重如何都改不动标签；"
     "第四类描述的是集成本身在任意权重下都有害。它们不是互斥的，而是从强到弱的层次。"),
    ("本文测得的归一化权重熵为 0.99998，直接落在这一情形。",
     "本文测得的归一化权重熵为 0.99998，直接落在这一情形。" + COND_D_ZH),
    ("三类条件给出一个可操作的诊断流程：**先测权重熵，再测预测分歧，最后才看性能差。** "
     "如果权重熵接近 1 且分歧条数为 0，那么继续调门控的超参数不会带来增益，因为问题不在超参数。",
     "四类条件给出一个可操作的诊断流程：**先测权重熵，再测预测分歧，然后是成员得分的离散度，最后才看性能差。** "
     "如果权重熵接近 1 且分歧条数为 0，那么继续调门控的超参数不会带来增益，因为问题不在超参数；"
     "如果成员得分的跨度超过你关心的差异量级，那么集成的上限由最弱成员决定，任何权重方案都救不回来。"),
    ("我们建议在基于公开数据集的入侵检测研究中至少报告以下八项。",
     "我们建议在基于公开数据集的入侵检测研究中至少报告以下九项。"),
    ("8. **逐样本预测的发布**：公开每条测试样本的预测与概率，使聚合指标可被第三方重算。",
     "8. **逐样本预测的发布**：公开每条测试样本的预测与概率，使聚合指标可被第三方重算。\n"
     "9. **任何融合的成员级得分**：在融合结果之外，同时报告每个成员的得分。等权融合受其成员约束，"
     "因此只报融合结果、不报成员得分的论文无法检验是否发生了条件 D 所述的稀释失效。"),
]


def apply(path: Path, pairs: list[tuple[str, str]], label: str) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            print(f"  [{label}] already applied: {old[:40]}...")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {label}: {old[:70]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  [{label}] updated")


def main() -> int:
    apply(BASE / "English_SCI_Manuscript_v4.md", EN, "English")
    apply(BASE / "中文SCI论文_v4_重构版.md", ZH, "Chinese")
    print("DILUTION_CONDITION_ADDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
