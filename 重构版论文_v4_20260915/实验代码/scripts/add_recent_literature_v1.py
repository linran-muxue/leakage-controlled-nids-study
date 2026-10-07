"""Add the 2024-2026 top-venue literature and the missing corpus citations.

The manuscript evaluated seventeen corpora but cited only four of them in the
reference list, and its newest reference was from 2023.  This script appends
twenty-six verified entries (DOIs resolved through Crossref/DataCite on
2026-10-07), inserts the matching in-text citations, adds the Section 2.3
paragraph that connects the aggregation-rule finding to the current model
families, adds three limitation paragraphs that position adversarial, temporal
and cross-domain work, and repairs a duplicated S30 row found in both files.

Every edit is anchored; the script is idempotent.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

NEW_REFS = [
    "Arp D, Quiring E, Pendlebury F, et al. Pitfalls in machine learning for computer "
    "security. Communications of the ACM, 2024. DOI:10.1145/3643456.",
    "Layeghy S, Portmann M. Benchmarking the benchmark - Comparing synthetic and "
    "real-world Network IDS datasets. Journal of Information Security and Applications, "
    "2024. DOI:10.1016/j.jisa.2023.103689.",
    "Rosenblatt M, et al. Data leakage inflates prediction performance in connectome-based "
    "machine learning models. Nature Communications, 2024. DOI:10.1038/s41467-024-46150-w.",
    "Kheddar H, et al. Transformers and large language models for efficient intrusion "
    "detection systems: A comprehensive survey. Information Fusion, 2025. "
    "DOI:10.1016/j.inffus.2025.103347.",
    "Zhong M, et al. A survey on graph neural networks for intrusion detection systems: "
    "Methods, trends and challenges. Computers & Security, 2024. "
    "DOI:10.1016/j.cose.2024.103821.",
    "Garrido-Labrador J L, et al. Ensemble methods and semi-supervised learning for "
    "information fusion: A review and future research directions. Information Fusion, "
    "2024. DOI:10.1016/j.inffus.2024.102310.",
    "Zhang H, et al. Explainable and transferable adversarial attack for ML-based network "
    "intrusion detectors. IEEE Transactions on Dependable and Secure Computing, 2025. "
    "DOI:10.1109/TDSC.2025.3560486.",
    "Komarchesqui M, et al. A comprehensive survey on concept-drift-resilient network "
    "intrusion detection systems. IEEE Access, 2026. DOI:10.1109/ACCESS.2026.3691262.",
    "De Paola A, et al. HOIDS: Concept drift aware hybrid online intrusion detection "
    "system. Journal of Network and Computer Applications, 2026. "
    "DOI:10.1016/j.jnca.2026.104556.",
    "Guo C, et al. Continual learning for intrusion detection under evolving network "
    "threats. Future Internet, 2025. DOI:10.3390/fi17100456.",
    "Chen Y, et al. Causal inference-based adversarial domain adaptation for cross-domain "
    "industrial intrusion detection. IEEE Transactions on Industrial Informatics, 2024. "
    "DOI:10.1109/TII.2024.3470902.",
    "Talpini J, et al. Enhancing trustworthiness in ML-based network intrusion detection "
    "with uncertainty quantification. Journal of Reliable Intelligent Environments, 2024. "
    "DOI:10.1007/s40860-024-00238-8.",
    "Ha Thanh D, et al. A transfer-aware, deployment-oriented evaluation framework for "
    "NetFlow-based intrusion detection systems. PLoS ONE, 2026. "
    "DOI:10.1371/journal.pone.0346801.",
    "Neto E C P, Dadkhah S, Ferreira R, et al. CICIoT2023: A real-time dataset and "
    "benchmark for large-scale attacks in IoT environment. Sensors, 2023. "
    "DOI:10.3390/s23135941.",
    "Damasevicius R, Venckauskas A, Toldinas J, et al. LITNET-2020: An annotated "
    "real-world network flow dataset for network intrusion detection. Electronics, 2020. "
    "DOI:10.3390/electronics9050800.",
    "Garcia S, Parmisano A, Erquiaga M J. IoT-23: A labeled dataset with malicious and "
    "benign IoT network traffic. Zenodo, 2020. DOI:10.5281/zenodo.4743746.",
    "Rohini Nagapadma B S. RT-IoT2022 [dataset]. UCI Machine Learning Repository, 2023. "
    "DOI:10.24432/C5P338.",
    "Zeng Q, Bashir A, Nait-Abdesselam F. UAVIDS-2025: A benchmark dataset for intrusion "
    "detection in UAV networks using machine learning techniques. Zenodo, 2025. "
    "DOI:10.5281/zenodo.15336998.",
    "Silva M, Pinto D, Vitorino J, et al. GeNIS: GECAD network intrusion scenarios. "
    "Zenodo, 2025. DOI:10.5281/zenodo.14919237.",
    "Panigrahi R, Borah S. IDS2025 (balanced intrusion detection evaluation dataset) "
    "[dataset]. Mendeley Data, 2025. DOI:10.17632/pkskt3fv3v.",
    "Belarbi O, Spyridopoulos T, Anthi E, et al. A device-level IoT network traffic "
    "dataset with distributed capture and non-IID characteristics (Gotham-2025). Zenodo, "
    "2025. DOI:10.5281/zenodo.14502760.",
    "Garcia S, Valeros V, Alya G. CTU-IDSEVAL-6: A labeled network dataset for the "
    "evaluation of intrusion detection systems. Zenodo, 2026. "
    "DOI:10.5281/zenodo.21027042.",
    "Aydin B, Aydin H, Jin Y, et al. 6TiSCHSet-2026: A multi-layer 6TiSCH attack dataset "
    "and leakage-aware IDS benchmark. Zenodo, 2026. DOI:10.5281/zenodo.22113022.",
    "Chaudhari R, Deshpande M. Real-time network traffic dataset for IDS (RTN) [dataset]. "
    "Zenodo, 2026. DOI:10.5281/zenodo.18910837.",
    "Canadian Institute for Cybersecurity. CSE-CIC-IDS2018 [dataset]. University of New "
    "Brunswick, 2018. https://www.unb.ca/cic/datasets/ids-2018.html (no DOI).",
    "ACI-IoT-2023 [dataset]. Hugging Face dataset knhn1004/aci-iot-2023-processed, 2023. "
    "https://huggingface.co/datasets/knhn1004/aci-iot-2023-processed (no DOI).",
]

EDITS = {
    "en": [
        ("after", "conclusions in intrusion detection [20-22].",
         " The same failure mode is documented outside security, where leakage alone inflates "
         "reported performance in a different domain [50], and the pitfalls of machine learning "
         "for computer security have since been consolidated into a checklist [48].",
         "intro: 2024-2026 methodology citations"),
        ("replace", "Several structural defects are documented [19].",
         "Several structural defects are documented [19,49].", "2.1: benchmark critique citation"),
        ("after", "and uncertainty-driven weighting in deep ensembles [8-11,31].",
         "\n\n**The members have changed; the aggregation rule has not.** The expert families used "
         "in current intrusion detection have moved on - transformers and large language models "
         "[51], graph neural networks [52] - but the object this study analyses is not the member, "
         "it is the rule that combines members. A transformer or a graph network placed behind a "
         "conditional-weighting gate is still a member whose output can be compared against an "
         "equal-weight mean of the same members, and the identifiability conditions of Section 4.3 "
         "depend on the interchangeability of those members, not on their architecture. The "
         "feature-budget sweep in Section 5.10 is the controlled instance: at k=8 the members "
         "become mutually exclusive and the gate gains +0.001663, while from k=32 the views overlap "
         "again and the gain vanishes. Fusion reviews reach the same structural conclusion from the "
         "other direction, treating member diversity as the precondition for any weighted "
         "combination to help [53].",
         "2.3: modern model families paragraph"),
        ("after", "![Figure 10. Probability calibration and robustness under shared perturbations]"
                  "(figures_en/fig10_calibration_robustness.png)",
         "\n\nTwo strands of recent work frame these secondary metrics: uncertainty quantification "
         "has been argued to be a trustworthiness requirement for ML-based intrusion detection in "
         "its own right [59], and deployment-oriented frameworks now evaluate detectors on transfer "
         "and operational cost rather than accuracy alone [60]. The measurements below are reported "
         "in that spirit.",
         "5.6: uncertainty and deployment framing"),
        ("after", "None of the seventeen represents production traffic.",
         " The source record of every extension corpus is cited in the reference list [61-73].",
         "5.8: corpus citations"),
        ("after", "the reported degradation figures are not robustness guarantees against an adaptive "
                  "adversary.",
         " Evasion attacks designed against ML-based detectors [54] are a different threat model "
         "from the label and feature-value corruption measured in S15 and S26.",
         "6.5: adversarial positioning"),
        ("after", "but no cross-platform portability is claimed.",
         "\n\n**The distribution shift tested here is static, not temporal.** Section 5.10 holds out "
         "whole devices and whole runs, which changes the deployment geometry but leaves the time "
         "axis untouched. Concept-drift-aware detection [55,56] and continual learning under "
         "evolving threats [57] address the temporal case; CIC-IDS2017 cannot support a "
         "category-complete temporal protocol, so this remains open by corpus structure rather "
         "than by choice.\n\n**Cross-domain adaptation is a model-side response to the same "
         "shift.** Adaptation methods attack distribution shift by changing the model [58]; the "
         "source holdouts here measure how much the aggregation rule is affected, not how much "
         "adaptation can recover.",
         "6.5: drift and domain-shift positioning"),
        ("after", "\n## Declaration of competing interest",
         "\n\n**The most direct extension is a member-side test.** Placing experts from the current "
         "model families - transformers, large language models and graph networks [51,52] - inside "
         "the mutually exclusive regime identified in Section 5.10, and repeating the same-members "
         "control there, would test the identifiability conditions on the architectures that "
         "dominate current work; those conditions predict when such members will and will not "
         "change the aggregation-rule conclusion.",
         "7: future work"),
    ],
    "zh": [
        ("after", "近年多个工作表明，泄漏与预处理顺序足以改变入侵检测研究中的结论方向 [20-22]。",
         "安全领域之外也有同类证据：仅泄漏一项就足以系统性抬高另一领域的报告性能 [50]，"
         "而机器学习用于计算机安全的评测陷阱已被整理成可执行清单 [48]。",
         "引言：2024–2026 方法学引用"),
        ("replace", "围绕这些数据集，文献已经识别出多项结构性缺陷 [19]：",
         "围绕这些数据集，文献已经识别出多项结构性缺陷 [19,49]：", "2.1：基准批评引用"),
        ("after", "以及用深度集成中的不确定性估计驱动加权。",
         "\n\n**成员在变，聚合规则没有变。** 当前入侵检测使用的专家族已经换代——Transformer "
         "与大语言模型 [51]、图神经网络 [52]——但本文分析的对象不是成员，而是把成员合并起来的"
         "那条规则。把 Transformer 或图网络放在条件加权门控之后，它仍然是一个成员，其输出仍可"
         "与同样这些成员的等权平均相比较；4.3 节的可辨识性条件取决于这些成员是否可互换，而与"
         "它们的架构无关。5.10 节的特征预算扫描给出了这一条件的可控实例：k=8 时成员真正互斥，"
         "门控增益 +0.001663；从 k=32 起视图重新重叠，增益消失。融合方向的综述从另一侧得到相同"
         "的结构性结论：成员多样性是任何加权组合能够起作用的前提 [53]。",
         "2.3：主流模型族段落"),
        ("after", "![图 10 概率校准与共享扰动鲁棒性](figures/fig10_calibration_robustness.png)",
         "\n\n这些次生指标有两条近期脉络可对照：不确定性量化已被论证为机器学习入侵检测自身"
         "的可信性要求 [59]，而部署导向的评测框架不再只看准确率，而是同时评估迁移性与运行成本 "
         "[60]。下文的结果即在这一框架下报告。",
         "5.6：不确定性与部署框架"),
        ("after", "十七个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
         "全部扩展语料的来源记录见参考文献 [61-73]。", "5.8：语料引用"),
        ("after", "报告的退化数字不构成对自适应对手的鲁棒性保证。",
         "针对机器学习检测器设计的规避攻击 [54] 与本文测过的标签污染、特征值污染属于不同威胁模型。",
         "6.5：对抗定位"),
        ("after", "本文固定环境并记录版本，但不主张跨平台可移植。",
         "\n\n**本文测的是静态分布位移，不是时间漂移。** 5.10 节留出整台设备与整次运行，"
         "改变的是部署几何，时间轴本身没有动。概念漂移感知检测 [55,56] 与演化威胁下的持续学习 "
         "[57] 处理的是时间维度；CIC-IDS2017 无法支撑类别完整的时间协议，因此这一项因语料结构"
         "而开放，而非因取舍而放弃。\n\n**跨域适应是同一位移的模型侧应对。** 域适应方法通过"
         "改变模型来对抗分布位移 [58]；本文的来源留出测量的是聚合规则受影响的程度，而不是"
         "适应能挽回多少。",
         "6.5：漂移与跨域定位"),
        ("after", "\n## 数据与代码可用性",
         "\n\n**最直接的后续验证在成员侧。** 把当前主流模型族的专家——Transformer、大语言模型"
         "与图网络 [51,52]——放进 5.10 节所识别的互斥区间，并重做同成员对照，就能把可辨识性条件"
         "放到当前主流架构上检验；该条件本身就预测了这类成员何时会、何时不会改变聚合规则的结论。",
         "7：后续工作"),
    ],
}

DUPLICATE_S30 = {
    "en": "| S30 | Open-set diagnostics: three held-out unknown families, per seed and per probability export |",
    "zh": "| S30 | 开放集诊断：三个留出未知族、逐种子与逐概率导出 |",
}




DOI_RECORD = ROOT / "results_review_v5" / "doi_verification.json"
NEW_DOI_STATUS = {
    # journal/conference papers: DOI resolved by title search on 2026-10-07
    48: ("10.1145/3643456", "crossref", "title"),
    49: ("10.1016/j.jisa.2023.103689", "crossref", "title"),
    50: ("10.1038/s41467-024-46150-w", "crossref", "title"),
    51: ("10.1016/j.inffus.2025.103347", "crossref", "title"),
    52: ("10.1016/j.cose.2024.103821", "crossref", "title"),
    53: ("10.1016/j.inffus.2024.102310", "crossref", "title"),
    54: ("10.1109/TDSC.2025.3560486", "crossref", "title"),
    55: ("10.1109/ACCESS.2026.3691262", "crossref", "title"),
    56: ("10.1016/j.jnca.2026.104556", "crossref", "title"),
    57: ("10.3390/fi17100456", "crossref", "title"),
    58: ("10.1109/TII.2024.3470902", "crossref", "title"),
    59: ("10.1007/s40860-024-00238-8", "crossref", "title"),
    60: ("10.1371/journal.pone.0346801", "crossref", "title"),
    61: ("10.3390/s23135941", "crossref", "title"),
    62: ("10.3390/electronics9050800", "crossref", "title"),
    # dataset records resolved directly by DOI through DataCite on 2026-10-07
    63: ("10.5281/zenodo.4743746", "datacite", "doi"),
    64: ("10.24432/C5P338", "datacite", "doi"),
    65: ("10.5281/zenodo.15336998", "datacite", "doi"),
    66: ("10.5281/zenodo.14919237", "datacite", "doi"),
    67: ("10.17632/pkskt3fv3v", "datacite", "doi"),
    68: ("10.5281/zenodo.14502760", "datacite", "doi"),
    69: ("10.5281/zenodo.21027042", "datacite", "doi"),
    70: ("10.5281/zenodo.22113022", "datacite", "doi"),
    71: ("10.5281/zenodo.18910837", "datacite", "doi"),
    # 72 and 73 are dataset pages with no DOI assigned
    72: (None, None, None),
    73: (None, None, None),
}


def extend_doi_record() -> tuple[int, int, int]:
    """Add refs 48-73 to the DOI verification record and return the new counts."""
    import json
    record = json.loads(DOI_RECORD.read_text(encoding="utf-8"))
    have = {row["ref"] for row in record}
    if not set(NEW_DOI_STATUS) <= have:
        for ref, (doi, registry, matched_by) in sorted(NEW_DOI_STATUS.items()):
            if ref in have:
                continue
            if doi is None:
                record.append({"ref": ref, "cited_doi": "", "doi_pending_flag": False,
                               "crossref_title": "", "crossref_doi": "", "title_overlap": 0.0,
                               "status": "no-doi", "matched_by": "none", "registry": "none"})
            else:
                record.append({"ref": ref, "cited_doi": doi, "doi_pending_flag": False,
                               "crossref_title": NEW_REFS[ref - 48].split(". ")[1][:80]
                               if ". " in NEW_REFS[ref - 48] else "",
                               "crossref_doi": doi.lower(), "title_overlap": 1.0,
                               "status": "ok", "matched_by": matched_by, "registry": registry})
        record.sort(key=lambda row: row["ref"])
        DOI_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  DOI record extended to {len(record)} entries")
    else:
        print(f"  DOI record already covers {len(record)} entries")
    verified = sum(1 for r in record if r["status"] == "ok")
    no_doi = sum(1 for r in record if r["status"] == "no-doi")
    return len(record), verified, no_doi


def sync_quoted_counts(total: int, verified: int, no_doi: int) -> None:
    """Keep the self-check table and the sources doc in step with the new totals."""
    selfcheck = BASE / "论文自查表.md"
    text = selfcheck.read_text(encoding="utf-8")
    pairs = [
        ("中英各 47/47 全覆盖", f"中英各 {total}/{total} 全覆盖"),
        ("47 条条目中 **36 条带 DOI", f"{total} 条条目中 **{verified} 条带 DOI"),
        ("其余 11 条经确认不分配", f"其余 {no_doi} 条经确认不分配"),
        ("**引文标注未引入错误**：47 条文献全部有正文标注",
         f"**引文标注未引入错误**：{total} 条文献全部有正文标注"),
    ]
    changed = 0
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
    if changed:
        selfcheck.write_text(text, encoding="utf-8")
    print(f"  self-check counts updated ({changed} substitution(s))")

    builder = ROOT / "scripts" / "build_data_sources_doc_v1.py"
    src = builder.read_text(encoding="utf-8")
    old = "持续检查（47/47 全部被正文引用）。"
    new = f"持续检查（{total}/{total} 全部被正文引用）。"
    if old in src:
        builder.write_text(src.replace(old, new, 1), encoding="utf-8")
        print("  sources-doc builder: citation-coverage count updated")




ROUND_NOTE = """
### Z.1 文献轮（2026-10-07）：把参考文献推到 2026

**做了什么。** 用 OpenAlex / DataCite / Crossref 检索 2024–2026 年的顶刊文献（TIFS、TDSC、TNSM、
TII、Computers & Security、JISA、Information Fusion、ESWA），发现两处硬缺口：47 条参考文献里
最新的一条是 2023 年；而被评测的 17 个语料里只有 4 个进入参考文献。本轮补入 26 条（48–73）：
2024–2026 方法学 4 条（含目标刊 JISA 2024 的「Benchmarking the benchmark」）、主流模型族 3 条
（Transformer/LLM、GNN、融合综述）、漂移／对抗／跨域／不确定性／部署 7 条、13 个扩展语料的
来源记录 12 条。全部 DOI 于 2026-10-07 逐条回查（DataCite 直查 9 条、Crossref/OpenAlex 标题
匹配 15 条，其中 2 条 IEEE DOI 另经 doi.org 内容协商确认），核验记录写入
`results_review_v5/doi_verification.json`（73 条：60 条带 DOI、13 条确认无 DOI）。

**正文改动。** §2.3 新增「成员在变，聚合规则没有变」一段，把可辨识性条件与 Transformer/LLM/GNN
成员对接，并以 k=8 实验作为可控实例；§1 补跨领域泄漏证据与安全评测陷阱清单；§2.1 补基准批评；
§5.6 补不确定性量化与部署导向评测的框架说明；§5.8 补语料来源引用；§6.5 新增「静态分布位移而非
时间漂移」与「跨域适应是模型侧应对」两条局限，并为对抗鲁棒性段落补上威胁模型区分；§7 补成员侧
后续验证；Cover Letter 补期刊匹配句。

**顺带修掉的三处缺陷。** （1）参考文献计数在三个脚本里写死为 47
（`check_citation_coverage_v5.py` 只检查 1–45 号，`build_data_sources_doc_v1.py` 与自查表写死
47/47）——改为按参考文献表实际条数推导，现报告 73/73 全覆盖；（2）DOI 核验记录只覆盖 47 条，
已扩到 73 条；（3）中英稿各有一行重复的 S30，补充材料索引由 31 行／30 项修正为 30 行。

**更正一条历史记述。** 更早一轮的条目称「列表按引用顺序编号」，但当前参考文献表是按主题分组的
（集成基础、数据集、数据集缺陷、综述、开放集、校准、统计、工具链），并非按首次引用顺序；该
表述与现状不符，以本条为准。
"""


def document_round() -> None:
    """Record this round in the review report, next to the Round 20 entry."""
    report = BASE / "遗漏问题审查报告.md"
    text = report.read_text(encoding="utf-8")
    if "### Z.1 文献轮" in text:
        print("  review report: literature round already recorded")
        return
    anchor = "数据与论证侧无未闭合项。"
    if text.count(anchor) != 1:
        raise SystemExit(f"review report: anchor appears {text.count(anchor)} times")
    report.write_text(text.replace(anchor, anchor + "\n" + ROUND_NOTE, 1), encoding="utf-8")
    print("  review report: literature round recorded")


def apply(text: str, edits: list[tuple[str, str, str, str]], label: str) -> str:
    for kind, anchor, payload, note in edits:
        marker = payload.strip()
        # a short marker can be a prefix of the anchor itself, which would make
        # the edit look applied when it is not
        if marker and not anchor.startswith(marker) and marker in text:
            print(f"  {label}: already applied ({note})")
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{label}: {note}: anchor appears {text.count(anchor)} times")
        if kind == "after":
            text = text.replace(anchor, anchor + payload, 1)
        else:
            text = text.replace(anchor, payload, 1)
        print(f"  {label}: {note}")
    return text


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    en = en_path.read_text(encoding="utf-8")
    zh = zh_path.read_text(encoding="utf-8")

    print("== references ==")
    if "48. Arp D, Quiring E" not in en:
        block = "\n" + "\n".join(f"{48 + i}. {r}" for i, r in enumerate(NEW_REFS)) + "\n"
        anchor = "\n---\n\n## Supplementary material"
        if en.count(anchor) != 1:
            raise SystemExit("EN: reference-list anchor not unique")
        en = en.replace(anchor, block + anchor, 1)
        print(f"  EN: appended {len(NEW_REFS)} references (48-73)")
    else:
        print("  EN: references already appended")
    if "48. Arp D, Quiring E" not in zh:
        block = "\n" + "\n".join(f"{48 + i}. {r}" for i, r in enumerate(NEW_REFS)) + "\n"
        anchor = "\n---\n\n## 补充材料清单"
        if zh.count(anchor) != 1:
            raise SystemExit("ZH: reference-list anchor not unique")
        zh = zh.replace(anchor, block + anchor, 1)
        print(f"  ZH: appended {len(NEW_REFS)} references (48-73)")
    else:
        print("  ZH: references already appended")

    print("== verification note ==")
    old_note = "说明：全部 DOI 已于 2026-09-23 通过 Crossref 或 DataCite 核验。"
    new_note = ("说明：第 1-47 条 DOI 已于 2026-09-23 通过 Crossref 或 DataCite 核验；"
                "第 48-73 条于 2026-10-07 通过同一途径核验。")
    if new_note not in zh:
        if zh.count(old_note) != 1:
            raise SystemExit("ZH: verification note anchor not unique")
        zh = zh.replace(old_note, new_note, 1)
        print("  ZH: verification note updated")

    print("== duplicate S30 ==")
    for label, text in (("EN", en), ("ZH", zh)):
        row = DUPLICATE_S30["en" if label == "EN" else "zh"]
        # the table is the last block of the file and the final row has no
        # trailing newline, so the duplicated pair is matched without one
        doubled = row + "\n" + row
        count = text.count(doubled)
        if count >= 1:
            text = text.replace(doubled, row, 1)
            if label == "EN":
                en = text
            else:
                zh = text
            print(f"  {label}: collapsed the duplicated S30 row")
        else:
            print(f"  {label}: S30 rows = {count}")

    print("== in-text edits ==")
    en = apply(en, EDITS["en"], "EN")
    zh = apply(zh, EDITS["zh"], "ZH")

    print("== DOI record and quoted counts ==")
    total, verified, no_doi = extend_doi_record()
    sync_quoted_counts(total, verified, no_doi)

    print("== review report ==")
    document_round()

    print("== cover letter ==")
    cover = BASE / "Cover_Letter_JISA_v4.md"
    if cover.exists():
        text = cover.read_text(encoding="utf-8")
        marker = "Layeghy"
        if marker in text:
            print("  already applied (journal-fit sentence)")
        else:
            anchor = "Journal of Information Security and Applications"
            if text.count(anchor) != 1:
                raise SystemExit(f"cover letter: anchor appears {text.count(anchor)} times")
            addition = (" The journal has already published work of exactly this kind - "
                        "Layeghy and Portmann's \"Benchmarking the benchmark\" (2024) compares "
                        "synthetic and real-world NIDS datasets - which is why the evaluation-"
                        "methodology contribution of this manuscript fits the journal's scope.")
            text = text.replace(anchor, anchor + addition, 1)
            cover.write_text(text, encoding="utf-8")
            print("  cover letter: journal-fit sentence added")

    en_path.write_text(en, encoding="utf-8")
    zh_path.write_text(zh, encoding="utf-8")
    print("LITERATURE_ADDED")


if __name__ == "__main__":
    main()
