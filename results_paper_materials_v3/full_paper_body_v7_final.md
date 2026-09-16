# 基于无泄漏特征选择与集成模型的网络入侵检测可复现实验研究

## 摘要

针对网络入侵检测研究中数据重复、类别不均衡、预处理泄漏和评价指标单一等问题，本文提出一套面向公开数据集的可审计实验协议。以CIC-IDS2017为主数据集，依次完成标签映射、无效值清理、全局特征向量去重、跨标签冲突审计、类别平衡和分层划分；归一化、特征评分和超参数选择均限制在训练数据或训练折内。主任务构建Normal、DoS/DDoS、Brute Force、Web Attack和Bot五分类平衡研究子集，共3,365条流量，每类673条。在统一配置（χ² Top-60、100棵树、min_samples_leaf=2）下，χ²随机森林三种种子的Accuracy为95.78%±0.11%，Macro-F1为95.79%±0.11%；全特征随机森林分别为95.78%±0.23%和95.79%±0.23%。10次重复分层划分未发现χ²筛选带来稳定显著提升。验证集性能加权与等权投票在逐样本预测上完全一致，说明当前单树性能集中时加权机制的边际作用有限。进一步在NSL-KDD和UNSW-NB15上进行独立标签体系基准验证，并报告类别级指标、概率质量、Bootstrap区间、开放集拒识、延迟和共享扰动结果。结果表明，本文工作的主要价值在于建立可复现、可核验的评价链条，而不是宣称某一模型在所有数据集或真实网关环境中普遍最优。

**关键词：** 网络入侵检测；CIC-IDS2017；NSL-KDD；UNSW-NB15；χ²特征选择；随机森林；数据泄漏审计；可复现研究

## 1 引言

网络入侵检测系统需要从连接记录或流量统计特征中区分正常行为与攻击行为。规则系统具有较强可解释性，但对变种攻击和组合型攻击需要持续维护规则库。机器学习方法能够从标注流量中学习统计模式，因此广泛用于拒绝服务、暴力破解、Web攻击和僵尸网络识别。然而，公开数据集中的重复记录、类别先验、文件边界和预处理方式会显著影响模型比较结果。

现有研究常将单次Accuracy作为主要结论，较少同时报告数据清洗阶段计数、训练集内特征选择、类别级指标、概率质量、重复划分和统计检验。若在划分前使用全体数据拟合归一化器或特征排序，测试信息可能通过变换参数进入训练过程；若忽略重复特征向量，训练和测试之间的相似记录也会导致性能高估。因此，本文将算法比较和数据协议审计作为两个相互关联但不混同的研究对象。

本文设置三个研究问题：RQ1，训练集内χ²筛选能否在降低输入维度的同时保持随机森林性能；RQ2，基于验证集单树性能的加权投票能否相对等权投票改善预测；RQ3，类别先验、公开文件划分、未知攻击和测量协议会如何改变模型结论。本文不预设优效结论，而是报告点估计、重复实验、置信区间和配对检验。

## 2 数据集与理论基础

### 2.1 CIC-IDS2017

CIC-IDS2017来源于加拿大网络安全研究所公开页面。原始`MachineLearningCSV`目录包含8个CSV文件、2,830,743条记录和78个流量统计特征。本文将BENIGN映射为Normal，将DDoS及各类DoS合并为DoS/DDoS，将FTP-Patator、SSH-Patator和Web Attack Brute Force合并为Brute Force，将XSS和SQL Injection合并为Web Attack，Bot保留为Bot。PortScan、Infiltration和Heartbleed不进入主五分类训练，仅用于开放集分析。

### 2.2 NSL-KDD

NSL-KDD文件来自公开`defcom17/NSL_KDD`镜像，保留KDDTrain+和KDDTest+原始边界。其标签体系为Normal、DoS、Probe、R2L和U2R，与CIC-IDS2017不同，因此仅作为独立公开数据集基准，不解释为跨数据集迁移。由于镜像精确commit未保存，本文提供本地文件SHA-256并将其描述为镜像快照，不推断未声明的标准许可证。

### 2.3 UNSW-NB15

UNSW-NB15来自UNSW Canberra Cyber项目页面，保留公开训练/测试文件边界。排除`id`、二元`label`和目标列`attack_cat`后，42个原始预测字段经训练集独热编码得到197个数值特征。其原生标签包括Normal、Generic、Exploits、Fuzzers、DoS、Reconnaissance、Analysis、Backdoor、Shellcode和Worms，与CIC标签体系不同，仅用于独立基准和协议敏感性分析。

### 2.4 随机森林与χ²筛选

设第i棵树对样本x输出类别概率向量$p_i(x)$，传统软投票为

$$p(c\mid x)=\frac{1}{T}\sum_{i=1}^{T}p_i(c\mid x).$$

对于特征j和类别c，令$O_{jc}$为观测频数、$E_{jc}$为独立性假设下的期望频数，则

$$\chi_j^2=\sum_c\frac{(O_{jc}-E_{jc})^2}{E_{jc}}.$$

本文先在训练集拟合Min-Max变换，使特征满足非负要求，再仅依据训练集计算χ²分数并选取Top-k。该统计量用于过滤式相关性排序，不表示因果关系。

### 2.5 加权投票与评价指标

将第i棵树在验证集上的平衡准确率记为$b_i$，加权系数定义为

$$w_i=\frac{b_i+\varepsilon}{\sum_{j=1}^{T}(b_j+\varepsilon)},$$

加权软投票为

$$p_w(c\mid x)=\sum_{i=1}^{T}w_i p_i(c\mid x),\quad \hat y=\arg\max_c p_w(c\mid x).$$

本文报告Accuracy、Balanced Accuracy、Macro-Precision、Macro-Recall和Macro-F1，并补充Log Loss、宏平均Brier Score、ECE、Bootstrap区间、McNemar检验和配对置换检验。Macro-F1定义为

$$Macro\text{-}F1=\frac{1}{|C|}\sum_{c\in C}F1_c.$$

## 3 数据处理与实验协议

### 3.1 数据审计

标签映射后保留2,671,766条记录；2,741条记录因无穷或非有限值被清除，得到2,669,025条有效记录。全局特征向量去重发现239,101条重复记录，其中跨标签冲突4,524条；冲突涉及133个唯一特征向量。去重和冲突处理后，按每类20,000条上限得到53,237条候选记录，再等量抽样形成3,365条五分类平衡研究子集。训练、验证和测试分别为2,355、505和505条，固定划分采用70%/15%/15%分层方案。

每条样本保留原始文件名、文件内行号、原始标签和映射标签等来源字段，但这些字段不进入模型输入。所有审计数字、文件标签覆盖和类别支持数均保存为机器可读表。

### 3.2 泄漏防控

全局去重和冲突处理属于数据集级协议，发生在最终划分前并被明确披露。Min-Max参数、χ²/互信息/ANOVA分数、类别编码和超参数选择均只使用训练集或训练折。验证集仅用于模型选择和单树权重估计，测试集仅用于锁定后的最终评估。来源字段、时间戳和原始标签不进入特征矩阵。

### 3.3 模型配置

主锁定配置为χ² Top-60、100棵树、min_samples_leaf=2、class_weight=balanced_subsample。对照模型包括决策树、SVM、ExtraTrees、全特征随机森林、χ²随机森林和验证集性能加权随机森林。固定数据划分使用随机种子42、2024和3407；另进行10次独立重复分层划分和训练集内交叉验证。NSL-KDD和UNSW-NB15分别使用其原生标签与公开训练/测试边界，不与CIC结果合并平均。

## 4 结果与分析

### 4.1 CIC主实验

χ²随机森林的平均Accuracy为95.78%±0.11%，Macro-F1为95.79%±0.11%；全特征随机森林分别为95.78%±0.23%和95.79%±0.23%。将78维压缩为60维后，性能基本保持，但没有证据支持显著提升。10次重复分层划分中，全特征RF的Macro-F1为95.70%±1.05%，χ²60 RF为95.72%±1.11%，配对符号置换p=0.969。

### 4.2 类别级指标、混淆矩阵与加权消融

seed=42的χ²随机森林中，Bot、DoS/DDoS、Normal、Brute Force和Web Attack的F1分别为1.000、0.980、0.965、0.924和0.913。Brute Force与Web Attack之间存在双向混淆。加权RF与等权投票逐样本预测完全一致，McNemar检验discordant pair为0、p=1.0。100棵树验证平衡准确率均值为0.9059、标准差为0.0114，树权重变异系数为1.26%，归一化权重熵为0.999983，平均概率L1差异为0.000299。

### 4.3 特征稳定性与概率质量

Top-10、Top-20和Top-60特征集合的平均Jaccard相似度分别为0.851、0.915和0.957。在相同Top-60预算下，互信息、ANOVA、χ²和全特征方案的Macro-F1分别为95.92%、95.98%、95.79%和95.79%；Log Loss分别为0.1339、0.1504、0.1344和0.1353；ECE分别为0.0246、0.0235、0.0244和0.0258。χ²的选择依据是计算简洁、可解释和与主协议一致，而不是所有指标上的最优。

### 4.4 鲁棒性与离线延迟

所有模型使用相同噪声矩阵和特征屏蔽掩码。χ² RF在1%高斯噪声下Macro-F1相对下降约30%，5%特征屏蔽下下降低于1%。batch=1时，χ² RF单线程P50/P95/P99为9.4590/11.8089/12.3521 ms，多线程为35.7258/45.1277/292.8834 ms；这些数字仅适用于已提取特征的离线predict调用，不代表真实网关端到端延迟。

### 4.5 不平衡和开放集

自然分布敏感性实验中，Accuracy约97.8%，但Macro-F1降至约89.1%—89.4%，seed=42的Web Attack F1仅0.546。将PortScan、Infiltration和Heartbleed作为未知攻击时，三类同时留出AUROC为0.9587、AUPR为0.9097、FPR@95TPR为0.0588、unknown recall为0.7488。未知拒识能力具有攻击家族依赖性，不能表述为开放集问题已经解决。

### 4.6 NSL-KDD独立基准

在KDDTrain+/KDDTest+原始边界上，RF全特征、RF-χ²、ExtraTrees-χ²和决策树-χ²的Accuracy分别为74.53%、74.98%、77.99%和75.60%，Macro-F1分别为51.19%、52.78%、59.91%和54.01%。ExtraTrees-χ²的Balanced Accuracy为57.07%；R2L召回率19.97%、F1为33.09%，U2R召回率17.00%、F1为23.53%。R2L和U2R大量被判为Normal，少数类是主要瓶颈。

### 4.7 UNSW-NB15独立基准

三种子平均结果为：RF全特征Accuracy=0.7038±0.0013、Balanced Accuracy=0.5677±0.0086、Macro-F1=0.4824±0.0021；RF-χ²分别为0.7083±0.0007、0.5415±0.0063和0.4673±0.0059；ExtraTrees-χ² Macro-F1=0.4249±0.0035；XGBoost-χ² Accuracy=0.7680±0.0013、Balanced Accuracy=0.5254±0.0075、Macro-F1=0.4838±0.0030。XGBoost的Accuracy和概率指标较高，但Balanced Accuracy低于RF全特征，表明多数类优势不能替代少数类分析。以seed=2024为例，RF全特征Accuracy为0.7025（Bootstrap 95%区间[0.6992, 0.7054]）、Macro-F1为0.4812（[0.4665, 0.4937]）；XGBoost-χ² Accuracy为0.7675（[0.7649, 0.7703]）、Macro-F1为0.4810（[0.4657, 0.4959]）。这些区间仅描述官方测试文件上的重采样不确定性。

官方训练/测试文件之间存在1,302个共同规范化特征键，覆盖8,541条测试记录（10.37%）。协议敏感性结果为：官方划分Accuracy=0.7085±0.0015、Balanced Accuracy=0.5354±0.0015、Macro-F1=0.4570±0.0010；删除测试侧重叠后分别为0.7419±0.0017、0.5675±0.0011和0.4851±0.0016；双方同时删除后分别为0.7414±0.0004、0.5506±0.0017和0.4770±0.0026。该结果说明公开文件边界和重复处理规则会改变汇总指标。

## 5 结论与局限性

本文构建了数据审计、训练集内预处理、特征选择、统一比较和统计验证相结合的可复现实验流程。CIC-IDS2017平衡研究子集上，χ²筛选将输入从78维降至60维，同时保持约95.79%的随机森林Macro-F1，但未显示稳定显著优势；验证性能加权与等权投票逐样本一致。NSL-KDD和UNSW-NB15验证了类别不均衡、少数类和公开划分重叠对结论的影响。本文不能将3,365条平衡子集结果外推为CIC全量性能，不能将文件级覆盖审计表述为完整时间外泛化，不能将独立数据集结果表述为跨数据集迁移成功，也不能将离线延迟表述为真实网关部署性能。

原始数据集不随代码仓库重新分发。代码、配置、审计摘要、逐样本预测、图表和统计结果发布于：https://github.com/linran-muxue/leakage-controlled-nids-study（release v1.0.2）。数据源页面、文件哈希和使用条款状态见项目`docs/`与`results_publication_final/`目录。

## 参考文献

[1] Sharafaldin I, Lashkari AH, Ghorbani AA. Toward generating a new intrusion detection dataset and intrusion traffic characterization. ICISSP, 2018:108–116. DOI:10.5220/0006639801080116.
[2] Tavallaee M, Bagheri E, Lu W, Ghorbani AA. A detailed analysis of the KDD CUP 99 data set. CISDA, 2009:1–6. DOI:10.1109/CISDA.2009.5356528.
[3] Breiman L. Random forests. Machine Learning, 2001, 45(1):5–32. DOI:10.1023/A:1010933404324.
[4] Liu H, Setiono R. Chi2: Feature selection and discretization of numeric attributes. ICTAI, 1995:388–391. DOI:10.1109/TAI.1995.479783.
[5] Buczak AL, Guven E. A survey of data mining and machine learning methods for cyber security intrusion detection. IEEE Communications Surveys & Tutorials, 2016, 18(2):1153–1176. DOI:10.1109/COMST.2015.2494502.
[6] Ring M, Wunderlich S, Grüdl D, Landes D, Hotho A. A survey of network-based intrusion detection data sets. Computers & Security, 2019, 86:147–167. DOI:10.1016/j.cose.2019.06.005.
[7] Khraisat A, Gondal I, Vamplew P, Kamruzzaman J. Survey of intrusion detection systems: Techniques, datasets and challenges. Cybersecurity, 2019, 2:20. DOI:10.1186/s42400-019-0038-7.
[8] McNemar Q. Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika, 1947, 12:153–157. DOI:10.1007/BF02295996.
[9] Efron B, Tibshirani RJ. Improvements on cross-validation: The .632+ bootstrap method. JASA, 1997, 92(438):548–560. DOI:10.2307/2965703.
[10] Moustafa N, Slay J. UNSW-NB15: A comprehensive data set for network intrusion detection systems. MilCIS, 2015:1–6. DOI:10.1109/MilCIS.2015.7348942.

[11] Demšar J. Statistical comparisons of classifiers over multiple data sets. Journal of Machine Learning Research, 2006, 7:1–30. https://www.jmlr.org/papers/v7/demsar06a.html.

## 数据参考

[dataset] Canadian Institute for Cybersecurity. CIC-IDS2017 dataset. n.d. https://www.unb.ca/cic/datasets/ids-2017.html (accessed 5 September 2026).
[dataset] defcom17. NSL_KDD repository snapshot. n.d. https://github.com/defcom17/NSL_KDD (accessed 5 September 2026).
[dataset] UNSW Canberra Cyber. UNSW-NB15 dataset. n.d. https://research.unsw.edu.au/projects/unsw-nb15-dataset (accessed 5 September 2026).

## 声明

Funding：如作者确认本研究没有任何外部专项、学校项目、导师项目、企业资助、奖学金或设备经费，可使用“This research received no external funding.”；否则应按实际机构和项目编号填写。

利益冲突：作者应在投稿系统中如实确认。原始数据仅来自公开页面，本文不包含扫描、渗透或未授权攻击流量采集。

生成式人工智能声明：论文准备过程中使用ChatGPT辅助语言编辑、文档组织、代码说明和可复现材料整理；作者已审阅并核验所有内容，对最终稿负责。
