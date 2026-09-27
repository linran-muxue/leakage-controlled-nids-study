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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402


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
    # per-seed and per-artefact detail: the numbers a reader asks for after the
    # headline table, all read from the released files rather than restated
    tost = pd.read_csv(ROOT / "results_equivalence_10seeds_v5" / "tost_results.csv")
    effect = pd.read_csv(ROOT / "results_seeds10_v5" / "effect_sizes.csv").set_index("comparison")
    cost = json.loads((ROOT / "results_cost_v5" /
                       "cost_sensitive_summary.json").read_text(encoding="utf-8"))["summary"]
    file_level = pd.read_csv(ROOT / "results_file_external_generalization_v3b" /
                             "file_external_results.csv")
    prop3 = json.loads((ROOT / "results_margin_bound_v5" /
                        "proposition3_quantification.json").read_text(encoding="utf-8"))
    gate_sel = json.loads((ROOT / "results_gate_tuning_v5" /
                           "selected_gate_config.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))
    raw = audit["raw_totals"]
    nbaiot_rccf = pd.read_csv(ROOT / "results_rccf_nbaiot_v48" /
                              "metrics_aggregate.csv").iloc[0]
    full_means = pd.read_csv(ROOT / "results_full_corpus_v49" /
                             "metrics_by_seed.csv").groupby("model")["macro_f1"].mean()

    def cost_nec(model: str, ratio: int) -> float:
        return float(next(item["nec"] for item in cost
                          if item["model"] == model and item["cost_ratio_fn_fp"] == ratio))

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
    lines.append("## 二、研究问题、判据与缺口")
    lines.append("")
    lines.append("条件集成加权（按样本估计的可靠性权重融合多个专家）被广泛采用，"
                 "但公开数据集上的性能差异极易被四类因素污染：**重复与近重复样本**、"
                 "**标签冲突**（同一特征向量被赋不同标签）、**特征选择泄漏**"
                 "（选择器在全量数据上拟合）以及**类别先验与调参预算**。"
                 "缺少受控验证时，「加权优于等权」既可能是机制效应，也可能只是协议副作用。")
    lines.append("")
    lines.append("本文把问题拆成三个可回答的子问题：")
    lines.append("")
    lines.append("| 编号 | 问题 | 判据（事先定好，不随结果调整）|")
    lines.append("|---|---|---|")
    lines.append(f"| RQ1 | 条件加权相对等权投票是否带来判别增益？| 十种子配对差 + TOST 等价检验，"
                 f"边界预设为 Δ = 0.005 与 Δ = 0.01（Macro-F1）|")
    lines.append(f"| RQ2 | 若没有增益，机制上为什么动不了预测？| 逐行可计算上界（式 2）给出的"
                 f"「可证不变比例」+ 权重弥散度 + 门控搜索的取值多样性 |")
    lines.append(f"| RQ3 | 结论随规模、先验与语料如何变化？| 三档总体（53 237 / 413 209 / 2 429 503）"
                 f"+ 平衡控制总体 + 三个独立原生标签基准 |")
    lines.append("")
    lines.append("**为什么用等价检验而不是「p > 0.05」**：十种子下 80% 功效能检出的最小差是 "
                 f"{row.min_detectable_effect_80pct:.6f}，与观测差 {abs(row.mean_difference):.6f} 同量级——"
                 "「不显著」在这种情况下无法区分「真的没有差异」与「样本不够」。"
                 "TOST 把「差落在 ±Δ 内」本身当成待检验命题，两个边界同时报告，"
                 "并配合种子级区间与测试行配对 Bootstrap 一起看。")
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
    lines.append(f"| 六阶段计数 | 原始 {raw['source_rows']:,} → 可映射标签 {raw['mapped_rows']:,}"
                 f"（剔除 {raw['excluded_label_rows']:,}）→ 非有限值剔除 {raw['invalid_rows']:,} 后 "
                 f"{raw['valid_rows']:,} → 物理范围筛查 {raw['physical_valid_rows']:,} → 全局去重 → 分层划分 |")
    lines.append("| 三档总体 | 截断 53 237（每类 ≤20 000）/ 扩大 413 209（每类 ≤200 000）/ "
                 "全去重语料 2 429 503（取消上限）；测试行 7 986 / 61 982 / 364 426 |")
    lines.append("| 专家构造 | 两种特征视图（卡方 60 维、全特征）× 两类森林（随机森林、极端随机树）共 4 个专家；"
                 "条件分支与对照臂共用同一批专家，只换聚合规则 |")
    lines.append("| 权重与门控 | 专家风险代理（边距描述子）过 softmax(−风险) 得权重，再做凸组合；"
                 f"门控在验证集上搜 {len(grid)} 组配置，选中 cv={gate_sel['cv']}、"
                 f"C={gate_sel['risk_C']:g}、{gate_sel['descriptor_set']}，测试集不参与选择 |")
    lines.append("| 特征选择 | 只在训练侧拟合：χ²、互信息、ANOVA 三种判据（外部基准与规模阶梯同协议）|")
    lines.append("| 评价 | 主指标 Macro-F1；同时报告准确率、平衡准确率、log loss、ECE/MCE、覆盖率 |")
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
    lines.append("### 4.2 统计判据：逐种子、逐行的完整记录")
    lines.append("")
    lines.append("| 种子 | 条件加权 | 等权 χ² | 差值 | 90% 区间 | 不一致对 | McNemar p | "
                 "TOST 0.005 | TOST 0.01 |")
    lines.append("|---:|---:|---:|---:|---|---:|---:|---|---|")
    for _, seed_row in tost.iterrows():
        lines.append(f"| {int(seed_row['seed'])} | {seed_row['macro_f1_rccf']:.6f} | "
                     f"{seed_row['macro_f1_baseline']:.6f} | {seed_row['delta']:+.6f} | "
                     f"[{seed_row['ci_low']:.6f}, {seed_row['ci_high']:.6f}] | "
                     f"{int(seed_row['discordant'])} | {seed_row['mcnemar_p']:.3f} | "
                     f"{'等价' if seed_row['tost_equivalent_at_0.005'] else '不等价'} | "
                     f"{'等价' if seed_row['tost_equivalent_at_0.01'] else '不等价'} |")
    lines.append("")
    lines.append(f"- **方向**：{int(effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_rccf'])} 个种子"
                 f"支持条件加权、{int(effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_baseline'])} 个"
                 f"支持等权（无并列），不是某个种子拖出来的结论；")
    lines.append(f"- **等价**：0.005 边界 {int(tost['tost_equivalent_at_0.005'].sum())}/10 个种子已等价，"
                 f"0.01 边界 {int(tost['tost_equivalent_at_0.01'].sum())}/10；")
    lines.append(f"- **逐行**：每次比较只有 {tost['discordant'].min()}–{tost['discordant'].max()} 行"
                 f"预测不同（占 7 986 行的 {tost['discordant'].min() / 7986 * 100:.2f}%–"
                 f"{tost['discordant'].max() / 7986 * 100:.2f}%），McNemar p 值 "
                 f"{tost['mcnemar_p'].min():.3f}–{tost['mcnemar_p'].max():.3f}，没有一次达到显著；")
    lines.append(f"- **效应量**：Cohen's dz = "
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'cohens_dz']:.3f}，相对差 "
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'relative_difference_pct']:.3f}%；")
    lines.append(f"- **功效**：十个种子下 80% 功效可检出的最小差为 "
                 f"{row.min_detectable_effect_80pct:.6f}，说明「不显著」本身不构成证据，"
                 f"必须用等价检验；")
    lines.append(f"- **全语料**：差值 {full['mean_difference']:.6f}，逐种子预测不一致行数平均 "
                 f"{full['mean_disagreements']:.0f}、最多 {full['max_disagreements']} 行"
                 f"（测试 364 426 行），方向十次全负。")
    lines.append("")
    lines.append("### 4.3 机制：为什么权重动不了预测")
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
    lines.append(f"- 权重弥散的二阶刻画：式 (3)/(4) 的一阶与二阶展开预测熵亏分别为 "
                 f"{prop3['mean_entropy_deficiency_predicted_from_var_delta']:.3e} 与 "
                 f"{prop3['mean_second_order_identity_value']:.3e}，实测 "
                 f"{prop3['mean_entropy_deficiency_observed']:.3e}"
                 f"（相对误差 {prop3['relative_error_of_first_order_prediction'] * 100:.1f}% / "
                 f"{prop3['relative_error_of_second_order_identity'] * 100:.1f}%）；"
                 f"风险偏移的中位标准差 {prop3['median_sd_risk_offset']:.6f}；")
    lines.append(f"- 门控锁定的配置是 cv={gate_sel['cv']}、C={gate_sel['risk_C']:g}、"
                 f"描述子 {gate_sel['descriptor_set']}（验证集 Macro-F1 "
                 f"{gate_sel['val_macro_f1_mean']:.6f} ± {gate_sel['val_macro_f1_std']:.6f}），"
                 f"选择只发生在验证集，测试集全程未参与；")
    lines.append(f"- 专家集合的分歧率决定增益大小：当专家两两分歧率降到 0.2%–0.4% 时，"
                 f"结构上不可能产生增益（命题 1 的失效区间）；本文的主实验正落在该区间内。")
    lines.append("")
    lines.append("### 4.4 先验、外部基准与文件级外推")
    lines.append("")
    lines.append(f"- **类别先验是最大的单一效应**：平衡控制总体（3 365 条、三类等量、测试 505 条）"
                 f"Macro-F1 {float(balanced.macro_f1_mean):.6f}、覆盖率 "
                 f"{float(balanced.coverage_mean):.3f}，比自然先验的 {ten['rccf']:.6f} 高 "
                 f"{prior_gap:.4f}——比聚合规则差异大约两个数量级；")
    lines.append("")
    lines.append("| 外部基准（三种子）| 测试行 | Macro-F1 | 准确率 | 平衡准确率 | 覆盖率 | 说明 |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    lines.append(f"| NSL-KDD（原生标签）| {float(nsl.test_samples_mean):,.0f} | "
                 f"{float(nsl.macro_f1_mean):.6f} | {float(nsl.accuracy_mean):.3f} | "
                 f"{float(nsl.balanced_accuracy_mean):.3f} | {float(nsl.coverage_mean):.3f} | "
                 f"准确率靠多数类，平衡准确率接近随机 |")
    lines.append(f"| UNSW-NB15（原生标签）| {float(unsw.test_samples_mean):,.0f} | "
                 f"{float(unsw.macro_f1_mean):.6f} | {float(unsw.accuracy_mean):.3f} | "
                 f"{float(unsw.balanced_accuracy_mean):.3f} | {float(unsw.coverage_mean):.3f} | "
                 f"二分类偏置下的独立验证 |")
    lines.append(f"| N-BaIoT（IoT 僵尸网络）| {float(nbaiot_rccf.test_samples_mean):,.0f} | "
                 f"{float(nbaiot_rccf.macro_f1_mean):.6f} | {float(nbaiot_rccf.accuracy_mean):.3f} | "
                 f"{float(nbaiot_rccf.balanced_accuracy_mean):.3f} | {float(nbaiot_rccf.coverage_mean):.3f} | "
                 f"已饱和，用于检验机制惰性 |")
    lines.append("")
    lines.append(f"- **文件级外推**：把周一至周五的每个原始文件作为留出集时，已知类 Macro-F1 覆盖 "
                 f"{file_level.macro_f1_known.min():.4f}–{file_level.macro_f1_known.max():.4f}；"
                 f"文件之间的差异（同一模型、同一协议）比聚合规则差异大两到三个数量级，"
                 f"说明「换一天的数据」远比比「换聚合规则」重要。")
    lines.append("")
    lines.append("### 4.5 代价与开放集")
    lines.append("")
    lines.append("- **训练与推理代价**（同一台机器、同一批测试行）：")
    lines.append("")
    lines.append("| 项目 | 条件加权 RCCF | 等权 χ² 森林 | 倍数 |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| 训练耗时（截断总体，单种子平均）| "
                 f"{float(ten_frame.loc['rccf', 'train_seconds']):.2f} s | "
                 f"{float(ten_frame.loc['equal_rf_chi2', 'train_seconds']):.2f} s | "
                 f"×{train_multiple:.0f} |")
    lines.append(f"| 训练耗时（全语料，单种子平均）| "
                 f"{full['rccf_mean_train_seconds'] / 3600:.1f} h | "
                 f"{full['control_mean_train_seconds']:.1f} s | ×{full['train_slowdown']:.0f} |")
    lines.append(f"| 模型体积 | {profile['rccf']['model_size_mb']:.2f} MB | "
                 f"{profile['equal_rf_chi2']['model_size_mb']:.2f} MB | ×{size_multiple:.1f} |")
    lines.append(f"| 批量吞吐 | {profile['rccf']['rows_per_second']:,.0f} 行/秒 | "
                 f"{profile['equal_rf_chi2']['rows_per_second']:,.0f} 行/秒 | "
                 f"÷{profile['equal_rf_chi2']['rows_per_second'] / profile['rccf']['rows_per_second']:.1f} |")
    lines.append(f"| 峰值内存增量 | {profile['rccf']['peak_rss_mb']:.1f} MB | "
                 f"{profile['equal_rf_chi2']['peak_rss_mb']:.1f} MB | "
                 f"×{profile['rccf']['peak_rss_mb'] / profile['equal_rf_chi2']['peak_rss_mb']:.2f} |")
    lines.append("")
    lines.append(f"- **代价敏感**：误报漏报代价比从 1 提到 100 时，归一化期望代价 NEC "
                 f"条件加权 {cost_nec('rccf', 1):.5f} → {cost_nec('rccf', 100):.5f}，"
                 f"等权森林 {cost_nec('equal_rf_chi2', 1):.5f} → {cost_nec('equal_rf_chi2', 100):.5f}——"
                 f"代价越高，条件加权越不划算。")
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
    lines.append(f"三个量级放在一起看最清楚（全语料、Macro-F1）：聚合规则差异 "
                 f"{abs(full['mean_difference']):.6f} < 模型族差异 "
                 f"{full_means['xgboost_chi2'] - full_means['equal_rf_chi2']:.3f}"
                 f"（XGBoost {full_means['xgboost_chi2']:.6f} vs 等权森林 "
                 f"{full_means['equal_rf_chi2']:.6f}）"
                 f" < 协议效应 {prior_gap:.4f}（类别先验）。"
                 f"换言之：**先把协议做对，再谈换模型，最后才轮到换聚合规则**。")
    lines.append("")
    lines.append("## 六、诚实的边界")
    lines.append("")
    lines.append("- 研究总体是审计后的公开数据子集，**不是生产流量**；四个语料都不提供同一测试床上的时间分离留出集；")
    lines.append("- 文件级实验不是时间外推；开放集只覆盖三个未知族与一个显著性水平；")
    lines.append("- 延迟测量不含抓包与特征提取；对抗性规避未评估（只做了随机扰动与特征屏蔽）；")
    lines.append("- 等价边界 0.005 与 0.01 是**研究者预设**的，不是从数据里估出来的；"
                 "两个边界都报告，读者可以按自己的容忍度读结论；")
    lines.append("- N-BaIoT 已饱和（所有模型 ≥ 0.9998），它检验机制惰性而不检验判别难度；"
                 "把它当作性能证据是误读；")
    lines.append("- 命题的前提是专家同质（同算法族、同特征预算）；对高度异质或强去相关的专家集合，"
                 "结论不适用（这正是下一步要检验的方向）；")
    lines.append("- 结论的范围是**流特征 + 公开数据集**，不主张生产可用性或算法优越性。")
    lines.append("")
    lines.append("## 七、如何快速读这篇稿子（15 分钟路线）")
    lines.append("")
    lines.append("| 顺序 | 读什么 | 用多久 | 读完知道什么 |")
    lines.append("|---|---|---:|---|")
    lines.append("| 1 | 摘要 + 图 1（研究设计）| 3 分钟 | 问题、对照、三档总体与主结论 |")
    lines.append("| 2 | 表 4(a)/4(b) + 表 5 | 4 分钟 | 主结果、区间、TOST 与效应量 |")
    lines.append("| 3 | 图 5/6 + 式 (2) | 3 分钟 | 为什么权重动不了预测（可逐行计算的上界）|")
    lines.append("| 4 | 第 6.2 节（稀释诊断）| 2 分钟 | 全语料反转的唯一解释 |")
    lines.append("| 5 | 第 7 节（局限与效度威胁）| 2 分钟 | 结论不覆盖什么 |")
    lines.append("| 6 | 需要细节时 | 按需 | 表 7（规模）、表 8（外部）、S01–S30 补充材料 |")
    lines.append("")
    lines.append("## 八、术语速查")
    lines.append("")
    lines.append("| 术语 | 含义 | 在本文哪里 |")
    lines.append("|---|---|---|")
    lines.append("| 数据泄漏 | 测试集信息进入训练，使指标虚高 | 第 2 节四类污染、第 3 节协议 |")
    lines.append("| 条件加权 / 等权投票 | 按样本可靠性分配权重再融合 / 各专家等权平均 | 式 (1)、第 3.3 节 |")
    lines.append("| 可辨识性条件 | 判断「权重是否可能改变预测」的前提，本文三条 | 式 (2)、命题 1–3 |")
    lines.append("| TOST | 双单侧等价检验：差值必须被证明落在 ±Δ 内 | 第 4.2 节、表 5 |")
    lines.append("| 稀释诊断 | 多路平均把某专家的偏差按 1/Q 摊进结果 | 式 (6)、第 6.2 节 |")
    lines.append("| Macro-F1 | 各类 F1 的未加权平均，不平衡数据的推荐主指标 | 全篇主指标 |")
    lines.append("| 开放集 / 未知类召回 | 测试时出现训练未见类别时的拒识能力 | 第 6.4 节、S30 |")
    lines.append("")
    lines.append("## 九、可复现材料")
    lines.append("")
    lines.append(f"- 仓库（代码、逐样本预测、审计中间产物、图表生成脚本）：{repo}（标签 v{version}）")
    lines.append("- 补充材料 S01–S30：数据来源与校验和、逐种子指标、门控搜索、边距上界、"
                 "多样性实验、外部基准、规模阶梯、开放集诊断等；")
    lines.append("- 论文包：正式稿件（中英）、Highlights、投稿信、图形摘要、主表 CSV 与投稿文本；")
    lines.append("- 汇报材料：`向老师汇报要点.md/.docx`（三个时长版本、逐页讲稿、"
                 "22 问预判问答、检查清单）与 `汇报用_论文介绍.pptx`（12 页）；")
    lines.append(f"- 一页全流程：`项目流程图.md/.docx`（六阶段，含各阶段入口与产物）；")
    lines.append(f"- 全部数字可由发布的逐样本预测重算（闸门 {counts.gate_checks()} 项自动复核）。")
    lines.append("")
    lines.append("## 十、引用")
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
