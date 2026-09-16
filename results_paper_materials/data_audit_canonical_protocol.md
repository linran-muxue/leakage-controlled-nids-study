# CIC-IDS2017 数据审计统一口径

## 推荐采用的唯一流水线

正式论文建议采用 `data_processed_audit_v2` 生成的审计口径。该目录是使用当前修正后的 `src/prepare_dataset.py` 从原始 8 个 CSV 重新扫描得到的审计快照，不能与旧版 `data/processed_dedup` 的模型结果混用。

## 字段定义与当前数值

| 字段 | 含义 | 数值 |
|---|---|---:|
| source_rows | 原始 8 个 CSV 的总数据行数 | 2,830,743 |
| mapped_rows | 标签映射到五分类后的行数 | 2,671,766 |
| invalid_rows | 含 NaN/正负无穷/无法转换为数值的行数 | 2,741 |
| valid_rows | 映射后且所有特征有效的行数 | 2,669,025 |
| duplicate_rows | 全局去重时遇到的重复行数 | 239,101 |
| unique_rows_before_conflict | 全局特征向量去重后、冲突剔除前的唯一向量数 | 2,429,924 |
| cross_label_conflict_hashes | 同一特征向量对应多个标签的冲突向量数 | 133 |
| unique_rows_after_conflict | 冲突向量剔除后的唯一向量数 | 2,429,791 |
| capped_rows_before_balance | 应用每类最多 20,000 条上限后的记录数 | 53,237 |
| balanced_rows | 按最小类别规模再次平衡后的记录数 | 3,365 |
| balanced_per_class | 每个主实验类别的样本数 | 673 |

## 必须遵守的算术关系

```text
valid_rows = mapped_rows - invalid_rows
unique_rows_after_conflict = unique_rows_before_conflict - cross_label_conflict_hashes
balanced_rows = balanced_per_class × 5
train + validation + test = balanced_rows
```

注意：`duplicate_rows` 是扫描过程中被识别为重复的行数，不应直接从 `valid_rows` 中再次扣除后推导唯一行数，因为跨标签冲突、哈希记录和旧版本去重逻辑可能使简单相减失真。正式论文直接报告代码产生的显式字段。

## 与旧结果的关系

旧目录 `E:\论文\data\processed_dedup` 中的 `dedup_audit.json` 将 `retained_rows_before_balance=712143` 与当前代码含义混在一起。重新扫描原始数据后，当前口径的“应用每类上限后记录数”为 53,237。由于重新采样还会改变训练/验证/测试中的具体样本，不能只替换 JSON 后继续声称旧模型结果对应新审计；若采用 v2，必须在 v2 数据上重跑最终实验。

## 正式论文推荐表述

“原始 8 个 CSV 共含 2,830,743 条记录。标签映射后保留 2,671,766 条，其中 2,741 条因缺失、无穷或非数值特征被清除。全局特征向量去重得到 2,429,924 个唯一向量，剔除 133 个跨标签冲突向量后剩余 2,429,791 条记录。应用每类 20,000 条上限后保留 53,237 条，再按五个目标类别的最小可用规模进行平衡，得到 3,365 条样本（每类 673 条）。随后按照 70%/15%/15% 分层划分为训练集、验证集和测试集。”

## 执行步骤

1. 保留 `data_processed_audit_v2` 作为候选最终数据目录，不覆盖旧目录。
2. 先检查 `data_processed_audit_v2/dedup_audit.json`、`dataset_summary.csv` 和三份划分文件。
3. 以 v2 为输入重新运行无泄漏参数选择、统一基线、NSL-KDD 外部实验不受影响、部署和统计分析。
4. 重新生成 `results_paper_materials/tables/table_data_audit.csv` 和第四章文字。
5. 只在所有结果都来自同一数据目录后，才生成最终 Word 稿。
