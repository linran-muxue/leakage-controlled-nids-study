# 补充材料索引 / Supplementary Material Index

| 编号 | 内容 | 文件 |
|---|---|---|
| S01 | 数据集来源、检索日期与 SHA-256 校验 | table_data_source_provenance_v1.csv |
| S02 | CIC-IDS2017 逐原始文件的处理阶段计数 | raw_file_stage_counts.csv; source_file_split_label_counts.csv |
| S03 | 自然先验总体与平衡控制总体的类别支持数 | processed_split_summary.csv |
| S04 | 训练侧卡方/互信息/ANOVA 得分与入选特征 | feature_scores_training_only.csv; selected_features.json |
| S05 | 逐种子完整指标表 | metrics_by_seed.csv; metrics_3seeds.csv |
| S06 | 各模型逐类别分类报告（三个种子） | classification_report_seed42.csv; classification_report_seed2024.csv; classification_report_seed3407.csv; classification_report_equal_rf_chi2_seed42.csv |
| S07 | 归一化混淆矩阵 | confusion_matrix_normalized_cfrg_forest_chi2_seed42.csv; confusion_matrix_normalized_equal_rf_chi2_seed42.csv |
| S08 | 树级加权与等权投票的逐样本预测对比 | weight_prediction_comparison.csv; weight_mechanism_summary.csv |
| S09 | 权重分布与权重熵完整记录 | tree_weight_distribution.csv |
| S10 | 协议敏感性实验（去重顺序、重复划分） | protocol_sensitivity_metrics.csv; summary.csv; paired_split_tests.csv |
| S11 | 5x3 嵌套交叉验证逐折指标与配对统计 | outer_modelwise_summary.csv; paired_macro_f1_statistics.csv |
| S12 | NSL-KDD 逐类别指标与预测计数 | classification_report_seed42.csv; metrics_aggregate.csv |
| S13 | UNSW-NB15 逐类别指标与划分敏感性 | classification_report_seed42.csv; metrics_aggregate.csv |
| S14 | 文件级外推压力测试逐文件结果 | file_external_results.csv |
| S15 | 校准、扰动鲁棒性与延迟百分位原始数值 | metrics.csv; robustness_shared.csv; latency_percentiles.csv |
| S16 | 门控 108 种超参数配置搜索记录 | gate_search_results.csv; gate_search_summary.csv; selected_gate_config.json |
| S17 | 逐测试行的边距与扰动上界 | margin_bound_summary.csv; margin_bound_summary.json |
| S18 | 专家多样性实验（五类专家集合 x 三种子） | diversity_suite_results.csv; diversity_gain_regression.json |
| S19 | 神经基线结果与选优门控的测试集确认 | metrics_aggregate.csv; mlp_vs_rccf_paired.csv; tuned_vs_default_test.csv |
| S20 | 十种子主实验、功效分析与效应量 | metrics_by_seed.csv; table4a_10seeds.csv; power_analysis.csv; effect_sizes.csv; tost_results.csv |
| S21 | 近重复审计与敏感性检验 | near_duplicate_summary.csv; near_duplicate_sensitivity.csv |
| S22 | 资源画像：模型体积、吞吐与峰值内存 | resource_profile.csv; resource_profile_summary.json |
| S23 | 代价敏感评估（误报漏报代价比 1 至 100） | cost_sensitive_summary.csv; cost_sensitive_by_seed.csv |
| S24 | 参考文献 DOI 核验记录 | doi_verification.json |
