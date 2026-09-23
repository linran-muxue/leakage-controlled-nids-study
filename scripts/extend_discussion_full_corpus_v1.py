"""Extend the discussion with the fifth attribution factor and its guidance.

The full-corpus run shows that population construction is itself a competing
explanation for a reported weighting gain: the same comparison is an equivalence
on the capped population and a consistent deficit on the uncapped corpus.  That
belongs in three places that currently enumerate four factors, the decision
matrix, and the reporting checklist.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_ITEM5 = ("\n5. **Population construction.** The identical comparison is an equivalence on the "
            "53,237-flow capped population and a consistent deficit on the fully uncapped "
            "2,429,503-flow corpus. Neither result is wrong; the population decides which one a "
            "study reports.")

EN_ROW = ("| Decide whether to deploy conditional weighting | Equal voting on capped populations; do "
          "not deploy on strongly imbalanced corpora | Equivalence at 53,237 flows against a deficit "
          "of -0.005533 on the uncapped 2,429,503-flow corpus, all ten seeds | Forgoes a mechanism "
          "whose training cost is 175 times that of one forest |")

EN: list[tuple[str, str]] = [
    ('an observed "weighting gain" has at least four competing explanations',
     'an observed "weighting gain" has at least five competing explanations'),
    ("4. **Metric selection.** Here RCCF has a better Log Loss but a worse ECE than the equal-weight "
     "forest; reporting either metric alone supports the opposite conclusion.",
     "4. **Metric selection.** Here RCCF has a better Log Loss but a worse ECE than the equal-weight "
     "forest; reporting either metric alone supports the opposite conclusion." + EN_ITEM5),
    ("should survive control of these four factors", "should survive control of these five factors"),
    ("| Reproducibility of results | Adopt this protocol and release per-row predictions | All "
     "aggregate metrics can be recomputed from released probabilities | Extra storage and version "
     "management |",
     "| Reproducibility of results | Adopt this protocol and release per-row predictions | All "
     "aggregate metrics can be recomputed from released probabilities | Extra storage and version "
     "management |\n" + EN_ROW),
    ("4. **A clear separation of research population and target population**: how the study subset "
     "was constructed and how it differs from the full corpus and from production priors.",
     "4. **A clear separation of research population and target population**: how the study subset "
     "was constructed and how it differs from the full corpus and from production priors. Where a "
     "headline comparison is sensitive to that construction - as it is here - report it on both the "
     "capped and the uncapped population, or state explicitly which one the claim is conditioned on."),
]

ZH_ITEM5 = ("\n5. **总体构造**：同一个比较在 53 237 条截断总体上是等价，在完全取消上限的 "
            "2 429 503 条语料上却是一致劣势。两者都不算错——是总体决定了研究报告哪一个。")

ZH_ROW = ("| 是否部署条件加权 | 截断总体上用等权投票；强不平衡语料上不要部署 | 53 237 条上等价，"
          "全语料 2 429 503 条上为 −0.005533 且十种子方向一致 | 放弃一个训练代价达 175 倍的机制 |")

ZH: list[tuple[str, str]] = [
    ("至少有四种替代解释，而且四种解释在本文的对照实验中都有对应的量级。",
     "至少有五种替代解释，而且五种解释在本文的对照实验中都有对应的量级。"),
    ("4. **指标选择**：本文中 RCCF 的 Log Loss 优于等权森林而 ECE 更差；单独报告任一指标都能得到相反的结论。",
     "4. **指标选择**：本文中 RCCF 的 Log Loss 优于等权森林而 ECE 更差；单独报告任一指标都能得到相反的结论。"
     + ZH_ITEM5),
    ("都应当在控制上述四项之后仍然成立", "都应当在控制上述五项之后仍然成立"),
    ("| 结果的可复现性 | 采用本文协议并发布逐样本预测 | 全部聚合指标可由逐样本概率重算 | 需要额外的存储与版本管理 |",
     "| 结果的可复现性 | 采用本文协议并发布逐样本预测 | 全部聚合指标可由逐样本概率重算 | 需要额外的存储与版本管理 |\n"
     + ZH_ROW),
    ("4. **研究总体与目标总体的区分**：说明使用的研究子集如何被构造，以及它与全语料、与生产流量先验的差距。",
     "4. **研究总体与目标总体的区分**：说明使用的研究子集如何被构造，以及它与全语料、与生产流量先验的差距。"
     "若某个头条比较对该构造敏感（本文即如此），应在截断总体与全语料上同时报告，或明确声明结论以哪一个为条件。"),
]


def apply(name: str, pairs: list[tuple[str, str]]) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            print(f"  [{name}] already applied: {old[:34]}...")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {name}: {old[:70]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  [{name}] discussion extended")


def main() -> int:
    apply("English_SCI_Manuscript_v4.md", EN)
    apply("中文SCI论文_v4_重构版.md", ZH)
    print("DISCUSSION_EXTENDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
