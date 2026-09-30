"""Add the three experiments that answer "is the data information incomplete?".

Run for this round:
  * a higher-capacity gate (gradient-boosted risk model instead of logistic) on
    the same four experts, ten seeds - does the inertness survive capacity?
  * a feature-budget sweep (k = 20 / 40 / 80, three seeds) of the same-members
    comparison - where does the gate start to act?
  * the balanced control extended from three to ten seeds.

This script states the results in both manuscripts.  No measured value is
changed: the three-seed balanced-control number stays as the table value and the
ten-seed value is reported as a robustness extension.
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
        "The gate search, the row-wise weight records and the expert-diversity suite are provided "
        "in Supplementary S08-S09, S16 and S18.",
        "**Measurement 7: a higher-capacity gate still cannot act.** The gate's risk models are "
        "logistic regressions, so its inertness could be a property of that model class rather "
        "than of the data. Holding the four experts, the folds and the seeds fixed, we replaced "
        "the risk model with a gradient-boosted tree ensemble (200 iterations, 31 leaves) and "
        "repeated the ten-seed comparison against the equal-weight fusion of the same experts. "
        "The high-capacity gate gains **+0.000050** Macro-F1 against the logistic gate's "
        "**+0.000010**, and changes **28 of 79,860** test predictions against the logistic "
        "gate's one. Both remain an order of magnitude inside the 0.005 margin, so the inertness "
        "is a property of the experts rather than of the capacity of the risk model.\n\n"
        "The gate search, the row-wise weight records and the expert-diversity suite are provided "
        "in Supplementary S08-S09, S16 and S18.",
    ),
    (
        "Per-seed paired statistics, per-class reports and the scale summaries for all three runs "
        "are provided in Supplementary S27-S29.",
        "**Feature-budget sensitivity.** The operating point fixes k = 60 per view. Repeating the "
        "same-members comparison at other budgets (three seeds, 7,986 test rows each) shows where "
        "the gate starts to act: at k = 20 the views diverge, the gate gains **+0.004288** "
        "Macro-F1 and changes **40 of 23,958** labels - still inside the 0.005 margin; at k = 40 "
        "and k = 80 it changes **exactly zero** labels on the same 23,958 rows. The boundary is "
        "therefore not an artefact of one feature budget: the gate acts only when the views are "
        "dissimilar enough, and where it does act the effect stays inside the smallest "
        "equivalence margin used in this study.\n\n"
        "**Balanced control at ten seeds.** The balanced control was reported on three seeds "
        "(Table 4(b)); extending it to the same ten seeds gives 0.962665 +/- 0.001124 Macro-F1 "
        "(range 0.960487-0.964448) against 0.961807 on three seeds. The class-prior effect "
        "therefore moves from +0.0725 to +0.0734 and keeps its order of magnitude.\n\n"
        "Per-seed paired statistics, per-class reports and the scale summaries for all three runs "
        "are provided in Supplementary S27-S29.",
    ),
    (
        "No intervention that fixes disagreement while holding everything else constant was run.",
        "The one intervention that was run is on the model side: replacing the gate's logistic "
        "risk model with a gradient-boosted ensemble leaves the gain at +0.000050, well inside the "
        "margin (Section 5.3). A data-level intervention that makes the experts genuinely "
        "dissimilar without changing anything else remains untested.",
    ),
]

ZH_EDITS: list[tuple[str, str]] = [
    (
        "门控搜索、逐行权重记录与专家多样性实验见补充材料 S08–S09、S16 与 S18。",
        "**测量七：更高容量的门控依然无法起作用。** 门控的风险模型用的是逻辑回归，因此惰性"
        "可能被归因于该模型类而非数据本身。我们固定四个专家、折数与随机种子，把风险模型换成"
        "梯度提升树集成（200 轮、31 叶），在同样四个专家的等权融合上重跑十种子比较："
        "高容量门控的增益为 **+0.000050**（逻辑回归门控为 **+0.000010**），"
        "改判 **79 860 条中的 28 条**（逻辑回归门控为 1 条）。两者都仍比 0.005 边界小一个数量级，"
        "说明惰性来自专家本身，而不是风险模型的容量。\n\n"
        "门控搜索、逐行权重记录与专家多样性实验见补充材料 S08–S09、S16 与 S18。",
    ),
    (
        "三次运行的逐种子配对统计、类别级报告与规模汇总见补充材料 S27–S29。",
        "**特征预算敏感性。** 操作点固定每视图 k = 60。在其它预算上重复同成员比较"
        "（三个种子，每个 7 986 条测试行）可以定位门控开始起作用的位置：k = 20 时视图分化，"
        "门控增益 **+0.004288**、改判 **23 958 条中的 40 条**，仍落在 0.005 边界内；"
        "k = 40 与 k = 80 时在同样的 23 958 条上改判 **恰好为 0 条**。"
        "因此这一边界不是某一特征预算的产物：只有当视图足够分化时门控才会起作用，"
        "而它起作用时的幅度仍未超出本文使用的最小等价边界。\n\n"
        "**平衡控制总体扩到十种子。** 平衡控制此前只报告三个种子（表 4(b)）；"
        "扩到同样的十个种子后 Macro-F1 为 0.962665 ± 0.001124（范围 0.960487–0.964448），"
        "三种子时为 0.961807。类别先验效应因此从 +0.0725 移到 +0.0734，量级不变。\n\n"
        "三次运行的逐种子配对统计、类别级报告与规模汇总见补充材料 S27–S29。",
    ),
    (
        "我们没有做「固定分歧、只改变其余条件」的干预实验。",
        "我们做过的唯一干预在模型侧：把门控的逻辑回归风险模型换成梯度提升树集成后，"
        "增益仍只有 +0.000050，远在边界之内（见 5.3 节）。"
        "在数据侧构造真正互不相似的专家、同时不改变其它条件，这一干预仍未做。",
    ),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        if anchor not in text:
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(anchor)} times: "
                             f"{anchor[:60]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    for path, edits in ((EN, EN_EDITS), (ZH, ZH_EDITS)):
        applied = apply(path, edits)
        text = path.read_text(encoding="utf-8")
        for marker in ("0.000050", "0.004288", "0.962665"):
            if marker not in text:
                raise SystemExit(f"{path.name}: missing {marker}")
        print(f"{path.name}: {applied} insertion(s)")
    print("OPTIMISATION_EXPERIMENTS_ADDED")


if __name__ == "__main__":
    main()
