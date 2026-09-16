# NSL-KDD外部基准实验

NSL-KDD作为第二个公开数据集，采用其官方KDDTrain+/KDDTest+划分，不与CIC-IDS2017强行对齐标签。NSL-KDD的任务标签为Normal、DoS、Probe、R2L、U2R；本次数据中没有实际出现Other类别。

结果：

- RandomForest：Accuracy=73.80%，Macro-F1=47.29%
- ExtraTrees：Accuracy=76.49%，Macro-F1=51.15%

由于类别严重不平衡，Accuracy与Macro-F1差距较大。该结果仅用于跨数据集稳定性和数据分布差异分析，不用于宣称CIC-IDS2017五分类性能。
