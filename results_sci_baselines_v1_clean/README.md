# SCI 强基线实验（v1）

本目录使用 `data_processed_audit_v4` 的 CIC-IDS2017 五分类平衡研究子集，执行训练集拟合 Min-Max、训练集 χ² Top-60 特征选择、验证集配置选择和测试集最终评估。

模型：

- 全特征随机森林；
- χ² Top-60 随机森林；
- χ² Top-60 ExtraTrees；
- χ² Top-60 XGBoost。

每个模型在相同的三个随机种子（42、2024、3407）下运行，并保存逐样本类别预测和概率。`metrics_aggregate.csv` 为三 seed 汇总，`pairwise_statistics.csv` 为 XGBoost/ExtraTrees 相对 χ²-RF 的配对统计结果。

重要边界：这是第一轮统一基线实验，不是完整嵌套交叉验证。验证集用于候选配置选择，测试集仅用于最终评估；后续 SCI 主实验仍需实施外层重复划分和内层调参的嵌套验证。
