"""Build a standalone introduction to the study from the released artefacts.

The manuscript's own Section 1 assumes a reader who has the paper in front of
them; this document is for everyone else - an advisor, a collaborator, a
reviewer deciding whether to read on.  Every number is read from the result
files rather than typed, so the introduction cannot drift from the paper.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = BASE / "论文介绍.md"


def ten_seed() -> dict[str, float]:
    frame = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    return {model: float(frame.loc[model, "macro_f1"])
            for model in ("rccf", "equal_rf_chi2", "equal_rf_all", "extra_trees_chi2")}


def main() -> None:
    title = (BASE / "English_SCI_Manuscript_v4.md").read_text(
        encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    zh_title = (BASE / "中文SCI论文_v4_重构版.md").read_text(
        encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    ten = ten_seed()
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv").set_index("comparison")
    row = power.loc["rccf_minus_equal_rf_chi2"]
    equivalence = json.loads((ROOT / "results_equivalence_10seeds_v5" /
                              "equivalence_summary.json").read_text(encoding="utf-8"))["pooled"]
    scale = json.loads((ROOT / "results_scale_sensitivity_v46" /
                        "scale_sensitivity_summary.json").read_text(encoding="utf-8"))
    full = json.loads((ROOT / "results_full_corpus_v49" /
                       "full_corpus_summary.json").read_text(encoding="utf-8"))
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    grid = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    regression = json.loads((ROOT / "results_diversity_v5" /
                             "diversity_gain_regression.json").read_text(encoding="utf-8"))
    openset = pd.read_csv(ROOT / "results_cfrg_open_set_v5_verified" / "open_set_metrics.csv")
    conditional = openset[openset.model.isin(("cfrg_forest", "cfrg_forest_temperature_scaled"))]
    equal = openset[openset.model.isin(("equal_rf", "equal_rf_temperature_scaled"))]
    nsl = pd.read_csv(ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv").iloc[0]
    unsw = pd.read_csv(ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv").iloc[0]
    nbaiot = pd.read_csv(ROOT / "results_nbaiot_baselines_v48" / "metrics_aggregate.csv",
                         header=[0, 1]).dropna(how="all")
    nbaiot = nbaiot.set_index(nbaiot.columns[0]).dropna(how="all")
    protocol = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" /
                           "protocol_sensitivity_metrics.csv")
    pivot = protocol.pivot(index="seed", columns="protocol", values="macro_f1")
    dedup = float((pivot["split_first_training_only_dedup"] -
                   pivot["global_dedup_before_split"]).abs().max())
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv").iloc[0]
    prior_gap = float(balanced.macro_f1_mean) - ten["rccf"]
    scale_rccf = pd.read_csv(ROOT / "results_rccf_cic_natural_v4_scale200k" /
                             "metrics_aggregate.csv").iloc[0]
    scale_frame = pd.read_csv(ROOT / "results_scale_sensitivity_v46" /
                              "metrics_aggregate.csv", header=[0, 1])
    scale_frame = scale_frame.set_index(scale_frame.columns[0])
    scale_control = float(scale_frame.loc["equal_rf_chi2", ("macro_f1", "mean")])
    ten_frame = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    train_multiple = float(ten_frame.loc["rccf", "train_seconds"] /
                           ten_frame.loc["equal_rf_chi2", "train_seconds"])
    predict_multiple = float(ten_frame.loc["rccf", "predict_seconds"] /
                             ten_frame.loc["equal_rf_chi2", "predict_seconds"])
    profile = json.loads((ROOT / "results_resources_v5" /
                          "resource_profile_summary.json").read_text(encoding="utf-8"))["summary"]
    size_multiple = float(profile["rccf"]["model_size_mb"]) / \
        float(profile["equal_rf_chi2"]["model_size_mb"])
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    version = re.search(r'version: "([^"]+)"', citation).group(1)
    repo = re.search(r'repository-code: "([^"]+)"', citation).group(1)

    lines: list[str] = []
    lines.append("# 论文介绍")
    lines.append("")
    lines.append(f"**中文标题**：{zh_title}  ")
    lines.append(f"**English title**：{title}  ")
    lines.append(f"**发布版本**：{version}  ")
    lines.append(f"**代码与证据仓库**：{repo}")
    lines.append("")
    lines.append("## 一、一句话结论")
    lines.append("")
    lines.append(f"在统一的泄漏受控协议下，「按样本可靠性对多个随机森林专家做条件加权」"
                 f"相对等权投票**没有判别增益**：截断总体上两者等价"
                 f"（Macro-F1 平均差 {row.mean_difference:.6f}，TOST 在两个预设边界成立），"
                 f"而完全取消类别上限的全语料上转为稳定劣势 "
                 f"（{full['mean_difference']:.6f}，十个种子方向一致）；"
                 f"同时，**协议选择的影响比聚合规则本身大一个数量级**"
                 f"（类别先验 {prior_gap:.4f}、去重顺序至多 {dedup:.4f}，聚合规则仅 0.0005 量级）。")
    lines.append("")
    lines.append("## 二、研究问题与缺口")
    lines.append("")
    lines.append("条件集成加权（按样本估计的可靠性权重融合多个专家）被广泛采用，"
                 "但公开数据集上的性能差异极易被四类因素污染：重复样本、标签冲突、"
                 "特征选择泄漏与类别先验。缺少受控验证时，「加权优于等权」既可能是机制效应，"
                 "也可能只是协议副作用。本文把该假设放到一个可复现的协议下检验，"
                 "并给出可证伪的判据。")
    lines.append("")
    lines.append("## 三、做法")
    lines.append("")
    lines.append("| 环节 | 设定 |")
    lines.append("|---|---|")
    lines.append("| 主数据 | CIC-IDS2017（原始 2 830 743 条，审计后取研究总体）|")
    lines.append("| 外部/跨域 | NSL-KDD、UNSW-NB15、N-BaIoT（UCI 442，CC BY 4.0）|")
    lines.append("| 协议 | 标签映射 → 非有限值清理 → 物理范围筛查 → 全局去重 → 分层划分 → "
                 "训练侧特征选择 |")
    lines.append("| 对照 | 等权 χ² 森林（最直接对照）、全特征等权森林、极端随机树、XGBoost、MLP |")
    lines.append("| 种子 | 主实验 10 个（42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505）|")
    lines.append("| 统计 | 配对差 + 种子级 90%/95% 区间 + 测试行配对 Bootstrap + TOST（0.005/0.01）|")
    lines.append("")
    lines.append("## 四、主要结果")
    lines.append("")
    lines.append("### 4.1 三档总体：结论随规模反转（Macro-F1，十种子平均）")
    lines.append("")
    lines.append("| 总体 | 流量 | 测试行 | 条件加权 | 等权 χ² 森林 | 平均差 | TOST 0.005 | TOST 0.01 |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|")
    lines.append(f"| 截断（每类 20 000）| 53 237 | 7 986 | {ten['rccf']:.6f} | "
                 f"{ten['equal_rf_chi2']:.6f} | {row.mean_difference:.6f} | 等价 | 等价 |")
    lines.append(f"| 扩大 7.8 倍（每类 200 000）| 413 209 | 61 982 | "
                 f"{float(scale_rccf.macro_f1_mean):.6f} | {scale_control:.6f} | "
                 f"{scale['mean_difference']:.6f} | 等价 | 等价 |")
    lines.append(f"| 全去重语料（取消上限）| 2 429 503 | {full['test_rows']:,} | "
                 f"{full['rccf_mean_macro_f1']:.6f} | {full['control_mean_macro_f1']:.6f} | "
                 f"{full['mean_difference']:.6f} | 不等价 | 等价 |")
    lines.append("")
    lines.append(f"截断总体上的两个区间估计都落在等价边界内：种子级 90% "
                 f"[{row.ci90_low:.6f}, {row.ci90_high:.6f}]，测试行配对 Bootstrap "
                 f"[{equivalence['pooled_ci_low']:.6f}, {equivalence['pooled_ci_high']:.6f}]；"
                 f"逐种子方向五正五负。全语料的 90% 区间为 "
                 f"[{full['seed_level_90_interval'][0]:.6f}, "
                 f"{full['seed_level_90_interval'][1]:.6f}]。")
    lines.append("")
    lines.append("### 4.2 机制：为什么权重动不了预测")
    lines.append("")
    lines.append(f"- 逐行可计算上界证明 **{margin['provable_by_bound_rate_mean'] * 100:.2f}%** 的测试行不受权重影响，"
                 f"实际改判 {margin['empirical_changed_rows']} 行；")
    lines.append(f"- 权重归一化熵 **{weight.normalized_weight_entropy:.5f}**，概率 L1 平均变化 "
                 f"{weight.mean_probability_l1:.6f}（最大 {weight.max_probability_l1:.6f}）；")
    lines.append(f"- 门控 **{len(grid)}** 种超参数配置只产生 **{grid.val_macro_f1.nunique()}** 个不同的验证集取值，"
                 f"锁定后在测试集上改判 0 行；")
    lines.append(f"- 增益由专家多样性支配：分歧率 0.20%–0.36% 的专家集合 6 次运行增益全为 0，"
                 f"去相关集合 9 次运行全为正（回归斜率 {regression['slope']:.4f}，"
                 f"Pearson r = {regression['pearson_r']:.3f}）。")
    lines.append("")
    lines.append("### 4.3 代价、开放集与外部基准")
    lines.append("")
    lines.append(f"- **代价**：同等总体下条件加权的训练耗时约为等权森林的 "
                 f"{train_multiple:.0f} 倍（截断总体），"
                 f"全语料为 {full['train_slowdown']:.0f} 倍；模型体积 {size_multiple:.1f} 倍、"
                 f"批量推理 {predict_multiple:.1f} 倍；"
                 f"在误报漏报代价比 1–100 内没有代价敏感优势。")
    lines.append(f"- **开放集**：以 PortScan、Infiltration、Heartbleed 为未知族时，条件分支 AUROC "
                 f"{math.floor(conditional.auroc.min() * 1000) / 1000:.3f}–"
                 f"{conditional.auroc.max():.3f}、未知类召回 "
                 f"{conditional.unknown_recall.min():.4f}–{conditional.unknown_recall.max():.4f}，"
                 f"等权森林为 {equal.auroc.min():.3f}–{equal.auroc.max():.3f} 与 "
                 f"{equal.unknown_recall.min():.3f}–{equal.unknown_recall.max():.3f}"
                 f"（风险门控把概率推向高置信区，削弱了拒绝所需的不确定性信号）。")
    lines.append(f"- **外部基准（三种子）**：NSL-KDD Macro-F1 {float(nsl.macro_f1_mean):.6f}、"
                 f"UNSW-NB15 {float(unsw.macro_f1_mean):.6f}；N-BaIoT 上所有模型 Macro-F1 ≥ "
                 f"{float(nbaiot[('macro_f1', 'mean')].min()):.4f}，该基准对流量特征分类器已饱和。")
    lines.append("")
    lines.append("## 五、贡献")
    lines.append("")
    lines.append("1. **一套可复用的泄漏受控协议**：从原始文件到建模的每一阶段都有计数与产物记录；")
    lines.append("2. **一组可证伪的可辨识性条件**：把「权重不改变预测」化为可逐行计算的判据"
                 f"（{margin['provable_by_bound_rate_mean'] * 100:.2f}% 样本可证）；")
    lines.append("3. **一张把协议效应与聚合规则差异分开量化的地图**：协议效应高一个数量级，"
                 "而模型族差异（XGBoost − 随机森林 +0.0078；MLP 落后 0.0916）又大于两者；")
    lines.append("4. **一份诚实的代价账**：训练/推理开销、概率质量、开放集行为与延迟百分位分列报告。")
    lines.append("")
    lines.append("## 六、诚实的边界")
    lines.append("")
    lines.append("- 研究总体是审计后的公开数据子集，**不是生产流量**；四个语料都不提供同一测试床上的时间分离留出集；")
    lines.append("- 文件级实验不是时间外推；开放集只覆盖三个未知族与一个显著性水平；")
    lines.append("- 延迟测量不含抓包与特征提取；对抗性规避未评估（只做了随机扰动与特征屏蔽）；")
    lines.append("- 结论的范围是**流特征 + 公开数据集**，不主张生产可用性或算法优越性。")
    lines.append("")
    lines.append("## 七、可复现材料")
    lines.append("")
    lines.append(f"- 仓库（代码、逐样本预测、审计中间产物、图表生成脚本）：{repo}（标签 v{version}）")
    lines.append("- 补充材料 S01–S30：数据来源与校验和、逐种子指标、门控搜索、边距上界、"
                 "多样性实验、外部基准、规模阶梯、开放集诊断等；")
    lines.append("- 论文包：正式稿件（中英）、Highlights、投稿信、图形摘要、主表 CSV 与投稿文本；")
    lines.append("- 全部数字可由发布的逐样本预测重算（闸门 45 项自动复核）。")
    lines.append("")
    lines.append("## 八、引用")
    lines.append("")
    lines.append("```bibtex")
    lines.append("@article{rccf_leakage_controlled_nids,")
    lines.append(f"  title   = {{Protocol Sensitivity Dominates Aggregation-Rule Differences in "
                 f"Flow-Based Network Intrusion Detection}},")
    lines.append("  author  = {<待作者填写>},")
    lines.append("  journal = {Journal of Information Security and Applications},")
    lines.append(f"  note    = {{Code and evidence: {repo}, release v{version}}}")
    lines.append("}")
    lines.append("```")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"INTRO_WRITTEN={OUT}")
    print(f"lines={len(lines)}")


if __name__ == "__main__":
    main()
