"""Correct the "the experts never disagree" claim, which the data contradict.

The abstract, the conclusion and Section 4.3 all said the four experts agree on
every test row.  Re-measuring the primary population shows they disagree on
0.2%-0.5% of rows (12-53 rows per pair, ten seeds, mean 0.370%): what is true is
that the *gate* reproduces equal voting on all but one of 79,860 predictions.
The claim is corrected, the measured disagreement is added as Measurement 8, and
the abstract is trimmed back inside the JISA limit.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

MEASUREMENT_8 = (
    "**Measurement 8: how much the experts actually disagree.** The four views are not identical "
    "on the primary test set: over ten seeds their pairwise disagreements cover **0.15%-0.66%** of "
    "rows (12 to 53 rows per pair, mean **0.370%**). What is identical is the labelled output - the "
    "gate reproduces equal voting on all but one of 79,860 predictions - so the disagreements "
    "exist but sit far from the decision boundary, which is what Condition 2 asserts.\n\n"
)

EN_EDITS: list[tuple[str, str]] = [
    ("The four experts disagree on no test row, and the normalised weight entropy is 0.99998.",
    "The four experts disagree on 0.15-0.66% of test rows, yet the gate matches equal voting on all "
     "but one of 79,860 predictions; weight entropy is 0.99998."),
    ("Experts never disagree; weight entropy is 0.99998;",
     "The experts disagree on 0.15-0.66% of test rows while the gate matches equal voting on all but "
     "one of 79,860 predictions; weight entropy is 0.99998;"),
    ("Section 5 reports that gated fusion and equal voting agree on every test row.",
     "Section 5 reports that gated fusion and equal voting agree on all but one of the 79,860 test "
     "predictions compared."),
    ("Under one leakage-controlled protocol we build a 53,237-flow natural-prior population",
     "We build a 53,237-flow natural-prior population"),
    ("99.91% of the 23,958 test rows are provably invariant",
     "99.91% of 23,958 test rows are provably invariant"),
    ("(slope 0.0646, r = 0.749; association, not intervention).",
     "(slope 0.0646, r = 0.749)."),
    ("The equivalence reproduces on a population 7.8 times larger but not on the uncapped",
     "The equivalence reproduces on a 7.8-times-larger population but not on the uncapped"),
    ("the seed-level 90% and paired bootstrap intervals lie inside the 0.005 and 0.01 equivalence "
     "margins.",
     "both intervals lie inside the 0.005 and 0.01 equivalence margins."),
    ("Section 5.3 shows the weights never move a label - but the price of averaging over feature "
     "views whose quality has diverged.",
     "Section 5.3 shows the weights changed one label in 79,860 predictions - but the price of "
     "averaging over feature views whose quality has diverged."),
    ("Section 5.3 shows the weights never move a label - but the price of averaging over feature "
     "views whose quality diverges at scale",
     "Section 5.3 shows the weights changed one label in 79,860 predictions - but the price of "
     "averaging over feature views whose quality diverges at scale"),
    ("The gate search, the row-wise weight records and the expert-diversity suite are provided "
     "in Supplementary S08-S09, S16 and S18.",
     MEASUREMENT_8
     + "The gate search, the row-wise weight records and the expert-diversity suite are provided "
       "in Supplementary S08-S09, S16 and S18."),
]

ZH_EDITS: list[tuple[str, str]] = [
    ("四个专家在测试集上无任何预测分歧，权重归一化熵为 0.99998；",
     "四个专家在测试集上有 0.15%–0.66% 的行存在分歧，但门控与等权投票在 79 860 条预测中"
     "只有 1 条不同；权重归一化熵为 0.99998；"),
    ("四个专家在测试集上没有任何一条预测分歧，归一化权重熵为 0.99998；",
     "四个专家在测试集上有 0.15%–0.66% 的行存在分歧，而门控与等权投票在 79 860 条预测中"
     "只有 1 条不同；归一化权重熵为 0.99998；"),
    ("5.3 节已表明权重从不改变任何一条预测——而是对质量已经分化的特征视图做平均的代价。",
     "5.3 节已表明权重在 79 860 条预测中只改变 1 条——而是对质量已经分化的特征视图做平均的代价。"),
    ("5.3 节已表明权重从不改变任何一条预测——而是在质量随规模分化的特征视图上取平均的代价",
     "5.3 节已表明权重在 79 860 条预测中只改变 1 条——而是在质量随规模分化的特征视图上取平均的代价"),
    ("门控搜索、逐行权重记录与专家多样性实验见补充材料 S08–S09、S16 与 S18。",
     "**测量八：专家之间的真实分歧有多大。** 在主总体的测试集上，四个视图并不完全相同："
     "十个种子下两两分歧覆盖 **0.2%–0.5%** 的行（每对 12 至 53 条，均值 **0.370%**）。"
     "完全相同的是**带标签的输出**——门控与等权投票在 79 860 条预测中只有 1 条不同——"
     "因此分歧确实存在，只是远离决策边界，这正是命题 2 所断言的情形。\n\n"
     "门控搜索、逐行权重记录与专家多样性实验见补充材料 S08–S09、S16 与 S18。"),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        if anchor not in text:
            continue
        head = replacement.strip()[:80]
        if head and head in text and not replacement.startswith(anchor):
            # the insert-before-anchor edit is already in place
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(anchor)} times: "
                             f"{anchor[:60]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    # repair: the insert-before-anchor edit ran twice in the first execution, and
    # the abstract sits exactly on the JISA limit, so three words are trimmed
    zh_measurement = ("**测量八：专家之间的真实分歧有多大。** 在主总体的测试集上，四个视图并不完全相同："
                      "十个种子下两两分歧覆盖 **0.15%–0.66%** 的行（每对 12 至 53 条，均值 **0.370%**）。"
                      "完全相同的是**带标签的输出**——门控与等权投票在 79 860 条预测中只有 1 条不同——"
                      "因此分歧确实存在，只是远离决策边界，这正是命题 2 所断言的情形。")
    for path, paragraph in ((EN, MEASUREMENT_8.strip()), (ZH, zh_measurement)):
        text = path.read_text(encoding="utf-8")
        copies = text.count(paragraph)
        removed = 0
        while copies > 1:
            run = (paragraph + "\n\n") * (copies - 1)
            if run in text:
                text = text.replace(run, "", 1)
                removed += copies - 1
                break
            copies -= 1
        if removed:
            path.write_text(text, encoding="utf-8")
            print(f"{path.name}: removed {removed} duplicated measurement paragraph(s)")

    # three-word margin on the abstract
    trims = [
        ("; weight entropy is 0.99998.", "; weight entropy 0.99998."),
        ("at a 175-fold cost; the IoT corpus saturates.", "at 175-fold cost; the IoT corpus saturates."),
        ("108 gate configurations yield six distinct scores;",
         "108 gate configurations yield six scores;"),
    ]
    text = EN.read_text(encoding="utf-8")
    abstract_start = text.index("## Abstract")
    abstract_end = text.index("**Keywords:**")
    abstract = text[abstract_start:abstract_end]
    for anchor, replacement in trims:
        if anchor in abstract:
            abstract = abstract.replace(anchor, replacement, 1)
    EN.write_text(text[:abstract_start] + abstract + text[abstract_end:], encoding="utf-8")

    for path, edits in ((EN, EN_EDITS), (ZH, ZH_EDITS)):
        applied = apply(path, edits)
        text = path.read_text(encoding="utf-8")
        for banned in ("disagree on no test row", "Experts never disagree",
                       "无任何预测分歧", "没有任何一条预测分歧",
                       "weights never move a label", "权重从不改变任何一条预测"):
            if banned in text:
                raise SystemExit(f"{path.name}: stale claim survives: {banned!r}")
        print(f"{path.name}: {applied} edit(s)")
    abstract = EN.read_text(encoding="utf-8")
    abstract = abstract[abstract.index("## Abstract"):abstract.index("**Keywords:**")]
    words = len(abstract.split("## Abstract", 1)[1].split())
    print(f"English abstract: {words} words")
    if words > 250:
        raise SystemExit(f"abstract over the JISA limit: {words} words")
    print("EXPERT_DISAGREEMENT_CLAIM_FIXED")


if __name__ == "__main__":
    main()
