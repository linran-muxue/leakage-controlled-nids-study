"""Merge the audited UNSW-NB15 analysis into the manuscript source."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results_paper_materials_v2" / "full_paper_body_v3.md"
OUT_DIR = ROOT / "results_paper_materials_v3"
OUT = OUT_DIR / "full_paper_body_v5_unsw.md"

UNSW_SECTION = r'''### 4.9 UNSW-NB15独立公开数据集基准

为检验实验流程在不同特征体系和标签定义下的可复现性，本文增加UNSW-NB15独立基准。实验严格采用官方`UNSW-NB15_training-set.csv`和`UNSW-NB15_testing-set.csv`划分，训练集包含175,341条记录，测试集包含82,332条记录，原始文件均为45列，标签列为`attack_cat`。训练文件SHA-256为`bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`，测试文件SHA-256为`734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`。审计未发现缺失单元或完全重复行。类别特征、Min-Max归一化和χ²排序均只在官方训练集内拟合，测试集保持独立。UNSW-NB15原生包含Normal、Generic、Exploits、Fuzzers、DoS、Reconnaissance、Analysis、Backdoor、Shellcode和Worms十类，与CIC-IDS2017五分类体系不同，因此本节只作为独立公开数据集基准，不解释为跨数据集迁移或标签对齐后的泛化。

三种随机种子（42、2024和3407）采用统一配置`k=60、100棵树、min_samples_leaf=2`。独热编码后实际得到43个可用数值特征，因此`k=60`被截断为全部43个特征，RF全特征和RF-χ²在该数据集上的输入完全相同，结果也完全一致。三种子平均结果为：RF Accuracy=0.8633±0.0004、Balanced Accuracy=0.6073±0.0073、Macro-F1=0.5627±0.0029；ExtraTrees-χ²的Macro-F1为0.5310±0.0026；XGBoost-χ²的Accuracy为0.8855±0.0007、Balanced Accuracy为0.5606±0.0036、Macro-F1为0.5491±0.0042。XGBoost-χ²的Log Loss=0.2924、宏平均Brier Score=0.0141、ECE=0.0190，均优于RF的0.4003、0.0170和0.0532，但其宏平均分类指标低于RF。由此可见，Accuracy优势主要受多数类影响，不能单独作为模型优劣依据。

### 4.10 UNSW-NB15类别级指标和少数类分析

以seed=2024为代表，RF对Normal的Recall为0.9999、F1为0.99996，但Analysis、Backdoor和DoS的F1分别仅为0.0041、0.0865和0.2557；XGBoost-χ²对应三类F1分别为0.0355、0.0390和0.1179。RF对Shellcode和Worms的Recall分别为0.8016和0.5455，XGBoost-χ²分别为0.6746和0.3636。测试集中的Analysis、Backdoor、Shellcode和Worms分别只有677、583、378和44条记录，少数类支持数不足导致宏平均指标与Accuracy之间存在明显差距。混淆矩阵显示，RF将大量DoS样本误判为Backdoor、Exploits或Fuzzers，XGBoost则将DoS大量判为Exploits；Analysis和Backdoor的预测数量也明显偏离真实支持数。类别级Precision、Recall、F1、支持数、预测数量以及归一化混淆矩阵分别见表A36—表A43。

Bootstrap采用测试集逐样本有放回重采样。以seed=2024为例，RF Accuracy为0.8634，1000次Bootstrap的95%区间为[0.8611, 0.8657]；Balanced Accuracy为0.6157，区间为[0.5998, 0.6311]；Macro-F1为0.5624，区间为[0.5476, 0.5746]。XGBoost-χ² Accuracy为0.8849，区间为[0.8829, 0.8871]；Macro-F1为0.5447，区间为[0.5283, 0.5595]。这些区间描述的是官方测试集抽样不确定性，不代表未来网络流量的保证区间。

### 4.11 UNSW-NB15结果边界

UNSW-NB15实验支持“同一审计和评估流程可以在不同公开数据集上独立复核”，但不支持以下结论：将UNSW-NB15十分类Accuracy与CIC-IDS2017五分类Accuracy直接比较；将`k=60`在UNSW-NB15上称为有效降维；将XGBoost的Accuracy优势解释为所有类别均得到改善；或将该结果写成跨数据集迁移成功。R2L/U2R少数类问题在NSL-KDD中同样存在，说明类别先验和小样本类别是网络入侵检测中需要单独处理的风险来源。

'''


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace(
        "进一步在官方NSL-KDD训练/测试划分上进行独立基准验证，并报告类别级指标、Bootstrap置信区间、离线推理延迟和扰动敏感性。",
        "进一步在官方NSL-KDD和UNSW-NB15训练/测试划分上进行独立基准验证，并报告类别级指标、Bootstrap置信区间、离线推理延迟和扰动敏感性。"
    )
    text = text.replace(
        "### 2.3 随机森林",
        "### 2.3 UNSW-NB15独立基准\n\nUNSW-NB15由澳大利亚新南威尔士大学相关项目构建，包含十类原生攻击标签。本文保留官方训练/测试边界，独热编码、归一化和χ²排序均只在训练集拟合。由于其标签体系、特征定义和类别先验均不同于CIC-IDS2017，结果仅用于独立公开数据集验证。\n\n### 2.4 随机森林"
    )
    start = text.index("### 4.9 NSL-KDD独立公开数据集基准")
    end = text.index("### 4.11 文件级泛化可行性与研究限制")
    old_nsl = text[start:end]
    old_nsl = old_nsl.replace("### 4.9 NSL-KDD独立公开数据集基准", "### 4.12 NSL-KDD独立公开数据集基准")
    old_nsl = old_nsl.replace("### 4.10 NSL-KDD少数类补充分析", "### 4.13 NSL-KDD少数类补充分析")
    replacement = UNSW_SECTION + old_nsl
    text = text[:start] + replacement + text[end:]
    text = text.replace("### 4.11 文件级泛化可行性与研究限制", "### 4.14 文件级泛化可行性与研究限制")
    text = text.replace("### 4.12 结论边界", "### 4.15 结论边界")
    text = re.sub(r"\\n{3,}", "\\n\\n", text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"WROTE={OUT}")


if __name__ == "__main__":
    main()
