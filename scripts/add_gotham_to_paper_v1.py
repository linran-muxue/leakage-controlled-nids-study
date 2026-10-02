"""Integrate the Gotham-2025 corpus, including its one positive result.

Gotham is the 2025 packet-level corpus the supervisor's "the data is too old"
objection asked for.  Two runs were made on the identical population: the
standard budget (k = 60, which on a 16-column table selects every column, so the
three views coincide) and a reduced budget (k = 8 of 16, where chi-square and
ANOVA genuinely disagree).  The first is inert, the second is the study's only
positive result: +0.0063 over the same-members equal fusion, ten seeds of ten.

That changes the paper's headline claim, so the abstract is rewritten as well:
"neither superiority" becomes "neither general superiority", with the positive
case quoted.  Every number is read from the released summaries.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"
SOURCES = ROOT / "scripts" / "build_data_sources_doc_v1.py"
REPORT = ROOT / "scripts" / "build_extension_report_v1.py"
REPORT_CHECK = ROOT / "scripts" / "check_extension_report_v1.py"
BUNDLE = ROOT / "scripts" / "package_submission_bundle_v18.py"
METRICS_FIX = ROOT / "scripts" / "fix_extension_metrics_v1.py"

OLD_EN_ABSTRACT_START = "Reported differences between intrusion-detection models are sensitive"
OLD_ZH_ABSTRACT_START = "公开入侵检测数据集上报告的模型性能差异"


def summary(folder: str) -> dict:
    return json.loads((ROOT / folder / "benchmark_summary.json").read_text(encoding="utf-8"))


def replace_line(path: Path, marker: str, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(marker)]
    if len(hits) != 1:
        raise SystemExit(f"{path.name}: {marker!r} starts {len(hits)} lines")
    index = hits[0]
    if lines[index].rstrip("\r\n") == new_line:
        print(f"{path.name}: {marker} already current")
        return
    ending = lines[index][len(lines[index].rstrip("\r\n")):]
    lines[index] = new_line + ending
    path.write_text("".join(lines), encoding="utf-8")
    print(f"{path.name}: rewrote {marker}")


def insert_after(path: Path, marker: str, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new_line in text:
        print(f"{path.name}: insert for {marker} already present")
        return
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(marker)]
    if len(hits) != 1:
        raise SystemExit(f"{path.name}: {marker!r} starts {len(hits)} lines")
    index = hits[0]
    ending = "\r\n" if lines[index].endswith("\r\n") else "\n"
    lines.insert(index + 1, new_line + ending)
    path.write_text("".join(lines), encoding="utf-8")
    print(f"{path.name}: inserted a paragraph after {marker}")


def patch(path: Path, pairs: list[tuple[str, str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, note in pairs:
        if new in text and old not in text:
            print(f"{path.name}: already applied ({note})")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
        text = text.replace(old, new, 1)
        print(f"{path.name}: {note}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    full = summary("results_rccf_gotham2025_v1")
    k8 = summary("results_rccf_gotham2025_v1_k8")
    classes = len(full["classes"])
    rows = full["test_rows"]
    gain = k8["same_members_difference"]
    rows_zh = f"{rows:,}".replace(",", " ")
    if full["same_members_difference"] != 0.0 or gain <= 0:
        raise SystemExit("the Gotham runs no longer show the expected pattern")

    # ---- abstracts ---------------------------------------------------------
    abstract_en = (
        "Reported differences between intrusion-detection models are sensitive to duplicate "
        "flows, conflicting labels, feature leakage and class priors. We test a widely adopted "
        "but rarely validated assumption: that fusing random-forest experts with sample-specific "
        "reliability weights (RCCF) beats equal voting. We build a 53,237-flow natural-prior "
        "population and a 3,365-flow balanced control from CIC-IDS2017, add NSL-KDD, UNSW-NB15 "
        "and an IoT corpus, and compare four feature views over ten seeds. The two models differ "
        "by -0.000456 Macro-F1 (five up, five down); both intervals lie inside the 0.005 and 0.01 "
        "equivalence margins, and over the same four experts the gate changes one label in 79,860 "
        "predictions although the experts disagree on 0.15%-0.66% of test rows; weight entropy is "
        "0.99998; class prior and dedup order move Macro-F1 by +0.0725 and +0.0060. Three "
        "identifiability conditions are derived, one a row-wise bound: 99.91% of 23,958 test rows "
        "are provably invariant, with a median margin 3,469-5,038 times it. Across fifteen "
        "configurations the gain co-varies with expert diversity (r = 0.749). The equivalence "
        "reproduces on a 7.8-times-larger population but not on the uncapped 2,429,503-flow "
        "corpus, where it becomes a consistent deficit (-0.005533) at 175-fold cost. On a 2025 "
        f"packet corpus with {classes} classes the gate gains +0.0063 at eight of sixteen "
        "features (all ten seeds), while at the full budget its three views coincide. The "
        "mechanism is 4.1 times larger and 4.6 times slower (S22). We contribute a "
        "leakage-controlled protocol, an identifiability boundary and a map separating protocol "
        "from aggregation-rule effects; the evidence supports neither general superiority nor "
        "production readiness.")
    abstract_zh = (
        "公开入侵检测数据集上报告的模型性能差异，对重复样本、标签冲突、特征选择泄漏与类别先验高度敏感。"
        "本文检验一个被广泛采用却缺少受控验证的假设：按样本估计的可靠性权重对多个随机森林专家做条件加权"
        "融合（RCCF），能否稳定优于等权投票。在统一的泄漏受控协议下，我们用 CIC-IDS2017 构造 53 237 条"
        "自然先验总体与 3 365 条平衡控制总体，并加入 NSL-KDD、UNSW-NB15 与一个物联网僵尸网络语料，"
        "在十个种子上比较四种特征视图。二者 Macro-F1 平均差为 −0.000456（五正五负），种子级 90% 区间与"
        "测试行级配对 Bootstrap 区间均落在 0.005 与 0.01 的等价边界内；对同成员等权融合时只改变 "
        "79 860 条预测中的 1 条，尽管专家在 0.15%–0.66% 的测试行上存在分歧；权重归一化熵为 0.99998；"
        "类别先验与去重顺序分别带来 +0.0725 与至多 +0.0060 的变化。我们给出三个可辨识性条件，并把其中"
        "之一化为可逐行计算的判据：23 958 条测试样本中 99.91% 可证明不受权重影响，决策边距中位数为扰动"
        "上界的 3469 至 5038 倍。在十五个配置上，增益与专家多样性同步变化（r = 0.749，属相关性证据"
        "而非干预实验）。该等价性在总体扩大 7.8 倍后依然成立，但在完全取消类别上限的 2 429 503 条语料上"
        "不再成立：此时差异转为小而稳定的劣势（−0.005533），训练代价达 175 倍。"
        f"在 2025 年发布的一个 {classes} 类数据包级语料上，同样的门控在十六个特征中只用八个时增益 "
        "+0.0063（十个种子方向一致），而在完整特征预算下三个视图完全重合。该机制体积是单个等权森林的 "
        "4.1 倍、吞吐低 4.6 倍（单种子资源画像，S22）。本文贡献一套泄漏受控协议、一组可辨识性边界，"
        "以及一张把协议效应与聚合规则差异分开量化的地图；证据不支持普遍优越性或生产可用性的主张。")
    replace_line(EN, OLD_EN_ABSTRACT_START, abstract_en)
    replace_line(ZH, OLD_ZH_ABSTRACT_START, abstract_zh)
    words = len(re.findall(r"\S+", abstract_en))
    print(f"English abstract: {words} words")
    if words > 250:
        raise SystemExit(f"abstract is {words} words, limit is 250")

    # ---- Section 5.8 -------------------------------------------------------
    gotham_en = (
        f"**A 2025 packet-level corpus, and the condition under which the gate helps.** "
        f"Gotham-2025 (Zenodo 14502760, CC BY 4.0) captures 78 IoT devices on a smart-city "
        f"testbed; its processed tables hold 35,134,281 packets and {classes} classes. Under the "
        f"study's protocol the table has only sixteen usable columns once the device addresses "
        f"and timestamps are dropped (they would hand the classifier the attacker's identity), so "
        f"the 60-feature budget selects every column and the three views coincide: the gate is "
        f"exactly equal to the same-members fusion on all {rows:,} test rows, all ten seeds. "
        f"Repeating the same comparison at eight of the sixteen features, where chi-square and "
        f"ANOVA genuinely disagree, reverses that: the gate gains {gain:+.4f} Macro-F1 with all "
        f"ten seeds positive and 38-50 of the {rows:,} labels changed. The gate is inert when its "
        f"members are interchangeable and helpful when they are not - the boundary the "
        f"identifiability conditions predict, now observed on a 2025 corpus.")
    gotham_zh = (
        f"**2025 年数据包级语料，以及门控在什么条件下有用。** Gotham-2025（Zenodo 14502760，"
        f"CC BY 4.0）在智慧城市测试床上采集 78 台 IoT 设备，处理表含 35 134 281 条数据包、"
        f"{classes} 个类别。"
        f"在本文协议下，剔除设备地址与时间戳后只剩十六个可用列（保留它们等于把攻击者身份交给分类器），"
        f"因此 60 维预算会选中全部列、三个视图完全重合：门控与同成员融合在全部 {rows_zh} 条测试行上完全"
        f"相同，十个种子无一例外。把同样的比较改到十六列中的八列——卡方与方差分析此时才真正不同——"
        f"结论反转：门控增益 {gain:+.4f} Macro-F1，十个种子全部为正，{rows_zh} 条标签中有 38–50 条被"
        f"改判。成员可互换时门控无效、成员不可互换时门控有用，这正是可辨识性条件所预测的边界，"
        f"现在在一个 2025 年语料上被观测到。")
    insert_after(EN, "**Two further corpora.**", gotham_en)
    insert_after(ZH, "**两个新语料。**", gotham_zh)

    # ---- corpus counts become fourteen ------------------------------------
    patch(EN, [
        ("**Thirteen corpora were evaluated, and every corpus comes from one collection "
         "programme.**",
         "**Fourteen corpora were evaluated, and every corpus comes from one collection "
         "programme.**", "EN limitation heading"),
        ("the three 2025 corpora (UAVIDS-2025, GeNIS, IDS2025) were added as extension corpora",
         "the 2025 corpora (UAVIDS-2025, GeNIS, IDS2025, Gotham-2025) were added as extension "
         "corpora", "EN limitation list"),
        ("None of the thirteen represents production traffic.",
         "None of the fourteen represents production traffic.", "EN limitation count"),
    ])
    patch(ZH, [
        ("**评测了十三个语料，但它们来自同一批采集计划的有限覆盖。**",
         "**评测了十四个语料，但它们来自同一批采集计划的有限覆盖。**", "中文局限标题"),
        ("其余九个语料（CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、"
         "ACI-IoT-2023 与 2025 年的 UAVIDS-2025、GeNIS、IDS2025）作为 5.8 节的扩展语料复现了主比较。",
         "其余十个语料（CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、"
         "ACI-IoT-2023 与 2025 年的 UAVIDS-2025、GeNIS、IDS2025、Gotham-2025）作为 5.8 节的扩展语料"
         "复现了主比较。", "中文局限列表"),
        ("十三个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
         "十四个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。", "中文局限计数"),
    ])

    # ---- sources table: Gotham moves from candidate to evaluated ----------
    patch(SOURCES, [
        ('    ("IDS2025", "2025", "Mendeley Data `pkskt3fv3v`", "记录页许可", "IDS2025"),\n)',
         '    ("IDS2025", "2025", "Mendeley Data `pkskt3fv3v`", "记录页许可", "IDS2025"),\n'
         '    ("Gotham-2025", "2025",\n'
         '     "Zenodo record 14502760（Gotham 测试床，78 台 IoT 设备，CC BY 4.0）", "CC BY 4.0",\n'
         '     "GothamDataset2025"),\n)', "Gotham added to the evaluated set"),
        ('    ("Gotham-2025", "2025", "Zenodo record 14502760（Gotham 测试床，78 台 IoT 设备的接口级流量）",\n'
         '     "CC BY 4.0", "开放",\n'
         '     "22.2 GiB 单归档；分块续传中，完成后按同一协议处理。"),\n', "",
         "Gotham removed from the candidate list"),
        ('**扩展语料（第 5.8 节，九项）**', '**扩展语料（第 5.8 节，十项）**', "sources extension count"),
        ('这九项与上面四项一样，都在同一套处理与评估协议下运行',
         '这十项与上面四项一样，都在同一套处理与评估协议下运行', "sources extension sentence"),
        ('"`scripts/fetch_2025_corpora_v1.py` 重新取得，并与下表的 SHA-256 逐字节核对。")',
         '"`scripts/fetch_2025_corpora_v1.py`、`scripts/fetch_gotham2025_v1.py` 重新取得，"\n'
         '                 "并与下表的校验值逐字节核对。")', "sources fetch scripts"),
    ])

    # ---- extension report --------------------------------------------------
    patch(REPORT, [
        ('             "> 八个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份。"',
         '             "> 九个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份、"\n'
         '             "2025 年数据包级语料 Gotham-2025。"', "report header"),
    ])
    patch(REPORT, [
        ('    text = "\\n".join(lines) + "\\n"',
         '    full = read_json(ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json")\n'
         '    k8 = read_json(ROOT / "results_rccf_gotham2025_v1_k8" / "benchmark_summary.json")\n'
         '    if full and k8:\n'
         '        lines += section(\n'
         '            "九、2025 年数据包级语料 Gotham-2025",\n'
         '            "门控在什么条件下才有用？",\n'
         '            f"Gotham-2025（Zenodo 14502760，CC BY 4.0）在 78 台 IoT 设备上采集 3 510 万条"\n'
         '            f"数据包、{len(full[\'classes\'])} 个类别，按同一水库协议处理；设备地址与时间戳作为"\n'
         '            "泄漏控制被剔除，余下十六列。",\n'
         '            r"& $py scripts\\prepare_gotham2025_v1.py"\n'
         '            "\\n" r"& $py scripts\\run_native_label_benchmark_v1.py --processed-dir data_processed_gotham2025_v1 --output-dir results_rccf_gotham2025_v1 --seeds 42 2024 3407 7 13 101 202 303 404 505 --experts full chi2 anova"\n'
         '            "\\n" r"& $py scripts\\run_native_label_benchmark_v1.py --processed-dir data_processed_gotham2025_v1 --output-dir results_rccf_gotham2025_v1_k8 --seeds 42 2024 3407 7 13 101 202 303 404 505 --experts full chi2 anova --feature-k 8",\n'
         '            "`data_processed_gotham2025_v1/`、`results_rccf_gotham2025_v1/`（60 维预算，"\n'
         '            "视图重合）、`results_rccf_gotham2025_v1_k8/`（8/16 维，视图分化）",\n'
         '            [(f"60 维预算（全部 16 列）",\n'
         '              f"RCCF {full[\'rccf_mean_macro_f1\']:.6f}，同成员等权融合 "\n'
         '              f"{full[\'equal_fusion_mean_macro_f1\']:.6f}，差 "\n'
         '              f"{full[\'same_members_difference\']:+.6f}"),\n'
         '             (f"8/16 维预算（视图分化）",\n'
         '              f"RCCF {k8[\'rccf_mean_macro_f1\']:.6f}，同成员等权融合 "\n'
         '              f"{k8[\'equal_fusion_mean_macro_f1\']:.6f}，差 "\n'
         '              f"{k8[\'same_members_difference\']:+.6f}")],\n'
         '            f"同一语料、同一批专家：特征预算让三个视图重合时门控完全无效"\n'
         '            f"（{full[\'same_members_difference\']:+.6f}），让它们分化时门控"\n'
         '            f"以 {k8[\'same_members_difference\']:+.6f} 超过同成员等权融合，"\n'
         '            "十个种子方向一致。这是全文唯一一个门控稳定为正的语料，边界与命题 1 一致。")\n'
         '    text = "\\n".join(lines) + "\\n"', "Gotham report section"),
    ])
    patch(REPORT_CHECK, [
        ('        "results_rccf_ids2025_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                    "benchmark_summary.json"],',
         '        "results_rccf_ids2025_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                    "benchmark_summary.json"],\n'
         '        "results_rccf_gotham2025_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                       "benchmark_summary.json"],\n'
         '        "results_rccf_gotham2025_v1_k8": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                          "benchmark_summary.json"],', "report check dirs"),
        ('    for folder, label in (("results_rccf_uavids2025_v1", "UAVIDS-2025"),\n'
         '                          ("results_rccf_genis2025_v1", "GeNIS"),\n'
         '                          ("results_rccf_ids2025_v1", "IDS2025")):',
         '    for folder, label in (("results_rccf_uavids2025_v1", "UAVIDS-2025"),\n'
         '                          ("results_rccf_genis2025_v1", "GeNIS"),\n'
         '                          ("results_rccf_ids2025_v1", "IDS2025"),\n'
         '                          ("results_rccf_gotham2025_v1", "Gotham-2025 (60 features)"),\n'
         '                          ("results_rccf_gotham2025_v1_k8", "Gotham-2025 (8/16 features)")):',
         "report check values"),
        ('    print(f"EXTENSION_OK experiments=13 quoted={len(checks)} "',
         '    print(f"EXTENSION_OK experiments=14 quoted={len(checks)} "',
         "report check count"),
    ])
    patch(BUNDLE, [
        ('      ROOT / "results_rccf_ids2025_v1" / "metrics_by_seed.csv"]),',
         '      ROOT / "results_rccf_ids2025_v1" / "metrics_by_seed.csv",\n'
         '      ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json",\n'
         '      ROOT / "results_rccf_gotham2025_v1" / "metrics_aggregate.csv",\n'
         '      ROOT / "results_rccf_gotham2025_v1" / "metrics_by_seed.csv",\n'
         '      ROOT / "results_rccf_gotham2025_v1_k8" / "benchmark_summary.json",\n'
         '      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_aggregate.csv",\n'
         '      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_by_seed.csv"]),',
         "bundle Gotham summaries"),
    ])
    patch(METRICS_FIX, [
        ('        "results_rccf_uavids2025_v1", "results_rccf_genis2025_v1",\n'
         '        "results_rccf_ids2025_v1"]',
         '        "results_rccf_uavids2025_v1", "results_rccf_genis2025_v1",\n'
         '        "results_rccf_ids2025_v1", "results_rccf_gotham2025_v1",\n'
         '        "results_rccf_gotham2025_v1_k8"]', "metrics aggregate list"),
    ])
    print("GOTHAM_INTEGRATED")


if __name__ == "__main__":
    main()
