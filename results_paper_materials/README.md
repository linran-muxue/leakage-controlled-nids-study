# 论文结果材料索引

本目录中的表格、图片和文字均由已有真实实验结果自动生成，未重新抽样、未修改原始 CSV，也未虚构指标。

## 图像

- `figures/fig_chi2_top20.png`：χ²值前20特征排名
- `figures/fig_k_selection.png`：k值与验证集Macro-F1曲线
- `figures/fig_model_performance.png`：各模型Accuracy与Macro-F1对比
- `figures/fig_time_comparison.png`：训练和推理时间对比
- `figures/fig_confusion_matrix_rf_chi2_seed42.png`：随机森林+χ²60混淆矩阵

## 表格

- `tables/table_data_audit.csv`：数据清洗、去重和平衡审计
- `tables/table_split_class_counts.csv`：训练/验证/测试集类别数量
- `tables/table_model_comparison.csv`：全部模型均值、标准差和时间
- `tables/table_ablation.csv`：随机森林与加权随机森林消融对比
- `tables/table_class_metrics_by_model.csv`：各模型类别级指标
- `tables/table_class_metrics_key_models.csv`：主要模型类别级指标

## 文字

- `chapter4_results_draft.md`：第四章实验结果与分析初稿，可据此整理到论文正文。
- `journal_full_extension_report.md`：投稿版扩展实验报告。
- `journal_submission_upgrade.md`：目标期刊定位与投稿前检查。
- `journal_guidelines_research.md`：已核验的《计算机系统应用》官方要求及《计算机技术与发展》的核验边界。

## 外部数据集

- `../results_nsl_kdd/`：NSL-KDD下载文件哈希、预处理摘要、RandomForest/ExtraTrees外部基准结果和逐样本预测。
- `tables/table_external_dataset_results.csv`：NSL-KDD结果汇总。
- `tables/table_paired_significance_tests.csv`：基于逐样本预测的McNemar与配对置换检验。
- `tables/table_filewise_class_coverage.csv`：CIC-IDS2017按原始文件的类别覆盖审计。

## 使用边界

正式论文应采用三种子（42、2024、3407）的均值和标准差。单个 seed 只用于展示混淆矩阵，不用于替代正式汇总结果。加权随机森林没有超过普通随机森林，正文不得写成“显著提升”。
