"""Add the missing navigation layer to the two manuscripts, section by section.

The structure audit of the v4 manuscripts found the spine intact but the
navigation uneven: Section 5 opens with a roadmap, Sections 2, 3, 4 and 6 open
straight into their first subsection, the assumption block (H1-H3) is never tied
to the research questions (RQ1-RQ4), and the Results roadmap stops at 5.6, one
subsection short of the section it introduces.

This script inserts one roadmap paragraph per affected section, in both
languages, and rewrites the Results roadmap so that every subsection is named
and every RQ is mapped to the subsection that answers it.  No measured value is
touched: the added sentences contain only section and question labels.
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
    # 1.3 - tie the assumptions to the questions
    ("**RQ4 (external validity).** Do the conclusions survive beyond CIC-IDS2017, "
     "on NSL-KDD, UNSW-NB15 and file-level stress tests?",
     "**RQ4 (external validity).** Do the conclusions survive beyond CIC-IDS2017, "
     "on NSL-KDD, UNSW-NB15 and file-level stress tests?\n\n"
     "The assumptions and the questions form one chain: H1-H3 are tested in order by RQ1-RQ3, "
     "and RQ4 asks whether all three survive outside the source corpus. Section 5 answers the "
     "questions in that order, and every claim in Sections 5 and 6 is traceable to one of them."),
    # 2 - roadmap
    ("## 2. Related Work and Positioning",
     "## 2. Related Work and Positioning\n\n"
     "This section reviews the four bodies of work the design draws on - evaluation hazards in "
     "public datasets (2.1), feature selection and leakage (2.2), ensemble aggregation and "
     "adaptive weighting (2.3), and probability quality, open-set rejection and deployment cost "
     "(2.4) - and states in 2.5 the gap that motivates the controlled comparison."),
    # 3 - roadmap
    ("![Figure 1. Leakage-controlled research framework and information boundary]"
     "(figures_en/fig1_protocol_pipeline.png)",
     "![Figure 1. Leakage-controlled research framework and information boundary]"
     "(figures_en/fig1_protocol_pipeline.png)\n\n"
     "The section proceeds from provenance to population: 3.1 records the sources, retrieval "
     "dates and licences, 3.2 audits CIC-IDS2017 and defines the two research populations, 3.3 "
     "describes the two external corpora, 3.4 fixes the leakage-controlled protocol, 3.5 states "
     "the estimands and the statistical procedure, and 3.6 lists the threats the design already "
     "excludes, leaving the residual ones to 6.5."),
    # 4 - roadmap
    ("## 4. Method",
     "## 4. Method\n\n"
     "The method has five parts: the feature views and base learners (4.1), the "
     "sample-conditional weighting rule (4.2), the identifiability conditions that bound when any "
     "weighting can act (4.3), the complexity argument (4.4), and the controls and ablations that "
     "share one budget (4.5)."),
    # 5 - roadmap rewritten to cover every subsection
    ("The chapter follows RQ1 to RQ4. Section 5.1 answers the feature-selection question, "
     "Sections 5.2 and 5.3 together answer the weighting question, Section 5.4 addresses "
     "protocol robustness, Section 5.5 addresses external validity, and Section 5.6 reports "
     "calibration, robustness, latency and open-set behaviour.",
     "The chapter follows RQ1 to RQ4. RQ1 is answered in 5.1; RQ2 in 5.2, with the mechanism "
     "that explains its outcome in 5.3; RQ3 in 5.4 and again at scale in 5.7; RQ4 in 5.5. "
     "Section 5.6 reports calibration, robustness, latency and open-set behaviour, which qualify "
     "the comparisons without answering a question of their own."),
    # 6 - roadmap
    ("## 6. Discussion",
     "## 6. Discussion\n\n"
     "The discussion reads the results in four steps: the failure conditions and their hierarchy "
     "(6.1), how to interpret reported weighting gains in that light (6.2), a decision matrix for "
     "practitioners (6.3), reporting recommendations for future evaluations (6.4), and the "
     "limitations that remain (6.5)."),
    ("**A qualification on that equivalence.**",
     "**A qualification on the first conclusion.**"),
]

ZH_EDITS: list[tuple[str, str]] = [
    ("**RQ4（外部有效性）**：结论能否跨出 CIC-IDS2017，在 NSL-KDD、UNSW-NB15 以及文件级压力测试中成立？",
     "**RQ4（外部有效性）**：结论能否跨出 CIC-IDS2017，在 NSL-KDD、UNSW-NB15 以及文件级压力测试中成立？\n\n"
     "假设与问题构成一条链：H1–H3 依次由 RQ1–RQ3 检验，RQ4 检验这三条结论能否越过源语料。"
     "第 5 节按此顺序回答，第 5、6 节的每条论断都可回溯到这四个问题之一。"),
    ("## 2 相关工作",
     "## 2 相关工作\n\n"
     "本节综述设计所依赖的四类工作——公开数据集的评测缺陷（2.1）、特征选择与泄漏（2.2）、"
     "集成聚合与自适应加权（2.3）、概率质量与开放集及部署代价（2.4）——并在 2.5 给出"
     "驱动本文受控对照的研究空白。"),
    ("![图 1 泄漏受控研究框架与信息边界](figures/fig1_protocol_pipeline.png)",
     "![图 1 泄漏受控研究框架与信息边界](figures/fig1_protocol_pipeline.png)\n\n"
     "本节从来源走到总体：3.1 记录来源、检索日期与许可，3.2 审计 CIC-IDS2017 并定义两个研究总体，"
     "3.3 介绍两个外部语料，3.4 固定泄漏受控协议，3.5 说明评价对象与统计流程，"
     "3.6 列出设计上已排除的效度威胁，其余留给 6.5。"),
    ("## 4 方法",
     "## 4 方法\n\n"
     "方法分五部分：特征视图与基学习器（4.1）、样本条件加权规则（4.2）、"
     "限定加权作用边界的可辨识性条件（4.3）、复杂度论证（4.4），以及同一预算下的对照与消融（4.5）。"),
    ("本章按 RQ1 至 RQ4 的顺序组织。5.1 回答特征筛选，5.2 与 5.3 共同回答加权增益，"
     "5.4 回答协议稳健性，5.5 回答外部有效性，5.6 报告校准、鲁棒性、延迟与开放集等次生指标。",
     "本章按 RQ1 至 RQ4 的顺序组织：RQ1 由 5.1 回答；RQ2 由 5.2 回答，其机制解释在 5.3；"
     "RQ3 由 5.4 回答，并在 5.7 的规模与领域敏感性中再次检验；RQ4 由 5.5 回答。"
     "5.6 报告校准、鲁棒性、延迟与开放集等次生指标，用于限定上述比较，自身不回答研究问题。"),
    ("## 6 讨论",
     "## 6 讨论\n\n"
     "讨论分四步：四类失效条件及其层级（6.1）、据此如何解释文献中报告的加权增益（6.2）、"
     "面向实践的决策矩阵（6.3）、面向未来评测的报告建议（6.4），以及仍然存在的局限（6.5）。"),
    ("**该等价性的限定条件。**", "**对第一条结论的限定。**"),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        tail = replacement.split("\n\n")[-1]
        if tail in text:
            continue
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(f"{path.name}: anchor appears {count} times, expected once: "
                             f"{anchor[:60]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    print(f"updated {path.name}: {applied} insertion(s) applied")


def main() -> None:
    for path, edits in ((EN, EN_EDITS), (ZH, ZH_EDITS)):
        apply(path, edits)
        # the guard: every insertion must be present afterwards
        updated = path.read_text(encoding="utf-8")
        for _, replacement in edits:
            tail = replacement.split("\n\n")[-1]
            if tail not in updated:
                raise SystemExit(f"{path.name}: insertion missing after write: {tail[:60]!r}")
        print(f"{path.name}: verified")


if __name__ == "__main__":
    main()
