# 4 实验结果与分析（UNSW-NB15独立基准补充）

## 4.9 数据来源与独立评估协议

UNSW-NB15实验使用官方划分的`UNSW-NB15_training-set.csv`和`UNSW-NB15_testing-set.csv`，训练集包含175,341条记录，测试集包含82,332条记录，均为45列，标签列为`attack_cat`。训练文件SHA-256为`bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`，测试文件SHA-256为`734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`。数据审计未发现缺失单元或完全重复行。实验保留官方训练/测试边界，不将两文件随机混合；类别特征的独热编码、Min-Max归一化和χ²排序均由训练集拟合。该数据集原生包含Normal、Generic、Exploits、Fuzzers、DoS、Reconnaissance、Analysis、Backdoor、Shellcode和Worms十类，与CIC-IDS2017五分类标签体系不同，因此本节仅作为独立公开数据集基准，不作为跨数据集迁移或标签对齐后的泛化证明。

## 4.10 三种子模型比较

表A1给出了三个随机种子（42、2024和3407）的汇总结果。排除`id`、二元`label`和目标列`attack_cat`后，42个原始预测字段经训练集词表独热编码为197个数值特征；因此`k=60`实际保留60个特征，RF全特征与RF-χ²使用不同输入矩阵。RF全特征的Accuracy为0.7038±0.0013，Balanced Accuracy为0.5677，Macro-F1为0.4824；RF-χ²的Accuracy为0.7083，Balanced Accuracy为0.5415，Macro-F1为0.4673。XGBoost-χ²取得最高Accuracy（0.7680），并具有最低Log Loss（0.5230）和ECE（0.0398），但其Balanced Accuracy（0.5254）低于RF全特征。这说明Accuracy优势主要受多数类影响，不能单独作为模型优劣结论。ExtraTrees-χ²的Macro-F1为0.4249。所有指标均限定于官方测试集和当前固定模型配置。

## 4.11 类别级指标与混淆分析

以seed=2024为代表，RF全特征对Normal的Recall为0.6558、F1为0.7869；Analysis、Backdoor和DoS的F1分别为0.0105、0.0600和0.2482。XGBoost-χ²的对应F1分别为0.0655、0.0345和0.0975；其Accuracy较高主要来自Generic、Normal、Exploits和Reconnaissance等样本量较大的类别。混淆矩阵显示，少数类预测数量明显偏离真实支持数，说明类别先验和边界重叠仍是主要瓶颈。正文应同时给出类别级Precision、Recall、F1、支持数、预测数量和归一化混淆矩阵，不能仅报告Accuracy。

## 4.12 少数类与概率质量

测试集中的Worms仅44条，Shellcode为378条，Analysis为677条，Backdoor为583条。代表性seed=2024中，RF全特征对Worms的Recall为0.4545，对Shellcode为0.8783；XGBoost-χ²对Worms的Recall为0.2727，对Shellcode为0.7116。XGBoost-χ²的Log Loss为0.5222，Brier Score为0.0284，ECE为0.0413，均低于RF全特征对应的0.6714、0.0342和0.0834；但其Balanced Accuracy为0.5172，低于RF全特征的0.5611。因此概率质量较好不等于少数类召回较高，分类性能与概率可靠性应分开报告。

## 4.13 结果解释与边界

UNSW-NB15结果支持三点结论：第一，官方训练/测试划分、训练集内预处理和逐样本概率保存可以构成独立可复核基准；第二，Accuracy、Balanced Accuracy、Macro-F1和概率指标对类别不均衡的反映不同；第三，少数类分析能够揭示总体Accuracy无法显示的风险。结果不支持以下表述：将UNSW-NB15十分类Accuracy与CIC-IDS2017五分类Accuracy直接比较；将RF-χ²在`k=60`下称为有效降维；将XGBoost的Accuracy优势解释为所有类别均得到改善；或将该独立基准写成跨数据集迁移成功。
