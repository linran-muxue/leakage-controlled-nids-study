"""Close the H2 control gap in both manuscripts with the new same-members control.

The primary comparison in the paper used a *single* equal-weight chi-square
forest as the control, while the treatment fuses four feature views.  A
supervisor reading flagged the mismatch: that comparison confounds the
aggregation rule with the composition of the ensemble.  The missing control -
the unweighted mean of the identical four experts - was run with
``scripts/run_equal_fusion_control_v1.py``: over ten seeds and 79,860 test
predictions the gated model changes exactly one label, and the Macro-F1
difference is -0.000010 (90% interval [-0.000029, +0.000008]).

This script states that control in the methods, reports it beside the existing
single-view comparison, and adds it to the abstract and the conclusion, in both
languages.  No other number is touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

EN_EDITS: list[tuple[str, str]] = [
    (
        "1. **Equal-weight control.** Same feature view, tree count and seed as the gated model. "
        "This is the direct test of H2.",
        "1. **Equal-weight fusion control (the direct test of H2).** The unweighted mean of the "
        "**identical four experts** - same feature views, same tree count, same per-expert seeds - "
        "so that the aggregation rule is the only difference from the gated model. The equal-weight "
        "chi-square forest on the same view is reported alongside it as the strongest "
        "**single-member** reference.",
    ),
    (
        "a mean difference of **-0.000456**, with five seeds favouring RCCF and five favouring "
        "the equal forest.",
        "a mean difference of **-0.000456**, with five seeds favouring RCCF and five favouring "
        "the equal forest. Against the equal-weight fusion of the **identical four experts** - the "
        "direct test of H2 - the gated model changes **one label across 79,860 test predictions** "
        "over the ten seeds and differs by **-0.000010** Macro-F1 (seed-level 90% interval "
        "[-0.000029, +0.000008]). The -0.000456 above is therefore the price of averaging in the "
        "weaker full-feature view, not an effect of gating.",
    ),
    (
        "difference between conditional weighting and an equal-weight chi-square forest is "
        "-0.000456, with the per-seed sign split five to five.",
        "difference between conditional weighting and an equal-weight chi-square forest is "
        "-0.000456, with the per-seed sign split five to five. Against the equal-weight fusion of "
        "those same four experts the gated model changes one label in 79,860 test predictions "
        "(-0.000010), which locates the single-view gap in the composition of the ensemble rather "
        "than in the gate.",
    ),
    (
        "The conclusions are bounded as follows, and these bounds should be cited alongside them.",
        "The conclusions are bounded as follows, and these bounds should be cited alongside them.\n\n"
        "**The same-members control covers the primary population.** The equal-weight fusion of the "
        "identical four experts was run on the 53,237-flow natural-prior population; on the "
        "413,209-flow and 2,429,503-flow populations the control remains the single-view "
        "equal-weight forest, so the dilution decomposition there rests on the view-gap arithmetic "
        "rather than on a measured same-members fusion.",
    ),
]

ZH_EDITS: list[tuple[str, str]] = [
    (
        "1. **等权对照**：同一特征视图、同一树数、同一随机种子的等权随机森林。这是 H2 的直接对照。",
        "1. **同成员等权融合对照（H2 的直接检验）**：对**完全相同的四个专家**"
        "（同一批特征视图、同一树数、同一组逐专家随机种子）取未加权平均，"
        "使门控模型与对照之间只差聚合规则；同一卡方视图的等权森林作为"
        "**最强单成员**参照并列报告。",
    ),
    (
        "RCCF 的 Macro-F1 为 0.889278，等权卡方森林为 0.889734，平均差 **−0.000456**，"
        "逐种子方向为五正五负。",
        "RCCF 的 Macro-F1 为 0.889278，等权卡方森林为 0.889734，平均差 **−0.000456**，"
        "逐种子方向为五正五负。对**完全相同的四个专家**做等权融合（H2 的直接检验）时，"
        "门控在十个种子共 79 860 条测试预测中只改变 **1 条**标签，Macro-F1 差为 "
        "**−0.000010**（种子级 90% 区间 [−0.000029, +0.000008]）——因此上面的 −0.000456 "
        "衡量的是把较弱的全特征视图平均进来的代价，而不是门控本身的效应。",
    ),
    (
        "条件加权森林与等权卡方森林的 Macro-F1 平均差为 −0.000456，逐种子方向五正五负；",
        "条件加权森林与等权卡方森林的 Macro-F1 平均差为 −0.000456，逐种子方向五正五负；"
        "对同样的四个专家做等权融合时，门控在 79 860 条测试预测中只改变 1 条（−0.000010），"
        "说明单视图差距来自集成成员的构成而非门控本身；",
    ),
    (
        "本文的结论受以下限制，读者在引用时应当连同这些边界一起引用。",
        "本文的结论受以下限制，读者在引用时应当连同这些边界一起引用。\n\n"
        "**同成员对照只覆盖主总体。** 完全相同的四个专家的等权融合只在 53 237 条自然先验总体上运行；"
        "在 413 209 条与 2 429 503 条两个总体上，对照仍是单视图等权森林，"
        "因此那里的稀释分解依赖视图差算术，而不是实测的同成员融合。",
    ),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        # idempotency: the tail of the replacement is the fingerprint that the
        # sentence is already there, in either language
        tail = replacement.strip()[-60:].strip()
        if tail and tail in text:
            continue
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(f"{path.name}: anchor appears {count} times, expected once: "
                             f"{anchor[:70]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    for path, edits in ((EN, EN_EDITS), (ZH, ZH_EDITS)):
        applied = apply(path, edits)
        print(f"{path.name}: {applied} edit(s) applied")
        text = path.read_text(encoding="utf-8")
        marker = "0.000010"
        if marker not in text:
            raise SystemExit(f"{path.name}: the same-members control sentence is missing")
        if text.count("79,860") + text.count("79 860") != 3:
            raise SystemExit(f"{path.name}: expected the 79,860 figure three times")
    print("EQUAL_FUSION_WORDING_OK")


if __name__ == "__main__":
    main()
