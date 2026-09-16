# 近五年网络入侵检测 SCI 文献扫描（2021–2025）

**检索日期：** 2026-09-11  
**检索范围：** 2021–2025 年，优先选择 IEEE、Elsevier、Springer、ACM、MDPI 等出版社页面及 DOI 永久链接；主题覆盖网络入侵检测、开放集识别、不确定性量化、数据泄漏与跨数据集泛化。  
**证据规则：** DOI/出版社元数据可定位的条目进入候选池；若摘要未给出数据集或数值指标，明确标记“需查全文”，不得在正文中补写未经核验的数字。

## 1. 可直接用于正文的高相关文献

| 编号 | 文献（年份、期刊/会议） | DOI / 一手 URL | 数据集与任务（证据状态） | 方法要点 | 可提取指标（证据状态） | 主要局限及对本文启示 |
|---:|---|---|---|---|---|---|
| 1 | Han S., Kim Y., Lee S. *Improvement of the Classification Performance of an Intrusion Detection Model for Rare and Unknown Attack Traffic*. **Electronics**, 2021, 10(18):2268. | [10.3390/electronics10182268](https://doi.org/10.3390/electronics10182268) | 论文涉及稀有/未知攻击流量；具体数据集版本需查全文 | 过采样、独立验证集、基于 softmax 概率的未知攻击判定 | 摘要报告未知攻击识别改进；表格数值需查全文 | 依赖 softmax 置信度，开放集校准有限；支持本文将未知攻击阈值限定在已知校准集上拟合 |
| 2 | Shin G.-Y. et al. *Unknown Attack Detection: Combining Relabeling and Hybrid Intrusion Detection*. **Computers, Materials & Continua**, 2021. | [10.32604/cmc.2021.017502](https://doi.org/10.32604/cmc.2021.017502) | 未知攻击检测；数据集与类别需查全文 | 重标记（relabeling）与混合 IDS | 需查全文提取 Accuracy、F1、未知召回等 | 跨数据集与时间漂移验证不足；可作为早期未知攻击路线对照 |
| 3 | Guolou P., Ye X. *Open-Set Intrusion Detection with MinMax Autoencoder and Pseudo Extreme Value Machine*. **IEEE IJCNN**, 2022. | [10.1109/IJCNN55064.2022.9892858](https://doi.org/10.1109/IJCNN55064.2022.9892858) | 开放集入侵检测；数据集需查 IEEE 全文 | MinMax Autoencoder 表征 + Pseudo Extreme Value Machine（PEVM） | 需查全文 | 会议短文，基准与部署成本信息有限；可作为 EVT/极值建模对照 |
| 4 | Baye G. et al. *Performance Analysis of Deep-Learning Based Open Set Recognition Algorithms for Network Intrusion Detection Systems*. **IEEE/IFIP NOMS**, 2023. | [10.1109/NOMS56928.2023.10154410](https://doi.org/10.1109/NOMS56928.2023.10154410) | 多数据集网络 IDS 开放集识别（具体集合需查全文） | 比较 OpenMax、EVM 等深度 OSR 末端算法 | 摘要说明比较已知准确率、未知检测率/OSCR；数值需查全文 | 主要是分析性基准而非新模型；支持本文把开放集结果定位为比较和边界分析 |
| 5 | Ali F. Y. et al. *Detecting Unknown Attacks in IoT Environments: An Open Set Classifier for Enhanced Network Intrusion Detection*. **IEEE MILCOM**, 2023. | [10.1109/MILCOM58377.2023.10356319](https://doi.org/10.1109/MILCOM58377.2023.10356319) | IoT 网络未知攻击（具体数据集需查全文） | 面向 IoT 的开放集分类器 | 需查全文 | 场景专用，跨域/时序鲁棒性有限；可用于说明 IoT 外部有效性仍需单独验证 |
| 6 | Guolou P. *OpenCADP: Open-Set Intrusion Detection with a Cluster Anomaly Detection Plugin*. **IEEE SMC**, 2023. | [10.1109/SMC53992.2023.10393991](https://doi.org/10.1109/SMC53992.2023.10393991) | 开放集 IDS；数据集需查全文 | 聚类异常检测插件（CADP）增强未知类识别 | 需查全文 | 依赖聚类假设和阈值，开放度敏感；可与本文共形拒识做机制对比 |
| 7 | Wu J. et al. *Open Set Dandelion Network for IoT Intrusion Detection*. **ACM Transactions on Internet Technology**, 2024. | [10.1145/3639822](https://doi.org/10.1145/3639822) | 知识丰富源域到数据稀缺目标 IoT 域的异构开放集（具体数据集需查全文） | 无监督异构域适配、类内紧凑/类间分离、目标成员机制、嵌入对齐与语义校正 | 摘要称目标 IoT 开放集有效；Accuracy/F1/H-score 需查全文 | 训练复杂，合成未知与真实零日可能有差距；可作为跨域开放集研究代表 |
| 8 | Yu W., Chen Z., Wang H. et al. *Industrial Network Intrusion Detection in Open-Set Scenarios*. **International Journal of Information Security**, 2024. | [10.1007/s10207-024-00949-2](https://doi.org/10.1007/s10207-024-00949-2) | CIC-IDS2017、Gas Pipeline（Springer 摘要明确） | BiGRU + Prototype Learning；Distance-Based Cross-Entropy 与 Prototype loss；类条件 Weibull EVT 拒识 | 摘要仅称已知类准确率高、不同 openness 下有效；具体数值需查全文 | 依赖 Weibull/阈值，数据集数量有限；支持本文报告 attack-family-dependent rejection 而不宣称通用开放集能力 |
| 9 | Talpini J., Sartori F., Savi M. *Enhancing Trustworthiness in ML-Based Network Intrusion Detection with Uncertainty Quantification*. **Journal of Reliable Intelligent Environments**, 2024. | [10.1007/s40860-024-00238-8](https://doi.org/10.1007/s40860-024-00238-8) | NF-ToN-IoT 与 CIC-IDS（摘要明确；具体版本和筛选规则需查全文） | 比较 NN、Bayesian NN、RF 的不确定性量化与 OoD/OSR；提出 BNN | 摘要称 BNN 在 OoD、鲁棒性、跨场景方差方面优于基线；AUROC/FPR/校准数值需查全文 | BNN 推理开销较高，离线流级评估；支持本文同时报告 ECE、Brier、Log Loss 与延迟 |
| 10 | Du L. et al. *Open World Intrusion Detection: An Open Set Recognition Method for CAN Bus in Intelligent Connected Vehicles*. **IEEE Network**, 2024. | [10.1109/MNET.2024.3367303](https://doi.org/10.1109/MNET.2024.3367303) | 车载 CAN 总线开放世界（数据集需查全文） | CAN 专用开放集识别 | 需查全文 | 域专用，迁移到通用网络流量需谨慎；用于讨论跨域可迁移性限制 |
| 11 | Qiu Z. et al. *VAEMax: Open-Set Intrusion Detection based on OpenMax and Variational Autoencoder*. **IEEE ICTC**, 2024. | [10.1109/ICTC61510.2024.10601788](https://doi.org/10.1109/ICTC61510.2024.10601788) | 开放集 IDS（数据集需查全文） | VAE 表征 + OpenMax 未知概率 | 需查全文 | 重构误差、OpenMax 阈值敏感；可作为本文最大概率/共形拒识基线的相关工作 |
| 12 | Fang J., Xie C. *Unknown Intrusion Traffic Detection Method Based on Unsupervised Learning and Open-Set Recognition*. **Scientific Reports**, 2025. | [10.1038/s41598-025-01084-1](https://doi.org/10.1038/s41598-025-01084-1) | CIC-IDS2017 开放集流量（摘要明确） | 信息最大化 GAN 闭集分类器 + 倒数第二层激活 + OpenMax | 摘要报告 misuse/anomaly 准确率分别高于 88.5%/88.2%；未知召回、OSCR 等需查全文 | 仅单一 CIC 数据集，GAN 成本高；准确率不能替代未知召回和开放集曲线，支持本文多指标报告 |
| 13 | Aly B. M., Azizol A. *An Empirical Study of Pattern Leakage Impact during Data Preprocessing on Machine Learning-Based Intrusion Detection Models Reliability*. **Expert Systems with Applications**, 2023. | [10.1016/j.eswa.2023.120715](https://doi.org/10.1016/j.eswa.2023.120715) | 预处理模式泄漏对 ML-IDS 的影响；具体数据集需查全文 | 实证比较存在/不存在 pattern leakage 的性能膨胀 | 需查全文提取 Accuracy、F1、AUROC 差异 | 聚焦特定泄漏模式，需更多数据集验证；与本文训练折内特征选择、全局去重和协议敏感性直接相关 |
| 14 | Mallampati S. B., Seetha H. *A Comparative Study on the Impacts of Data Leakage During Feature Selection using the CIC-IoT 2023 Intrusion Detection Dataset*. **IEEE ICEES**, 2024. | [10.1109/ICEES61253.2024.10776873](https://doi.org/10.1109/ICEES61253.2024.10776873) | CIC-IoT 2023（标题明确） | 比较全数据选特征与训练折内选特征的泄漏影响 | 需查全文 | 会议研究、单一数据集、仅关注特征选择泄漏；支持本文将筛选器严格限制在训练数据 |
| 15 | Medjadba Y., Drid H., Rahouti M. *Intrusion Detection in Software-Defined Networking using Hybrid Bayesian Model Averaging for Reliable Uncertainty Quantification*. **Computer Networks**, 2025. | [10.1016/j.comnet.2025.111436](https://doi.org/10.1016/j.comnet.2025.111436) | SDN IDS（数据集需查全文） | 混合 Bayesian model averaging，输出可靠不确定性 | 需查全文提取 AUROC/ECE 等 | SDN 拓扑专用且推理开销高；可用于比较不确定性量化路线与树模型成本 |
| 16 | Cantone M., Marrocco C., Bria A. *Machine Learning in Network Intrusion Detection: A Cross-Dataset Generalization Study*. **IEEE Access**, 2024. | [10.1109/ACCESS.2024.3472907](https://doi.org/10.1109/ACCESS.2024.3472907) | 跨数据集训练/测试域分离（具体数据集需查全文） | 系统评估跨数据集泛化 | 需查全文提取跨域性能跌落和统计方法 | 评估性研究，未必包含 OSR；直接支持本文把 NSL-KDD/UNSW 定位为独立基准而非迁移成功 |

## 2. 主题—本文证据对应关系

| 主题 | 文献证据 | 本文应补充或强调的内容 |
|---|---|---|
| 数据泄漏与预处理偏差 | Aly & Azizol 2023；Mallampati & Seetha 2024 | 明确去重在划分前执行、特征筛选/缩放在训练折内拟合；报告 protocol-sensitivity 的相对下降幅度 |
| 未知攻击与开放集 | Han 2021；Guolou & Ye 2022；Baye et al. 2023；Yu et al. 2024；Fang & Xie 2025 | 已知类与未知族严格分离；阈值只由已知校准集学习；同时报告 AUROC、AUPR、FPR@95TPR、unknown recall 与 OSCR/风险—覆盖率 |
| 不确定性与概率可靠性 | Talpini et al. 2024；Medjadba et al. 2025 | 报告 Log Loss、宏平均 Brier、ECE/MCE、Bootstrap 区间和校准曲线；不将置信度等同于未知检测能力 |
| 跨数据集/域泛化 | Wu et al. 2024；Du et al. 2024；Cantone et al. 2024 | NSL-KDD、UNSW-NB15 保持原生标签并单独报告；不能把不同标签空间合并为一个总分，也不能声称迁移成功 |
| 轻量化与可信部署 | Talpini et al. 2024；Medjadba et al. 2025 | 受控硬件上报告单线程/多线程 P50、P95、P99、吞吐、内存和模型大小；明确不等同端到端网关性能 |

## 3. 目前文献综述仍存在的缺口

1. **近五年直接 IDS 论文的全文数值尚未全部提取。** DOI 和出版社记录已定位，但摘要没有给出数据集、类别支持数或完整指标时，必须下载全文后再填表，不能凭搜索摘要补数字。
2. **缺少系统对比表。** 主文相关工作应至少列出数据集、标签空间、是否开放集、是否跨文件/跨域、是否训练折内防泄漏、报告的主要指标和可复现代码。
3. **算法贡献定位需收敛。** 现有文献显示 OpenMax、EVT、VAE、BNN、域适配等路线已有大量研究；CFRG-Forest 的差异应写成“树级 OOB 交叉拟合的样本条件门控及其边界评估”，不能声称首次解决开放集 IDS。
4. **指标不能只用 Accuracy。** 近年文献普遍关注未知召回、OSCR、AUROC/AUPR、校准和不确定性；本文应将 Macro-F1、Balanced Accuracy、Log Loss、Brier、ECE 与延迟并列。
5. **跨数据集结果不可直接平均。** 不同数据集标签和特征定义不同，文献中的跨域结果应作为动机，本文仍须保留 native-label independent benchmark 的表述。

## 4. 建议加入正文的引用位置

- **引言：** 引用 Aly & Azizol（泄漏风险）、Cantone et al.（跨数据集泛化）、Talpini et al.（不确定性量化）。
- **相关工作—开放集识别：** 引用 Han 2021、Guolou & Ye 2022、Baye et al. 2023、Yu et al. 2024、Fang & Xie 2025，并明确这些方法依赖概率阈值、EVT、OpenMax 或深度表征。
- **相关工作—可靠性与校准：** 引用 Talpini et al. 2024、Medjadba et al. 2025，说明概率质量和 OoD 检测应分开评价。
- **方法—防泄漏协议：** 引用 Aly & Azizol 2023、Mallampati & Seetha 2024，支持训练折内拟合筛选器/缩放器的设计。
- **讨论—适用边界：** 引用 Wu et al. 2024、Du et al. 2024，说明 IoT/CAN 专用开放集方法不能直接外推到 CIC 流量。

## 5. 参考文献入稿前核验清单

- [ ] 打开每个 DOI 出版商页面，核对作者顺序、题名、期刊/会议、年份、卷期、页码或文章号。
- [ ] 对“需查全文”的条目补录实际数据集版本、类别数、训练/测试协议、主要指标及数值；若全文无法获得，保留为相关工作候选，不放入定量对比表。
- [ ] 不把会议论文或预印本的摘要数字与期刊正式版本混用。
- [ ] 所有新文献在正文至少有一次引用，文末参考文献表逐条对应；DOI 使用 `https://doi.org/...` 规范形式。
- [ ] 仅在数据集、标签体系和评价指标一致时，才可在正文表格中横向比较；否则仅做定性综述。

## 6. 结论

近五年文献共同表明：网络 IDS 的可信性问题已从“单一准确率”扩展到预处理泄漏、跨域泛化、开放集未知攻击和概率不确定性。当前项目最有说服力的贡献不是宣称 CFRG-Forest 全面优于现有模型，而是提供一条可复现的、训练边界明确的评测链，并用重复划分、强基线、独立数据集和开放集结果展示其适用范围与失效边界。上述 16 篇文献可形成 SCI 相关工作骨架；在最终投稿前，应优先完成“需查全文”条目的定量字段核验。
