"""Assemble the supplementary material bundle described in the manuscripts (gap C1)."""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "重构版论文_v4_20260915" / "补充材料_S01_S28"

ITEMS: dict[str, tuple[str, list[str]]] = {
    "S01": ("数据集来源、检索日期与 SHA-256 校验",
            ["results_paper_materials_v3/tables/table_data_source_provenance_v1.csv"]),
    "S02": ("CIC-IDS2017 逐原始文件的处理阶段计数",
            ["results_data_audit_cic_natural_v3b/raw_file_stage_counts.csv",
             "results_data_audit_cic_natural_v3b/source_file_split_label_counts.csv"]),
    "S03": ("自然先验总体与平衡控制总体的类别支持数",
            ["results_data_audit_cic_natural_v3b/processed_split_summary.csv"]),
    "S04": ("训练侧卡方/互信息/ANOVA 得分与入选特征",
            ["results_cic_natural_baselines_v3b/feature_scores_training_only.csv",
             "results_cic_natural_baselines_v3b/selected_features.json"]),
    "S05": ("逐种子完整指标表",
            ["results_rccf_cic_natural_v3b/metrics_by_seed.csv",
             "results_cic_natural_baselines_v3b/metrics_3seeds.csv"]),
    "S06": ("各模型逐类别分类报告（三个种子）",
            ["results_rccf_cic_natural_v3b/classification_report_seed42.csv",
             "results_rccf_cic_natural_v3b/classification_report_seed2024.csv",
             "results_rccf_cic_natural_v3b/classification_report_seed3407.csv",
             "results_cic_natural_baselines_v3b/classification_report_equal_rf_chi2_seed42.csv"]),
    "S07": ("归一化混淆矩阵",
            ["results_cic_natural_baselines_v3b/confusion_matrix_normalized_cfrg_forest_chi2_seed42.csv",
             "results_cic_natural_baselines_v3b/confusion_matrix_normalized_equal_rf_chi2_seed42.csv"]),
    "S08": ("树级加权与等权投票的逐样本预测对比",
            ["results_weight_mechanism_v3/weight_prediction_comparison.csv",
             "results_weight_mechanism_v3/weight_mechanism_summary.csv"]),
    "S09": ("权重分布与权重熵完整记录",
            ["results_weight_mechanism_v3/tree_weight_distribution.csv"]),
    "S10": ("协议敏感性实验（去重顺序、重复划分）",
            ["results_protocol_sensitivity_v4/protocol_sensitivity_metrics.csv",
             "results_repeated_splits_v3/summary.csv",
             "results_repeated_splits_v3/paired_split_tests.csv"]),
    "S11": ("5x3 嵌套交叉验证逐折指标与配对统计",
            ["results_nested_modelwise_v1_5x3/outer_modelwise_summary.csv",
             "results_nested_modelwise_v1_5x3/paired_macro_f1_statistics.csv"]),
    "S12": ("NSL-KDD 逐类别指标与预测计数",
            ["results_rccf_nsl_v2_final/classification_report_seed42.csv",
             "results_rccf_nsl_v2_final/metrics_aggregate.csv"]),
    "S13": ("UNSW-NB15 逐类别指标与划分敏感性",
            ["results_rccf_unsw_v2_final/classification_report_seed42.csv",
             "results_rccf_unsw_v2_final/metrics_aggregate.csv"]),
    "S14": ("文件级外推压力测试逐文件结果",
            ["results_file_external_generalization_v3b/file_external_results.csv"]),
    "S15": ("校准、扰动鲁棒性与延迟百分位原始数值",
            ["results_cfrg_calibration_v2_verified/metrics.csv",
             "results_rccf_evidence_v3b/robustness_shared.csv",
             "results_rccf_evidence_v3b/latency_percentiles.csv"]),
    "S16": ("门控 108 种超参数配置搜索记录",
            ["results_gate_tuning_v5/gate_search_results.csv",
             "results_gate_tuning_v5/gate_search_summary.csv",
             "results_gate_tuning_v5/selected_gate_config.json"]),
    "S17": ("逐测试行的边距与扰动上界",
            ["results_margin_bound_v5/margin_bound_summary.csv",
             "results_margin_bound_v5/margin_bound_summary.json"]),
    "S18": ("专家多样性实验（五类专家集合 x 三种子）",
            ["results_diversity_v5/diversity_suite_results.csv",
             "results_diversity_v5/diversity_gain_regression.json"]),
    "S19": ("神经基线结果与选优门控的测试集确认",
            ["results_mlp_final_v5/metrics_aggregate.csv",
             "results_mlp_final_v5/mlp_vs_rccf_paired.csv",
             "results_tuned_gate_test_v5/tuned_vs_default_test.csv"]),
    "S20": ("十种子主实验、功效分析与效应量",
            ["results_seeds10_v5/metrics_by_seed.csv",
             "results_seeds10_v5/table4a_10seeds.csv",
             "results_seeds10_v5/power_analysis.csv",
             "results_seeds10_v5/effect_sizes.csv",
             "results_equivalence_10seeds_v5/tost_results.csv"]),
    "S21": ("近重复审计与敏感性检验",
            ["results_near_duplicate_v5/near_duplicate_summary.csv",
             "results_near_duplicate_v5/near_duplicate_sensitivity.csv"]),
    "S22": ("资源画像：模型体积、吞吐与峰值内存",
            ["results_resources_v5/resource_profile.csv",
             "results_resources_v5/resource_profile_summary.json"]),
    "S23": ("代价敏感评估（误报漏报代价比 1 至 100）",
            ["results_cost_v5/cost_sensitive_summary.csv",
             "results_cost_v5/cost_sensitive_by_seed.csv"]),
    "S24": ("参考文献 DOI 核验记录",
            ["results_review_v5/doi_verification.json"]),
    "S25": ("数据集覆盖矩阵与命题 3 定量验证",
            ["results_review_v5/dataset_coverage_matrix.csv",
             "results_margin_bound_v5/proposition3_quantification.csv",
             "results_margin_bound_v5/proposition3_quantification.json"]),
    "S26": ("扩展鲁棒性：标签噪声、缺失值与标定漂移",
            ["results_robustness_extended_v5/robustness_extended_summary.csv",
             "results_robustness_extended_v5/robustness_extended_all_seeds.csv",
             "results_robustness_extended_v5/robustness_extended_summary_3seeds.csv"]),
    "S27": ("规模敏感性：413 209 条总体与十种子配对比较",
            ["results_scale_sensitivity_v46/metrics_by_seed.csv",
             "results_scale_sensitivity_v46/metrics_aggregate.csv",
             "results_scale_sensitivity_v46/paired_by_seed.csv",
             "results_scale_sensitivity_v46/scale_sensitivity_summary.json",
             "results_rccf_cic_natural_v4_scale200k/metrics_aggregate.csv"]),
    "S28": ("N-BaIoT 基准：审计、类别支持度、逐种子指标与配对比较",
            ["data_processed_nbaiot_v48/dataset_summary.csv",
             "data_processed_nbaiot_v48/preprocess_config.json",
             "results_nbaiot_baselines_v48/metrics_by_seed.csv",
             "results_nbaiot_baselines_v48/paired_by_seed.csv",
             "results_nbaiot_baselines_v48/scale_sensitivity_summary.json",
             "results_rccf_nbaiot_v48/metrics_by_seed.csv"]),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    lines = ["# 补充材料索引 / Supplementary Material Index", "",
             "| 编号 | 内容 | 文件 |", "|---|---|---|"]
    checksums = []
    missing = []
    for key, (title, sources) in ITEMS.items():
        folder = OUT / key
        folder.mkdir()
        names = []
        for src in sources:
            path = ROOT / src
            if not path.exists():
                missing.append(src)
                continue
            target = folder / path.name
            shutil.copy2(path, target)
            names.append(f"{key}/{path.name}")
            checksums.append(f"{sha256(target)}  {key}/{path.name}")
        lines.append(f"| {key} | {title} | {'; '.join(Path(n).name for n in names) or '缺失'} |")
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"SUPPLEMENTARY_ASSEMBLED items={len(ITEMS)} files={len(checksums)}")
    if missing:
        print("missing sources:", missing)


if __name__ == "__main__":
    main()
