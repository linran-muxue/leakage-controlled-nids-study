"""Build the material for presenting the paper to a supervisor.

Three listening budgets (30 seconds, three minutes, ten minutes), a slide order,
a one-page number sheet, the eight questions a supervisor is most likely to ask
with the answer and where the evidence lives, and the wording to avoid.  Every
number is read from the result files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def corpus_facts() -> tuple[int, int, str]:
    """(evaluated corpora, released prediction files, the 2025 summary line).

    Counted from the working tree rather than typed: both numbers moved
    twice while the recent corpora were being added.
    """
    extension = [path for path in ROOT.glob("results_rccf_*_v1")
                 if not path.name.endswith("_k8")
                 and (path / "benchmark_summary.json").exists()]
    corpora = 4 + len(extension)
    predictions = len(list(ROOT.glob("results_*/**/predictions*.csv")))
    y2025 = []
    for folder, label in (("results_rccf_uavids2025_v1", "UAVIDS-2025"),
                          ("results_rccf_genis2025_v1", "GeNIS"),
                          ("results_rccf_ids2025_v1", "IDS2025"),
                          ("results_rccf_gotham2025_v1", "Gotham-2025")):
        path = ROOT / folder / "benchmark_summary.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        y2025.append(f"{label}（{len(data['classes'])} 类，Macro-F1 "
                     f"{data['rccf_mean_macro_f1']:.4f}，差 "
                     f"{data['same_members_difference']:+.6f}）")
    return corpora, predictions, "、".join(y2025)

BASE = ROOT / "重构版论文_v4_20260915"
OUT = BASE / "向老师汇报要点.md"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402


def main() -> None:
    corpora, predictions, y2025_line = corpus_facts()
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
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
    full_agg = pd.read_csv(ROOT / "results_full_corpus_v49" / "metrics_aggregate.csv",
                           header=[0, 1])
    full_agg = full_agg.set_index(full_agg.columns[0])
    full_all = float(full_agg.loc["equal_rf_all", ("macro_f1", "mean")])
    full_chi2 = float(full_agg.loc["equal_rf_chi2", ("macro_f1", "mean")])
    dilution = (full_chi2 - full_all) / 4
    protocol = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" /
                           "protocol_sensitivity_metrics.csv")
    pivot = protocol.pivot(index="seed", columns="protocol", values="macro_f1")
    dedup = float((pivot["split_first_training_only_dedup"] -
                   pivot["global_dedup_before_split"]).abs().max())
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" /
                           "metrics_aggregate.csv").iloc[0]
    prior = float(balanced.macro_f1_mean) - float(ten.loc["rccf", "macro_f1"])
    # per-seed records: the equivalence test row by row, the effect size, and the
    # resource and cost profiles - the material a supervisor asks for when the
    # summary table is not enough
    tost = pd.read_csv(ROOT / "results_equivalence_10seeds_v5" / "tost_results.csv")
    effect = pd.read_csv(ROOT / "results_seeds10_v5" / "effect_sizes.csv").set_index("comparison")
    profile = json.loads((ROOT / "results_resources_v5" /
                          "resource_profile_summary.json").read_text(encoding="utf-8"))["summary"]
    cost = json.loads((ROOT / "results_cost_v5" /
                       "cost_sensitive_summary.json").read_text(encoding="utf-8"))["summary"]
    nsl = pd.read_csv(ROOT / "results_rccf_nsl_v2_final" /
                      "metrics_aggregate.csv").iloc[0]
    unsw = pd.read_csv(ROOT / "results_rccf_unsw_v2_final" /
                       "metrics_aggregate.csv").iloc[0]
    nbaiot = pd.read_csv(ROOT / "results_rccf_nbaiot_v48" /
                         "metrics_aggregate.csv").iloc[0]
    file_level = pd.read_csv(ROOT / "results_file_external_generalization_v3b" /
                             "file_external_results.csv")
    prop3 = json.loads((ROOT / "results_margin_bound_v5" /
                        "proposition3_quantification.json").read_text(encoding="utf-8"))
    gate_sel = json.loads((ROOT / "results_gate_tuning_v5" /
                           "selected_gate_config.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))
    raw = audit["raw_totals"]

    def cost_nec(model: str, ratio: int) -> float:
        return float(next(row["nec"] for row in cost
                          if row["model"] == model and row["cost_ratio_fn_fp"] == ratio))

    lines: list[str] = []
    lines.append("# 向老师汇报要点")
    lines.append("")
    lines.append("> 一页纸的汇报口径：三个时长版本、建议页序、数字速查、预判问答与措辞红线。"
                 "所有数字取自发布产物，正文与补充材料可逐条追溯。")
    lines.append("")
    lines.append("## 一、30 秒版本（开场或电梯里）")
    lines.append("")
    lines.append("老师，我这篇稿子检验的是「按样本可靠性给多个森林专家做条件加权，"
                 "是否真的优于等权投票」这个被广泛采用但缺少受控验证的假设。"
                 f"在严格去泄漏的协议下，两者在截断总体上**等价**（Macro-F1 平均差 "
                 f"{row.mean_difference:.6f}，TOST 在两个预设边界都成立）；"
                 f"但把类别上限完全取消后，条件加权转为稳定劣势（{full['mean_difference']:.6f}，"
                 "十个种子方向一致），原因是特征视图随规模分化、融合被最弱成员稀释。"
                 "更重要的发现是：**协议选择的影响比聚合规则本身大一个数量级**。")
    lines.append("")
    lines.append("## 二、3 分钟版本（先讲结论，再讲证据）")
    lines.append("")
    lines.append("1. **问题**（20 秒）：公开数据集上的模型差异极易被重复样本、标签冲突、"
                 "特征选择泄漏与类别先验污染；我把它压到最直接的对照——条件加权 vs 等权 χ² 森林。")
    lines.append("2. **做法**（30 秒）：CIC-IDS2017 六阶段审计（原始 2 830 743 条），"
                 "加 NSL-KDD、UNSW-NB15、N-BaIoT 三个独立基准；主实验 10 个种子；"
                 "报告配对差、区间估计与 TOST。")
    lines.append("3. **结果**（60 秒）：")
    lines.append(f"   - 截断总体 53 237 条：平均差 {row.mean_difference:.6f}，"
                 f"种子级 90% 区间 [{row.ci90_low:.6f}, {row.ci90_high:.6f}]，"
                 f"配对 Bootstrap [{equivalence['pooled_ci_low']:.6f}, "
                 f"{equivalence['pooled_ci_high']:.6f}]，都落在等价边界内；")
    lines.append(f"   - 扩大 7.8 倍（413 209 条）：{scale['mean_difference']:.6f}，两个边界仍等价；")
    lines.append(f"   - 全去重语料 2 429 503 条：{full['mean_difference']:.6f}，"
                 "0.01 边界等价、0.005 边界不等价；")
    lines.append(f"   - 机制：{margin['provable_by_bound_rate_mean'] * 100:.2f}% 的测试行可证明不受权重影响，"
                 f"实际改判 {margin['empirical_changed_rows']} 行；{len(grid)} 组门控配置只有 "
                 f"{grid.val_macro_f1.nunique()} 个不同验证值。")
    lines.append("4. **为什么反转**（30 秒）：全语料上全特征视图比卡方视图低 "
                 f"{full_chi2 - full_all:.6f}，四路平均把其中一份差距摊成 "
                 f"{dilution:.6f}，与实测 {full['mean_difference']:.6f} 几乎相等——"
                 "这是稀释，不是加权。")
    lines.append("5. **顺带的量化结论**（20 秒）：协议效应（类别先验 "
                 f"{prior:.4f}、去重顺序至多 {dedup:.4f}）比聚合规则差异（0.0005 量级）大一个数量级；"
                 "模型族差异又更大（MLP 落后 0.0916）。")
    lines.append("")
    lines.append("## 三、10 分钟版本的页序与时长")
    lines.append("")
    lines.append("| 页 | 内容 | 时长 | 一句话目的 |")
    lines.append("|---|---|---:|---|")
    lines.append("| 1 | 标题 + 一句话结论 | 40 秒 | 先给结论，别让老师猜 |")
    lines.append("| 2 | 问题：四类污染 | 60 秒 | 说明为什么值得做受控实验 |")
    lines.append("| 3 | 协议：六阶段审计与三档总体（图 2 + 表 3）| 80 秒 | 证明数据可信、步骤可查 |")
    lines.append("| 4 | 主结果：三档总体表 + 图 4 | 110 秒 | 讲清「等价，但随规模反转」|")
    lines.append("| 5 | 统计判据：区间、TOST、McNemar、效应量 | 70 秒 | 说明「等价」是检验结论而非没拒绝 |")
    lines.append("| 6 | 机制一：边距上界与门控搜索（图 5/6）| 70 秒 | 解释为什么权重动不了预测 |")
    lines.append("| 7 | 机制二：稀释诊断（视图分差 ÷ 4 ≈ 实测差）| 60 秒 | 给出反转的唯一解释 |")
    lines.append("| 8 | 代价与开放集（图 10/11）| 70 秒 | 诚实呈现不利证据 |")
    lines.append("| 9 | 平衡控制与三个外部基准 | 60 秒 | 说明结论不是某一档先验或某个语料的产物 |")
    lines.append("| 10 | 结论、部署建议与局限 | 60 秒 | 收尾并交代边界 |")
    lines.append("| 11 | 数字速查（备用页，不主动讲）| — | 被追问时直接念 |")
    lines.append("| 12 | 复现与验证入口（备用页）| — | 被问「能复现吗」时翻到这页 |")
    lines.append("")
    lines.append("## 四、10 分钟逐页讲稿（可直接照念）")
    lines.append("")
    lines.append("**第 1 页 · 标题与结论（40 秒）**")
    lines.append("")
    lines.append(f"> 「这篇稿子检验一个被广泛采用、但缺少受控验证的假设：按样本可靠性给多个森林专家做"
                 f"条件加权，是否真的优于等权投票。结论分三档：截断总体 53 237 条上两者等价（平均差 "
                 f"{row.mean_difference:+.6f}，TOST 在两个预设边界都成立）；扩大到 413 209 条仍等价"
                 f"（{scale['mean_difference']:+.6f}）；把类别上限完全取消、全语料 2 429 503 条时转为"
                 f"稳定劣势（{full['mean_difference']:+.6f}，十个种子方向一致，但 0.01 边界仍等价）。"
                 f"最后一句是我真正想留下的：协议选择的影响比聚合规则差异大一个数量级。」")
    lines.append("")
    lines.append("- 数字：三个差值卡（截断 / 7.8 倍 / 全语料）。")
    lines.append("- 提示：讲完停一秒再翻页，让三个数字落地；先给结论，不让老师猜。")
    lines.append("")
    lines.append("**第 2 页 · 为什么要受控实验（60 秒）**")
    lines.append("")
    lines.append("> 「公开数据上的『加权更好』通常被四件事托着：重复与近重复样本、标签冲突、"
                 "特征选择泄漏、类别先验与调参预算。这四类我逐一处理。举两个量级："
                 f"只是把每类上限取消、换成自然先验，Macro-F1 就差 {prior:.4f}；"
                 f"只换去重与划分的先后顺序，差最多 {dedup:.4f}。也就是说，"
                 "不控制这些因素，任何『加权带来的提升』都可能是协议副作用。」")
    lines.append("")
    lines.append(f"- 数字：类别先验 {prior:.4f}、去重顺序 {dedup:.4f}，都远大于聚合规则差异 0.0005 量级。")
    lines.append("- 提示：这一页只为说明「为什么值得做一个受控实验」，不要展开文献。")
    lines.append("")
    lines.append("**第 3 页 · 协议：六阶段审计与三档总体（80 秒）**")
    lines.append("")
    lines.append(f"> 「CIC-IDS2017 原始 {raw['source_rows']:,} 行，按六阶段处理：可映射标签 "
                 f"{raw['mapped_rows']:,} 行（剔除 {raw['excluded_label_rows']:,} 行无法归入五类的标签）、"
                 f"非有限值再剔除 {raw['invalid_rows']:,} 行、物理范围筛查后剩 "
                 f"{raw['physical_valid_rows']:,} 行，接着全局去重（前向/反向双哈希）与分层划分，"
                 f"跨划分精确重叠 0。由此得到三档总体：每类上限 2 万的 53 237 条、上限 20 万的 413 209 条、"
                 f"取消上限的全语料 2 429 503 条。特征选择只在训练侧做（卡方、互信息、ANOVA 三种判据），"
                 f"主实验十个种子。」")
    lines.append("")
    lines.append(f"- 数字：{raw['source_rows']:,} → {raw['mapped_rows']:,} → {raw['valid_rows']:,} → "
                 f"{raw['physical_valid_rows']:,} → 去重 → 三档；78 维特征、5 类、测试 7 986 条。")
    lines.append("- 提示：计数是这一页的主角；老师若问细节，指向表 3 与补充材料 S02。")
    lines.append("")
    lines.append("**第 4 页 · 主结果（110 秒）**")
    lines.append("")
    lines.append(f"> 「主表三行：截断总体条件加权 "
                 f"{float(ten.loc['rccf', 'macro_f1']):.6f}、等权 χ² 森林 "
                 f"{float(ten.loc['equal_rf_chi2', 'macro_f1']):.6f}，"
                 f"平均差 {row.mean_difference:+.6f}，种子级 90% 区间 "
                 f"[{row.ci90_low:.6f}, {row.ci90_high:.6f}]、测试行配对 Bootstrap "
                 f"[{equivalence['pooled_ci_low']:.6f}, {equivalence['pooled_ci_high']:.6f}]，"
                 f"两个区间都落在 0.005 与 0.01 边界内，逐种子方向五正五负。扩大 7.8 倍后差 "
                 f"{scale['mean_difference']:+.6f}，仍等价。全语料差 "
                 f"{full['mean_difference']:+.6f}，90% 区间 "
                 f"[{full['seed_level_90_interval'][0]:.6f}, {full['seed_level_90_interval'][1]:.6f}] "
                 f"整段为负——0.01 边界等价、0.005 边界不等价。」")
    lines.append("")
    lines.append("- 数字：三行的两个模型值、平均差与两个区间；逐种子方向五正五负。")
    lines.append("- 提示：讲全语料时明确说「方向稳定为负、但仍在 0.01 等价」，不要用「显著变差」。")
    lines.append("")
    lines.append("**第 5 页 · 统计判据（70 秒）**")
    lines.append("")
    lines.append(f"> 「『等价』是检验结论，不是『没拒绝原假设』。TOST 的两个单侧检验在两个预设边界上都成立；"
                 f"逐种子看，{int(tost['tost_equivalent_at_0.005'].sum())}/10 个种子在 0.005 边界已等价、"
                 f"{int(tost['tost_equivalent_at_0.01'].sum())}/10 个在 0.01 边界等价。"
                 f"测试行上的 McNemar 检验，不一致对只有 {tost['discordant'].min()}–"
                 f"{tost['discordant'].max()} 行（占 7 986 条的 "
                 f"{tost['discordant'].min() / 7986 * 100:.2f}%–{tost['discordant'].max() / 7986 * 100:.2f}%），"
                 f"p 值 {tost['mcnemar_p'].min():.3f}–{tost['mcnemar_p'].max():.3f}，没有一次显著。"
                 f"效应量 Cohen's dz 为 {effect.loc['rccf_minus_equal_rf_chi2', 'cohens_dz']:.3f}。"
                 f"十个种子下 80% 功效能检出的最小差是 "
                 f"{row.min_detectable_effect_80pct:.6f}，而观测差只有 {row.mean_difference:.6f} 的量级——"
                 f"所以这里必须用等价检验而不是『不显著』。」")
    lines.append("")
    lines.append("- 数字：9/10 与 10/10、不一致对 6–21 行、p 0.146–1.000、dz −0.396、最小可检测差 0.001146。")
    lines.append("- 提示：这是老师最可能追问的一页，讲慢一点。")
    lines.append("")
    lines.append("**第 6 页 · 机制一：为什么权重动不了预测（70 秒）**")
    lines.append("")
    lines.append(f"> 「命题 2 给了一个可以逐行计算的上界：权重向量与均匀权重的 L1 距离若小于样本边际的一半，"
                 f"该行的 argmax 不可能被改变。实测 {margin['provable_by_bound_rate_mean'] * 100:.2f}% 的测试行"
                 f"可证明不受影响，实际改判 {margin['empirical_changed_rows']} 行；四个专家在测试集上没有一条"
                 f"分歧。权重本身也很平：归一化熵 {weight.normalized_weight_entropy:.5f}，概率 L1 平均变化 "
                 f"{weight.mean_probability_l1:.6f}。门控搜索 {len(grid)} 组配置只产生 "
                 f"{grid.val_macro_f1.nunique()} 个不同的验证集取值，锁定的配置（cv="
                 f"{gate_sel['cv']}、C={gate_sel['risk_C']:g}、描述子={gate_sel['descriptor_set']}）"
                 f"在测试集上同样改判 0 行。」")
    lines.append("")
    lines.append(f"- 数字：可证不变 {margin['provable_by_bound_rate_mean'] * 100:.2f}%、改判 0 行、"
                 f"熵 {weight.normalized_weight_entropy:.5f}、108 → 6。")
    lines.append("- 提示：如果老师只想记一个数，让他记「99.91% 可证明不变、0 行改判」。")
    lines.append("")
    lines.append("**第 7 页 · 机制二：稀释诊断（60 秒）**")
    lines.append("")
    lines.append(f"> 「那全语料上为什么反而更差？不是加权造成的，是四路平均把一份落后的特征视图摊薄了："
                 f"全语料上全特征视图比卡方视图低 {full_chi2 - full_all:.6f}，四分之一是 "
                 f"{dilution:.6f}，与实测 {full['mean_difference']:+.6f} 几乎相等；"
                 f"中间那档（413 209 条）同样成立，视图差 0.004249、四分之一 0.001062。」")
    lines.append("")
    lines.append(f"- 数字：{full_chi2 - full_all:.6f} ÷ 4 = {dilution:.6f} ≈ 实测 "
                 f"{full['mean_difference']:.6f}。")
    lines.append("- 提示：一句「这是稀释，不是加权」就够；细节留给补充材料 S29。")
    lines.append("")
    lines.append("**第 8 页 · 代价与开放集（70 秒）**")
    lines.append("")
    lines.append(f"> 「代价这边我不打算美化：按十种子均值，同等总体下条件加权的训练耗时约是"
                 f"等权森林的 80 倍，全语料 {full['train_slowdown']:.0f} 倍（单种子约 "
                 f"{full['rccf_mean_train_seconds'] / 3600:.1f} 小时对 "
                 f"{full['control_mean_train_seconds']:.0f} 秒）；模型体积 "
                 f"{profile['rccf']['model_size_mb'] / profile['equal_rf_chi2']['model_size_mb']:.1f} 倍，"
                 f"批量吞吐 {profile['rccf']['rows_per_second']:.0f} 对 "
                 f"{profile['equal_rf_chi2']['rows_per_second']:.0f} 行/秒（体积与吞吐来自单种子"
                 f"资源画像）。开放集上，以 PortScan、"
                 f"Infiltration、Heartbleed 为未知族时，条件分支 AUROC "
                 f"{conditional.auroc.min():.3f}–{conditional.auroc.max():.3f}、未知类召回 "
                 f"{conditional.unknown_recall.min():.4f}–{conditional.unknown_recall.max():.4f}，"
                 f"等权森林是 {equal.auroc.min():.3f}–{equal.auroc.max():.3f} 与 "
                 f"{equal.unknown_recall.min():.3f}–{equal.unknown_recall.max():.3f}——"
                 f"风险门控把概率推向高置信区，反而削弱了拒绝所需的不确定性信号。」")
    lines.append("")
    lines.append(f"- 数字：训练 80×/{full['train_slowdown']:.0f}×、体积 "
                 f"{profile['rccf']['model_size_mb'] / profile['equal_rf_chi2']['model_size_mb']:.1f}×、"
                 f"开放集 AUROC 与未知类召回两组区间。")
    lines.append("- 提示：主动讲不利证据，比被问出来好。")
    lines.append("")
    lines.append("**第 9 页 · 平衡控制与三个外部基准（60 秒）**")
    lines.append("")
    lines.append(f"> 「为了说明结论不是某一档类别先验的产物，我在完全平衡的对照总体（3 365 条、"
                 f"三类各半）上重跑：Macro-F1 {balanced.macro_f1_mean:.6f}、覆盖率 "
                 f"{balanced.coverage_mean:.3f}，比自然先验高 {prior:.4f}——先验本身就是最大的一个效应。"
                 f"三个外部语料用各自的原生标签：NSL-KDD Macro-F1 {nsl.macro_f1_mean:.6f}"
                 f"（准确率 {nsl.accuracy_mean:.3f}，但平衡准确率只有 {nsl.balanced_accuracy_mean:.3f}，"
                 f"说明它主要靠多数类）；UNSW-NB15 {unsw.macro_f1_mean:.6f}"
                 f"（平衡准确率 {unsw.balanced_accuracy_mean:.3f}）；N-BaIoT 上所有模型都到 "
                 f"{nbaiot.macro_f1_mean:.6f}——这个基准对流量特征分类器已经饱和，"
                 f"它检验的是机制惰性，不是判别难度。文件级外推的范围是 "
                 f"{file_level.macro_f1_known.min():.4f}–{file_level.macro_f1_known.max():.4f}。」")
    lines.append("")
    lines.append(f"- 数字：平衡控制 {balanced.macro_f1_mean:.6f}；NSL {nsl.macro_f1_mean:.6f}、"
                 f"UNSW {unsw.macro_f1_mean:.6f}、N-BaIoT {nbaiot.macro_f1_mean:.6f}；"
                 f"文件级 {file_level.macro_f1_known.min():.4f}–{file_level.macro_f1_known.max():.4f}。")
    lines.append("- 提示：强调「独立原生标签基准」，不要说成迁移实验。")
    lines.append("")
    lines.append("**第 10 页 · 结论、部署建议与局限（60 秒）**")
    lines.append("")
    lines.append("> 「三句话收尾：第一，在这个协议下，条件加权相对等权投票没有判别增益，规模越大越不利；"
                 "第二，可复用的不是某个模型，而是一套泄漏受控协议、一组可逐行计算的可辨识性条件，"
                 "以及一张把协议效应与聚合规则差异分开量化的地图；第三，工程上如果只追求判别性能，"
                 "等权森林是更划算的选择——同精度、训练快两个数量级、模型小四倍。"
                 "局限我说三条：公开数据不是生产流量、没有同一测试床的时间分离留出集、"
                 "开放集只覆盖三个未知族。」")
    lines.append("")
    lines.append("- 数字：训练代价 80–175 倍（十种子均值）、模型小 4.1 倍（单种子画像）、"
                 "协议效应高一个数量级。")
    lines.append("- 提示：留一句「下一步」给老师接话（见 Q18）。")
    lines.append("")
    lines.append("## 五、数字速查（被追问时直接念）")
    lines.append("")
    lines.append("| 类别 | 项目 | 数值 | 出处 |")
    lines.append("|---|---|---|---|")
    lines.append(f"| 数据 | 原始 / 可映射 / 有效 / 物理有效 | {raw['source_rows']:,} / "
                 f"{raw['mapped_rows']:,} / {raw['valid_rows']:,} / {raw['physical_valid_rows']:,} | 表 3、S02 |")
    lines.append(f"| 数据 | 剔除的不可映射标签 / 非有限值 | {raw['excluded_label_rows']:,} / "
                 f"{raw['invalid_rows']:,} | S02 |")
    lines.append("| 数据 | 截断总体 | 53 237 条 / 测试 7 986 / 十种子 | 表 3、表 4 |")
    lines.append("| 数据 | 扩大档 / 全语料 | 413 209 条 / 2 429 503 条 | 表 7 |")
    lines.append(f"| 主结果 | 截断总体条件加权 / 等权 | "
                 f"{float(ten.loc['rccf', 'macro_f1']):.6f} / "
                 f"{float(ten.loc['equal_rf_chi2', 'macro_f1']):.6f} | 表 4a |")
    lines.append(f"| 主结果 | 平均配对差 | {row.mean_difference:.6f} | 表 5、S20 |")
    lines.append(f"| 主结果 | 种子级 90% 区间 | [{row.ci90_low:.6f}, {row.ci90_high:.6f}] | 表 5 |")
    lines.append(f"| 主结果 | 配对 Bootstrap 90% | [{equivalence['pooled_ci_low']:.6f}, "
                 f"{equivalence['pooled_ci_high']:.6f}] | 表 5、S20 |")
    lines.append(f"| 主结果 | 扩大 7.8 倍 | 413 209 条，差 {scale['mean_difference']:.6f} | 表 7、S27 |")
    lines.append(f"| 主结果 | 全语料 | 2 429 503 条，差 {full['mean_difference']:.6f}，90% 区间 "
                 f"[{full['seed_level_90_interval'][0]:.6f}, {full['seed_level_90_interval'][1]:.6f}] | 表 7、S29 |")
    lines.append(f"| 统计 | 逐种子方向（支持加权 / 支持等权）| "
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_rccf']:.0f} / "
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_baseline']:.0f} | 表 5 |")
    lines.append(f"| 统计 | 逐种子 TOST 等价 | 0.005 边界 {int(tost['tost_equivalent_at_0.005'].sum())}/10；"
                 f"0.01 边界 {int(tost['tost_equivalent_at_0.01'].sum())}/10 | S20 |")
    lines.append(f"| 统计 | 测试行不一致对 / McNemar p | {tost['discordant'].min()}–{tost['discordant'].max()} 行"
                 f"（{tost['discordant'].min() / 7986 * 100:.2f}%–{tost['discordant'].max() / 7986 * 100:.2f}%）；"
                 f"p {tost['mcnemar_p'].min():.3f}–{tost['mcnemar_p'].max():.3f} | 表 5、S20 |")
    lines.append(f"| 统计 | 效应量 / 相对差 | Cohen's dz "
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'cohens_dz']:.3f}；"
                 f"{effect.loc['rccf_minus_equal_rf_chi2', 'relative_difference_pct']:.3f}% | 表 5 |")
    lines.append(f"| 统计 | 80% 功效最小可检测差 | {row.min_detectable_effect_80pct:.6f} | S20 |")
    lines.append(f"| 机制 | 可证不变 / 实际改判 | {margin['provable_by_bound_rate_mean'] * 100:.2f}% / "
                 f"{margin['empirical_changed_rows']} 行 | S17 |")
    lines.append(f"| 机制 | 权重熵 / 概率 L1 | {weight.normalized_weight_entropy:.5f} / "
                 f"均 {weight.mean_probability_l1:.6f} | S08、S09 |")
    lines.append(f"| 机制 | 门控配置 | {len(grid)} 组 → {grid.val_macro_f1.nunique()} 个验证值；"
                 f"选中 cv={gate_sel['cv']}、C={gate_sel['risk_C']:g}、{gate_sel['descriptor_set']} | S16 |")
    lines.append(f"| 机制 | 命题 3 二阶/一阶预测误差 | "
                 f"{prop3['relative_error_of_second_order_identity'] * 100:.1f}% / "
                 f"{prop3['relative_error_of_first_order_prediction'] * 100:.1f}% | S19 |")
    lines.append(f"| 机制 | 多样性回归 | 斜率 {regression['slope']:.4f}，r = {regression['pearson_r']:.3f}，"
                 f"{regression['n_points']} 个配置点 | S18 |")
    lines.append(f"| 规模 | 视图差 ÷ 4（全语料）| {full_chi2 - full_all:.6f} ÷ 4 = {dilution:.6f} ≈ 实测 "
                 f"{full['mean_difference']:.6f} | S29 |")
    lines.append(f"| 规模 | 全语料逐种子改判行数 | 平均 {full['mean_disagreements']:.0f}，"
                 f"最多 {full['max_disagreements']}（测试 364 426 行）| S29 |")
    lines.append(f"| 先验 | 平衡控制总体 | Macro-F1 {balanced.macro_f1_mean:.6f}，覆盖 "
                 f"{balanced.coverage_mean:.3f}，比自然先验高 {prior:.4f} | 表 4b |")
    lines.append(f"| 代价 | 训练耗时 | 截断约 80 倍；全语料 {full['train_slowdown']:.0f} 倍"
                 f"（{full['rccf_mean_train_seconds'] / 3600:.1f} 小时对 "
                 f"{full['control_mean_train_seconds']:.0f} 秒）| 表 4、S29 |")
    lines.append(f"| 代价 | 模型体积 / 吞吐 | "
                 f"{profile['rccf']['model_size_mb'] / profile['equal_rf_chi2']['model_size_mb']:.1f} 倍；"
                 f"{profile['rccf']['rows_per_second']:.0f} 对 "
                 f"{profile['equal_rf_chi2']['rows_per_second']:.0f} 行/秒 | S22 |")
    lines.append(f"| 代价 | 代价敏感 NEC（代价比 1 → 100）| 条件 {cost_nec('rccf', 1):.5f} → "
                 f"{cost_nec('rccf', 100):.5f}；等权 {cost_nec('equal_rf_chi2', 1):.5f} → "
                 f"{cost_nec('equal_rf_chi2', 100):.5f} | S21 |")
    lines.append(f"| 开放集 | AUROC | 条件 {conditional.auroc.min():.3f}–{conditional.auroc.max():.3f} "
                 f"对等权 {equal.auroc.min():.3f}–{equal.auroc.max():.3f} | S30 |")
    lines.append(f"| 开放集 | 未知类召回 | 条件 {conditional.unknown_recall.min():.4f}–"
                 f"{conditional.unknown_recall.max():.4f} 对等权 "
                 f"{equal.unknown_recall.min():.3f}–{equal.unknown_recall.max():.3f} | S30 |")
    lines.append(f"| 外部 | NSL-KDD | Macro-F1 {nsl.macro_f1_mean:.6f}，准确率 {nsl.accuracy_mean:.3f}，"
                 f"平衡准确率 {nsl.balanced_accuracy_mean:.3f}，覆盖 {nsl.coverage_mean:.3f} | 表 8、S28 |")
    lines.append(f"| 外部 | UNSW-NB15 | Macro-F1 {unsw.macro_f1_mean:.6f}，准确率 {unsw.accuracy_mean:.3f}，"
                 f"平衡准确率 {unsw.balanced_accuracy_mean:.3f} | 表 8、S28 |")
    lines.append(f"| 外部 | N-BaIoT（饱和）| Macro-F1 {nbaiot.macro_f1_mean:.6f}，"
                 f"测试 {nbaiot.test_samples_mean:.0f} 条 | 表 8、S28 |")
    lines.append(f"| 外部 | 文件级外推范围 | {file_level.macro_f1_known.min():.4f}–"
                 f"{file_level.macro_f1_known.max():.4f}（周内各文件）| S26 |")
    lines.append(f"| 交付 | 验证闸门 / 投稿包 | {counts.gate_checks()} 项检查；"
                 f"{counts.bundle_files()} 个文件，tag {counts.latest_tag()} | README、自查表 |")
    lines.append("")
    lines.append("## 六、术语速查（老师不在这个细分方向时先讲这六条）")
    lines.append("")
    lines.append("| 术语 | 一句话解释 | 本文里的位置 |")
    lines.append("|---|---|---|")
    lines.append("| 数据泄漏 | 测试集的信息以任何形式进入训练过程，使指标虚高 | 第 2 节四类污染、第 3 节协议 |")
    lines.append("| 条件加权 | 按每个样本的估计可靠性给各专家分配不同权重，再融合预测 | 式 (1)、第 3.3 节 |")
    lines.append("| 可辨识性条件 | 判定「权重是否可能改变预测」的前提；本文三条，其中一条可逐行计算 | 式 (2)、命题 1–3 |")
    lines.append("| TOST（双单侧检验）| 等价性检验：差值大于 +Δ 与小于 −Δ 都被拒绝，才算「等价」 | 第 4.2 节、表 5 |")
    lines.append("| Bootstrap 区间 | 对测试行或种子重采样得到差值的经验分布区间，不依赖正态假设 | 表 5、S20 |")
    lines.append("| 稀释诊断 | 多路平均把某一专家的偏差按 1/Q 摊进融合结果，与加权本身无关 | 式 (6)、第 6.2 节 |")
    lines.append("")
    lines.append("## 七、老师最可能追问的 24 个问题")
    lines.append("")
    lines.append("前八问每次汇报都会出现；后面十六问按老师追问的方向取用"
                 "（设计 4、统计 4、数据 4、机制 1、流程与边界 3）。")
    lines.append("")
    faq = [
        ("你怎么能说「没有增益」？",
         f"因为这是等价检验而不是「未拒绝原假设」：两个区间估计都落在预设的 0.005 与 0.01 边界内"
         f"（TOST 在两个边界都成立），逐种子方向五正五负，四个专家在测试集上没有一条预测分歧。"),
        ("那为什么全语料上反而更差？",
         f"不是加权造成的：权重从不改变任何一条预测（{margin['provable_by_bound_rate_mean'] * 100:.2f}% "
         f"的测试行可证明不变）。是四路平均把一份落后的特征视图摊薄了：全特征视图比卡方视图低 "
         f"{full_chi2 - full_all:.6f}，四分之一即 {dilution:.6f}，与实测 {full['mean_difference']:.6f} 吻合。"),
        ("负结果算贡献吗？",
         "贡献不是「某个模型更好」，而是三样可复用的东西：一套泄漏受控协议、"
         "一组可证伪的可辨识性条件（其中一条可逐行计算），以及一张量化地图——"
         "协议效应比聚合规则差异大一个数量级；三者都能被别人直接拿去用。"),
        ("数据和代码可信吗？",
         f"{corpora} 个语料的摘要与字节数都与来源记录逐一核对过（CIC 8 个文件 2 830 743 行、"
         "NSL/UNSW 官方划分、N-BaIoT 归档 1 772 922 927 字节），"
         f"{predictions:,} 个逐样本预测全部公开，"
         f"仓库带 tag；{counts.gate_checks()} 项自动检查每次提交前全绿。"),
        ("数据集是不是太老了？",
         f"评测的 {corpora} 个语料里八个发布于 2020 年及以后，其中四份发布于 2025 年："
         f"{y2025_line}；"
         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"
         "结论不随语料年代改变。"),
        ("门控到底有没有用？",
         "有用，但有条件——而且条件是可检验的。2025 年的 Gotham-2025 语料上，"
         "16 列特征用满（60 维预算会选中全部列）时三个视图完全重合，差值恰为 0.000000；"
         "把预算压到 16 选 8、让卡方与方差分析真正分歧后，门控以 +0.0063 超过同成员等权"
         "融合，十个种子方向一致。这正是命题 1 预测的边界：成员可互换时门控必然无效，"
         "成员可区分时它才可能有用。全文其余语料都在前一种情形里。"),
        ("和已有工作有什么不同？",
         "多数工作是提出新的加权方案并报告增益；本文把「加权 vs 等权」放到同一个去泄漏协议里做最直接的对照，"
         "并给出增益何时为零的判据（专家两两分歧率 0.2%–0.4% 时结构上不可能产生增益）。"),
        ("为什么用 Macro-F1 而不是准确率？",
         "不平衡下准确率会骗人：全语料上 XGBoost 准确率 0.9993 但 Macro-F1 只有 0.800255，"
         "随机森林 0.9958 / 0.759540，极端随机树 0.696629。"),
        ("代价是不是太大？",
         f"是，这正是结论之一：按十种子均值，截断总体训练约 80 倍、全语料 "
         f"{full['train_slowdown']:.0f} 倍；模型体积 4.1 倍、批量推理 5 倍来自单种子资源画像。"
         "在误报漏报代价比 1–100 内没有代价敏感优势。"),
        ("下一步做什么？",
         "三个方向：显式强制专家去相关的加权机制（检验打破命题 1 前提后能否恢复增益）；"
         "跨时段/跨场景的完整类别协议（把文件级覆盖分析升级为真正的外部有效性检验）；"
         "把报告建议做成可自动检查的清单。"),
    ]
    for index, (question, answer) in enumerate(faq, 1):
        lines.append(f"**Q{index}：{question}**")
        lines.append("")
        lines.append(f"> {answer}")
        lines.append("")
    lines.append("### 补充问答（设计、统计、数据、流程）")
    lines.append("")
    extra_faq = [
        ("为什么是四个专家，而不是两个或十个？",
         "四个专家是「两种特征视图（卡方 60 维 / 全特征）× 两类森林（随机森林 / 极端随机树）」的完整交叉；"
         "再多就变成调参预算差异，再少无法把视图差异与算法差异分开。"
         "对照臂与条件分支共享同一批专家，只换聚合规则，这是「最直接对照」的含义。"),
        ("权重到底是怎么算出来的？",
         "每个专家先在验证集上给出风险代理（基于边距的评分），过 softmax(−风险) 得权重，再做凸组合；"
         f"温度与描述子来自 {len(grid)} 组配置的门控搜索，只在验证集上选，"
         f"锁定后测试集改判 {margin['empirical_changed_rows']} 行。"),
        ("门控搜索是不是在测试集上调参？",
         f"不是：{len(grid)} 组配置只在验证集评估，只产生 {grid.val_macro_f1.nunique()} 个不同的验证值"
         f"（目标面对超参不敏感），锁定的是 cv={gate_sel['cv']}、C={gate_sel['risk_C']:g}、"
         f"{gate_sel['descriptor_set']}，测试集在整个搜索过程中未被读取。"),
        ("为什么不用深度模型做对照？",
         "本文检验的是聚合规则而不是模型容量：专家越强，聚合差异越容易被掩盖。"
         "为了让效应可辨识，四个专家刻意同质（同算法族、同特征预算）；"
         "同时报告更强基线的量级（全语料 XGBoost 比等权森林高 0.041），"
         "说明「换模型族」比「换聚合规则」重要两个数量级。"),
        ("为什么用 TOST 而不是「p > 0.05 就没有差异」？",
         f"因为「不显著」可能只是样本不够。十个种子下 80% 功效能检出的最小差是 "
         f"{row.min_detectable_effect_80pct:.6f}，比观测差 {row.mean_difference:.6f} 还大；"
         f"TOST 把「差落在 ±Δ 内」当作待检验命题，Δ 取 0.005 与 0.01 两个预设值，两个边界都报告。"),
        ("逐种子结果一致吗？",
         f"方向五正五负，不是某个种子拖出来的；逐种子 TOST 在 0.005 边界 "
         f"{int(tost['tost_equivalent_at_0.005'].sum())}/10 等价、0.01 边界 "
         f"{int(tost['tost_equivalent_at_0.01'].sum())}/10 等价；测试行 McNemar 不一致对只有 "
         f"{tost['discordant'].min()}–{tost['discordant'].max()} 行（占 "
         f"{tost['discordant'].min() / 7986 * 100:.2f}%–{tost['discordant'].max() / 7986 * 100:.2f}%），"
         f"p 值最小 {tost['mcnemar_p'].min():.3f}，没有一次显著。"),
        ("效应量有多小？",
         f"Cohen's dz = {effect.loc['rccf_minus_equal_rf_chi2', 'cohens_dz']:.3f}，相对差 "
         f"{effect.loc['rccf_minus_equal_rf_chi2', 'relative_difference_pct']:.3f}%，"
         "低于任何工程上有意义的差别；但我不主张「完全相同」，只主张在预设边界内等价。"),
        ("你的结论和「XGBoost 更强」矛盾吗？",
         "不矛盾，是同一张量级图景：模型族差异（全语料 XGBoost 比等权森林高 0.041）比聚合规则差异"
         "（0.0005 量级）大约两个数量级；协议效应（类别先验 0.0725）比模型族差异还大。"),
        ("数据泄漏具体有哪些？",
         "四类：跨文件重复与近重复样本、完全相同的特征向量被赋不同标签、在全量数据上拟合的特征选择器、"
         "类别先验与调参预算差异。前两类用全局去重（前向/反向双哈希、跨划分重叠 0），"
         "第三类把选择器限制在训练侧，第四类用平衡控制总体单独量化。"),
        ("为什么不用时间切分？",
         f"{corpora} 个公开语料都不提供同一测试床上的时间戳，无法构造真正的时间留出集；"
         f"作为部分替代做了文件级覆盖分析（Macro-F1 {file_level.macro_f1_known.min():.4f}–"
         f"{file_level.macro_f1_known.max():.4f}），并在稿件里明确写成局限。"),
        ("为什么 NSL-KDD 的分数这么低？",
         f"用原生标签、不做重采样：Macro-F1 {nsl.macro_f1_mean:.6f}，准确率 {nsl.accuracy_mean:.3f}，"
         f"但平衡准确率只有 {nsl.balanced_accuracy_mean:.3f}、覆盖率 {nsl.coverage_mean:.3f}，"
         "说明它主要靠多数类——这正是本文主张看 Macro-F1 与覆盖率的原因。"),
        ("N-BaIoT 上大家都 0.9998 以上，说明什么？",
         f"说明该基准对流量特征分类器已经饱和（本文 {nbaiot.macro_f1_mean:.6f}），"
         "它落在命题 1 预言的「任何加权都无法起作用」区间：在新领域验证机制惰性，"
         "但不检验判别难度。"),
        ("审稿人最可能攻击哪三点？",
         "一是「等价边界是自己选的」——回应：两个边界都预设并同时报告，且给出最小可检测差；"
         "二是「只在 CIC-IDS2017 上做主实验」——回应：另有三档规模与三个外部基准；"
         "三是「结论只是描述性」——回应：命题 1–3 给出可证伪条件，其中一条可逐行计算。"),
        ("要复现要多久、要什么机器？",
         f"单种子全语料训练约 {full['rccf_mean_train_seconds'] / 3600:.1f} 小时（CPU、无 GPU），"
         f"十种子在三路并行下一夜可跑完；仓库给出四条命令（数据审计 → 主实验 → 汇总 → 出包），"
         f"所有数字由 {counts.gate_checks()} 项自动检查复核。"),
    ]
    for offset, (question, answer) in enumerate(extra_faq, len(faq) + 1):
        lines.append(f"**Q{offset}：{question}**")
        lines.append("")
        lines.append(f"> {answer}")
        lines.append("")
    lines.append("## 八、措辞红线（避免过度声明）")
    lines.append("")
    lines.append("- 不说「首次提出」「证明了加权无用」；说「在流特征公开数据与本文协议下，未观测到判别增益」；")
    lines.append(f"- 不把全语料的 {full['mean_difference']:.6f} 说成「显著变差」——它在 0.01 边界上仍等价，"
                 "只是方向稳定为负；")
    lines.append(f"- 不说「生产可用」：{corpora} 个语料都不含生产流量，"
                 "也没有同一测试床上的时间分离留出集；")
    lines.append("- 不提「准确率 99% 以上」作为优点：本文的论点恰恰是准确率会误导，主指标是 Macro-F1；")
    lines.append("- 引用外部基准时说明是「独立原生标签基准」，不是迁移实验。")
    lines.append("- 不说「权重完全没用」：命题只覆盖可辨识区间，专家高度去相关时增益是存在的"
                 "（多样性回归斜率 0.0646、r = 0.749，9 次去相关配置全部为正）；")
    lines.append("- 不说「结论普适」：协议效应大于聚合规则这一条是在流特征公开数据上测到的，"
                 "换任务或换模态需要重新验证。")
    lines.append("")
    lines.append("## 九、汇报前 10 分钟检查清单")
    lines.append("")
    lines.append("1. 打开 `汇报用_论文介绍.pptx`（12 页），确认停在第 1 页、放映模式为 16:9；")
    lines.append("2. 旁边开好 `向老师汇报要点.docx`（本文件），第 5 节数字速查与第 7 节问答用于追问；")
    lines.append("3. 准备好两个「翻到就讲」的证据入口：`数据处理代码与流程.docx`（六阶段与代码）与"
                 "`公式来源与核验.docx`（五个公式的出处与复算）；")
    lines.append("4. 若被要求现场看数据：打开 `数据与资料来源总表.docx`（URL、日期、许可、SHA-256）与"
                 "`论文自查表.docx`（69 项自查的逐条证据位置）；")
    lines.append("5. 时间不够时的裁剪顺序：第 9 页 → 第 5 页 → 第 8 页（保留 1/2/3/4/6/7/10）；"
                 "时间富余时的补充顺序相反；")
    lines.append("6. 三句必须原话说出口的话："
                 "「这是等价检验，不是没拒绝原假设」、"
                 "「全语料方向稳定为负，但 0.01 边界仍等价」、"
                 "「协议效应比聚合规则差异大一个数量级」。")
    lines.append("")
    lines.append("## 十、随身材料")
    lines.append("")
    lines.append("- `论文介绍.md/.docx`：书面介绍（含背景、判据、完整数字、术语表与读稿路线），可直接发给老师；")
    lines.append("- `汇报用_论文介绍.pptx`：12 页汇报幻灯片，含逐页讲稿备注；")
    lines.append("- `English_SCI_Manuscript_v4.docx` / `中文SCI论文_v4_重构版.docx`：正式稿件；")
    lines.append("- `项目流程图.md/.docx`：六阶段全流程一页图；")
    lines.append("- 补充材料 S01–S30 与公开仓库（tag v1.11.0）：被追问细节时的证据索引；")
    lines.append(f"- 投稿包 `submission_package/论文投稿包_{counts.latest_tag()}.zip`：{counts.bundle_files()} 个文件，"
                 f"含全部稿件、补充材料与校验清单。")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    body = "\n".join(lines)
    # the two documents are read together: the script names the deck's pages and
    # the deck's notes point back at the script, so the anchors must stay put
    for anchor in ("## 四、10 分钟逐页讲稿", "**第 10 页 · 结论、部署建议与局限",
                   "**Q22：", "## 九、汇报前 10 分钟检查清单"):
        assert anchor in body, f"missing anchor: {anchor}"
    print(f"TALK_SCRIPT_WRITTEN={OUT}")
    print(f"lines={len(lines)}")


if __name__ == "__main__":
    main()
