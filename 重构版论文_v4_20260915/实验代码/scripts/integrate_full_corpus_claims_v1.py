"""Make the whole manuscript consistent with the full-corpus result.

Round 19 added the 2,429,503-flow run after the rest of the paper was written.
That run *reverses* the headline claim on the uncapped corpus (the difference
becomes a small but consistent deficit rather than an equivalence), so five
places that still asserted an unqualified equivalence had to be rewritten:

1. the abstract (also trimmed to stay inside the JISA 250-word limit),
2. contribution 3,
3. the sentence introducing Section 5.7 ("two further runs" -> three),
4. the sentence closing Section 5.7, which claimed the equivalence was not an
   artefact of the cap - true for the 7.8x run, false for the full corpus,
5. the first conclusion, and
6. Section 6.5, which must carry the population-dependence as a limitation.

Every anchor is asserted, so re-running is safe and a future edit that removes
an anchor fails loudly instead of silently skipping the fix.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

FULL_EN = ("The equivalence reproduces on a population 7.8 times larger but not on the uncapped "
           "2,429,503-flow corpus, where it becomes a small, consistent deficit (-0.005533, all ten "
           "seeds) at a 175-fold training cost; the IoT corpus saturates for every model.")

EN: list[tuple[str, str]] = [
    ("Reported performance differences between intrusion-detection models are sensitive to",
     "Reported differences between intrusion-detection models are sensitive to"),
    ("add NSL-KDD, UNSW-NB15 and an IoT corpus as independent benchmarks, and compare four feature views",
     "add NSL-KDD, UNSW-NB15 and an IoT corpus, and compare four feature views"),
    ("The four experts disagree on no test row, the learned weights have a normalised entropy of "
     "0.99998, and class prior and deduplication order move Macro-F1",
     "The four experts disagree on no test row, weight entropy is 0.99998, and class prior and "
     "deduplication order move Macro-F1"),
    ("Three identifiability conditions are derived, one becoming a row-wise bound: 99.91% of the "
     "23,958 test rows are provably invariant, with a median decision margin 3,469 to 5,038 times "
     "that bound.",
     "Three identifiability conditions are derived, one a row-wise bound: 99.91% of the 23,958 test "
     "rows are provably invariant, with a median decision margin 3,469-5,038 times it."),
    ("The equivalence reproduces on a population 7.8 times larger and on the IoT corpus, where every "
     "model exceeds 0.9998 Macro-F1.",
     FULL_EN),
    ("The mechanism is 4.1 times larger and 4.6 times lower in throughput than one forest, with no "
     "cost-sensitive advantage.",
     "The mechanism is 4.1 times larger and 4.6 times slower than one forest, without cost-sensitive "
     "advantage."),
    ("We contribute a reusable leakage-controlled protocol, an identifiability boundary and a "
     "quantitative map separating protocol effects from aggregation-rule differences",
     "We contribute a reusable leakage-controlled protocol, an identifiability boundary and a map "
     "separating protocol from aggregation-rule effects"),
    ("the equivalence is reproduced on a population 7.8 times larger and on a fourth, IoT-domain "
     "benchmark.",
     "the equivalence survives a 7.8-fold larger population but **breaks on the fully uncapped "
     "corpus**, where the difference becomes a small, consistent deficit."),
    ("Two further runs address the question directly.",
     "Three further runs address the question directly."),
    ("Together the two runs bound the result from both sides: the equivalence is not an artefact of "
     "the 53,237-flow cap, and it reproduces in a domain whose classes are trivially separable.",
     "Together the three runs bound the result from both sides, and the bound is narrower than a "
     "simple confirmation. The equivalence survives a 7.8-fold larger population, so it is not an "
     "artefact of the 53,237-flow cap, but it does **not** survive the fully uncapped corpus: there "
     "the difference becomes a small, consistent deficit at the 0.005 margin. The aggregation-rule "
     "difference is therefore negligible on capped populations and only becomes measurable - and "
     "negative - once the corpus is left completely unbalanced, which is the regime in which the "
     "mechanism would actually be deployed."),
    ("The cost is about an 80-fold increase in training time and a fivefold increase in batch "
     "inference time.",
     "The cost is about an 80-fold increase in training time and a fivefold increase in batch "
     "inference time. That equivalence is a property of the population, not of the mechanism: on the "
     "fully uncapped 2,429,503-flow corpus the difference turns into a consistent deficit of "
     "-0.005533 (all ten seeds, equivalent at 0.01 but not at 0.005) at a 175-fold training cost."),
    ("**File-level experiments are not temporal holdouts.**",
     "**The equivalence depends on how the population is built.** It holds on the 53,237-flow "
     "natural-prior population and on the 7.8-fold larger one, but not on the fully uncapped "
     "2,429,503-flow corpus, where the same comparison becomes a small, consistent deficit. The "
     "statement that conditional weighting is indistinguishable from equal voting must therefore "
     "always be quoted together with the population it was measured on; it is not a scale-free "
     "property.\n\n**File-level experiments are not temporal holdouts.**"),
]

FULL_ZH = ("该等价性在总体扩大 7.8 倍后依然成立，但在完全取消类别上限的 2 429 503 条语料上不再成立："
           "此时差异转为小而稳定的劣势（−0.005533，十个种子方向一致），训练代价达 175 倍；"
           "物联网语料上所有模型的 Macro-F1 均超过 0.9998。")

ZH: list[tuple[str, str]] = [
    ("该等价性在总体扩大 7.8 倍与物联网语料上同样成立，后者所有模型的 Macro-F1 均超过 0.9998。",
     FULL_ZH),
    ("且该等价性在总体扩大 7.8 倍与第四个物联网领域数据集上都可复现。",
     "该等价性在总体扩大 7.8 倍后仍成立，但在完全取消类别上限的全语料上失效，差异转为小而稳定的劣势。"),
    ("以下两组实验直接回答这一质疑。",
     "以下三组实验直接回答这一质疑。"),
    ("两组实验从两侧界定了结论：等价性既不是 53 237 条截断造成的，也会在类别高度可分的领域重现。",
     "三组实验从两侧界定了结论，而且这个界定比单纯的确认更严格：等价性在总体扩大 7.8 倍后仍成立，"
     "因此不是 53 237 条截断造成的；但它在完全取消类别上限的全语料上失效，差异转为小而稳定的劣势"
     "（0.005 边界不等价、0.01 边界等价）。也就是说，聚合规则的差异在截断总体上可以忽略，"
     "只有把语料完全放开、进入真实部署会遇到的强不平衡状态时才变得可测——而且是负的。"),
    ("代价则是训练时间增加约 80 倍、整批推理时间增加约 5.3 倍。",
     "代价则是训练时间增加约 80 倍、整批推理时间增加约 5.3 倍。需要补充的是，该等价性依赖总体构造："
     "在完全取消类别上限的 2 429 503 条语料上，差异转为 −0.005533 的稳定劣势"
     "（十种子方向一致，0.01 边界等价、0.005 边界不等价），训练代价 175 倍。"),
    ("**文件级实验不构成时间外推。**",
     "**等价性依赖总体的构造方式。** 它在 53 237 条自然先验总体与 7.8 倍扩大总体上成立，"
     "但在完全取消类别上限的 2 429 503 条语料上转为小而稳定的劣势。因此"
     "「条件加权与等权投票不可区分」这一结论必须与所测总体一同引用，它不是与规模无关的性质。\n\n"
     "**文件级实验不构成时间外推。**"),
]


def apply(name: str, pairs: list[tuple[str, str]]) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        # ``new`` may legitimately *contain* ``old`` (the Section 6.5 edit keeps
        # the original heading as its tail), so testing ``old not in text``
        # would re-apply that edit on every run and duplicate the paragraph.
        if new in text:
            print(f"  [{name}] already applied: {old[:34]}...")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {name}: {old[:70]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  [{name}] {len(pairs)} edit(s) applied")


def main() -> int:
    apply("English_SCI_Manuscript_v4.md", EN)
    apply("中文SCI论文_v4_重构版.md", ZH)
    print("FULL_CORPUS_CLAIMS_INTEGRATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
