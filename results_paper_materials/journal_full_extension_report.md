# 投稿版扩展实验报告

## 已完成并真实运行

### 1. ExtraTrees 基线

在同一训练/验证/测试划分、同一χ²60特征集和三个随机种子下加入 ExtraTrees。结果文件位于 `results_journal_full`，包括分类报告、混淆矩阵、逐样本预测和汇总指标。

三种子平均结果：ExtraTrees+χ²60 的 Accuracy 约为95.17%，Macro-F1约为95.14%，低于全特征随机森林。

### 2. 逐样本预测保存

`results_journal_full/predictions_*.csv` 保存每个测试样本的 `y_true` 和 `y_pred`，可支持后续McNemar检验、错误样本分析和审稿复核。

### 3. McNemar 与配对置换检验

结果位于 `tables/table_paired_significance_tests.csv`。随机森林全特征与χ²随机森林、加权随机森林之间的差异均未达到显著水平；ExtraTrees与随机森林的差异同样未达到显著水平。正文应写“未观察到统计显著差异”，不要写“显著优于”。

### 4. 加权策略消融

比较了 balanced accuracy、普通 accuracy 和 macro-F1 三种树权重。结果位于 `results_weight_ablation/weight_strategy_summary.csv`。三种策略在当前测试集上的指标完全一致，说明当前数据下加权目标函数不是主要性能决定因素。

### 5. 按文件划分可行性审计

结果位于 `tables/table_filewise_class_coverage.csv`。CIC-IDS2017的攻击类型按场景文件集中分布，严格按文件切分会导致部分测试类别在训练集完全不存在，因此不能把它直接作为标准五分类外推实验。该审计本身可作为数据集局限性分析。

## 尚未完成

### 第二公开数据集

NSL-KDD已完成下载、预处理和外部基准实验。其官方训练/测试划分保留，标签体系为Normal、DoS、Probe、R2L、U2R，与CIC-IDS2017不一致，因此作为独立基准任务报告。RandomForest的Accuracy/Macro-F1为73.80%/47.29%，ExtraTrees为76.49%/51.15%。

### 真正时间外推实验

当前处理后的CSV没有保留原始文件名和时间戳字段，因此无法从现有processed数据重建严格时间切分。若要完成，需要重新生成带 `source_file` 或时间字段的审计数据，并预先定义训练日、验证日和测试日，不能事后根据测试结果调整。

## 期刊结论建议

本文可以将贡献表述为：

1. 构建了带全局去重、冲突剔除、训练集特征选择和数据泄漏审计的可复现实验流程；
2. 通过交叉验证确定χ²特征数量和随机森林超参数；
3. 在平衡与自然不平衡两种数据设置下，系统比较随机森林、ExtraTrees、SVM和决策树；
4. 通过Bootstrap、McNemar和配对置换检验报告不确定性与模型差异；
5. 证明在当前CIC-IDS2017五分类设置下，χ²特征压缩能够基本保持性能，但加权投票没有带来统计显著收益。
