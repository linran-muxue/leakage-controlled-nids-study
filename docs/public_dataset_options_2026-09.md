# 可新增公开网络入侵检测数据集评估（SCI升级候选，2026-09）

## 1. 目的与筛选原则

当前项目已经完成 CIC-IDS2017 与 NSL-KDD 的独立验证。为增强 SCI 稿件的外部有效性，新增数据集应满足：

1. 有可追溯的官方数据页或原始发布论文；
2. 下载地址、版本、文件哈希和许可证/使用条款能够记录；
3. 标签体系与 CIC-IDS2017 明确不同，能够检验跨场景稳健性；
4. 不需要真实联网扫描、攻击或在线采集；
5. 能够在个人电脑上通过分块读取、抽样或官方小子集完成实验；
6. 结果可以与当前模型协议保持一致：训练集内预处理、训练集内特征选择、独立测试集、逐样本预测和概率指标。

数据集的“公开可下载”不等同于“许可证完全自由”。在正式投稿前应保存官方页面截图/网页存档、下载日期、文件哈希，并逐条核对使用条款。

## 2. 候选数据集对比

| 数据集 | 官方来源/发布方 | 典型规模与格式 | 标签特点 | CPU可行性 | 对当前论文的价值 | 主要风险 |
|---|---|---|---|---|---|---|
| **UNSW-NB15** | [UNSW Canberra Cyber 官方项目页](https://research.unsw.edu.au/projects/unsw-nb15-dataset)；原始论文：Moustafa and Slay, MILCOM 2015 | 官方提供 `UNSW-NB15_training-set.csv` 与 `UNSW-NB15_testing-set.csv`，约25.8万条记录；约49个流量属性（含标识/标签字段） | Normal 加 9个攻击族：Fuzzers、Analysis、Backdoors、DoS、Exploits、Generic、Reconnaissance、Shellcode、Worms | **高**；文件小于CIC-IDS2018/BoT-IoT，可直接分块读取 | 与CIC标签体系、生成环境和特征集合不同；适合做第三个独立多分类基准 | 官方页面通常未给出类似软件包的统一OSI许可证；需保留下载条款。部分特征是由特定工具生成，不能直接声称代表真实企业流量 |
| **Edge-IIoTset** | [Mendeley Data 数据页](https://data.mendeley.com/datasets/2fjmq8rmn6/1)；原始论文：Ferrag et al., IEEE TII 2022 | IoT/IIoT testbed 流量，约61个特征、14类攻击加Normal，提供CSV；可下载后按文件/类别抽样 | DoS/DDoS、扫描、注入、密码、木马、XSS等多种攻击；类别体系与CIC不同 | **中高**；建议使用官方CSV并按每类封顶，不读取原始pcap | 适合证明模型对IoT/IIoT场景的外部有效性；Mendeley页面便于记录DOI和版本 | 需核对当前版本、文件大小和许可证；同一测试床生成的数据存在环境偏差，不能等同真实生产网络 |
| **TON_IoT** | [UNSW Canberra Cyber 官方项目页](https://research.unsw.edu.au/projects/toniot-datasets)；原始论文：Moustafa et al., IEEE Access 2021 | 异构数据集：网络流、Windows/Linux遥测、IoT传感器和系统日志；CSV/JSON等多种格式，规模从小文件到较大子集 | 网络攻击和主机/IoT事件标签，包含扫描、DoS/DDoS、注入、密码、勒索软件等；标签按数据源分别定义 | **中**；优先选择官方网络流子集，避免一次性加载全套异构遥测 | 可扩展为“网络流+主机遥测”的跨模态外部验证，创新性高于再次使用CIC家族 | 数据源和标签定义不完全统一；需要预先锁定一个子任务，不能把不同模态直接拼接后报告单一指标；许可证及下载权限需核验 |
| **CIC-DDoS2019** | [Canadian Institute for Cybersecurity 官方页面](https://www.unb.ca/cic/datasets/ddos-2019.html) | 80个CICFlowMeter特征，含大量DDoS攻击流；原始pcap和CSV均较大，适合抽样 | 以DDoS/反射放大类为主（DNS、LDAP、MSSQL、NetBIOS、NTP、SNMP、SSDP、SYN、TFTP、UDP等）及Benign | **中低**；只建议使用官方CSV的分层抽样，不建议在个人电脑处理全部pcap | 适合做DDoS专项鲁棒性或攻击家族细分实验 | 与CIC-IDS2017共享CICFlowMeter风格和部分实验范式，独立性较弱；类别极不平衡且DDoS任务窄，不宜作为唯一第三数据集 |
| **CSE-CIC-IDS2018** | [UNB/CIC 官方页面](https://www.unb.ca/cic/datasets/ids-2018.html) | 多日网络流量、CSV/pcap；规模通常为GB级甚至更大，约80个流量特征 | Benign、Brute-force、Botnet、DoS/DDoS、Web、Infiltration、Heartbleed等 | **中低**；必须按文件和类别分块抽样 | 可做与CIC-IDS2017相近协议的跨年度/跨场景补充 | 与当前数据集同属CIC系列，特征工程高度相似，外部有效性增益有限；大文件和类别覆盖差异会增加处理成本；不能把两者当作完全独立来源 |
| **BoT-IoT** | [UNSW Canberra Cyber 官方项目页](https://research.unsw.edu.au/projects/bot-iot-dataset)；原始论文：Koroniotis et al., IEEE TDSC 2021 | 原始数据可达数千万流；官方提供5%子集及CSV/pcap选项；约46个网络特征 | Normal、DDoS、DoS、Reconnaissance、Theft等IoT攻击大类及更细标签 | **中**；建议固定使用官方5% CSV并设置每类上限 | IoT场景、严重类别不平衡和攻击家族不同，可用于自然分布敏感性 | 数据量与类别比例极不平衡；合成IoT测试床偏差明显；许可证/使用条款需从官方页面确认 |
| **IoT-23** | [Stratosphere Laboratory 官方数据页](https://www.stratosphereips.org/datasets-iot23) | 20个恶意/良性IoT场景，原始pcap和标注文件；通常需要自行提取流特征 | 按恶意软件家族和场景标注，含Benign、Mirai、Gafgyt等 | **低到中**；如果没有现成流特征，需额外安装Zeek/CICFlowMeter并处理pcap | 独立的IoT恶意流量来源，可进行跨设备/跨场景实验 | 预处理成本高；标签粒度与当前五分类不一致；需严格记录特征提取器版本和许可 |

## 3. 首选推荐

### 首选：UNSW-NB15

建议把 UNSW-NB15 作为最先新增的数据集，原因是：

- 规模适中，个人电脑可完成分块读取和多模型重复实验；
- 官方训练集/测试集划分已提供，便于避免随机重划分争议；
- 9个攻击族与CIC-IDS2017、NSL-KDD均不完全相同，能够检验标签体系变化下的性能；
- 不需要处理超大pcap，新增数据的工程成本最低；
- 可以复用当前的审计框架：文件哈希、标签映射、训练集内特征选择、自然分布和逐样本预测。

建议任务定义为“UNSW-NB15十分类（Normal+9攻击族）”，不要强行映射为CIC-IDS2017的五分类。这样论文中应称为“独立数据集验证”，而不是跨数据集迁移。

### 第二选择：Edge-IIoTset

若希望突出物联网/工业互联网应用，Edge-IIoTset 比再次加入 CSE-CIC-IDS2018 更有外部场景价值。其优势是标签多样、特征格式相对规整，并可通过按类别封顶控制内存。应在下载后先核验版本、文件哈希和许可证，再决定是否纳入主文或补充材料。

### 不建议立即加入：CSE-CIC-IDS2018

CSE-CIC-IDS2018 可以作为补充，但不宜作为论文“独立性”主要证据：它与CIC-IDS2017共享CIC数据生成和流特征生态，且文件较大、标签覆盖不均，新增实验可能只是重复验证同一类数据偏差。

## 4. 跨数据集实验设计建议

不要把不同数据集的标签直接合并后训练一个模型。建议采用以下三种协议之一，并在论文中明确：

### 协议A：独立数据集复现实验（推荐）

对每个数据集分别完成：

1. 数据审计、文件哈希和标签分布；
2. 数据集原生训练/测试划分或严格分层划分；
3. 每个训练折内单独拟合缺失值处理、标准化和特征选择；
4. 统一报告 Macro-F1、Balanced Accuracy、少数类F1、Log Loss、ECE和P95延迟；
5. 不比较不同数据集的绝对Accuracy高低，只比较同一数据集内模型相对关系。

### 协议B：跨数据集零样本迁移（高风险）

只有在两个数据集存在可审计的共同特征和共同标签语义时才可做。当前CIC-IDS2017与UNSW-NB15的字段和标签并不直接同构，因此不建议把它作为近期主实验。

### 协议C：跨场景预训练/微调（高成本）

需要先定义公共特征、标签映射和训练预算，并报告从头训练、预训练后微调和目标域少样本三组结果。若没有足够样本和严格协议，容易被审稿人质疑为标签工程而非真正迁移学习。

## 5. 下载和数据审计要求

在实际下载前，不要先下载原始pcap。应按以下顺序：

1. 记录官方页面URL、发布方、访问日期和版本号；
2. 优先下载CSV或官方小子集；
3. 使用SHA-256和MD5记录文件完整性；
4. 保存原始压缩包，不在原始目录覆盖文件；
5. 运行文件级审计：行数、列数、标签计数、缺失值、无穷值、重复行、跨标签冲突；
6. 先锁定标签映射，再做抽样；
7. 生成 `source_file`、`source_row_id` 和 `processed_row_id` 旁车字段；
8. 只在训练数据内拟合选择器和缩放器，测试集保持独立；
9. 将数据集纳入 `MANIFEST`，记录文件哈希、参数、随机种子、代码版本和输出路径。

## 6. 预期创新点增强方式

新增数据集本身不是创新。更有价值的表述是：

1. **跨数据源稳健性**：同一审计和建模协议在CIC-IDS2017、NSL-KDD、UNSW-NB15/Edge-IIoTset上重复验证；
2. **标签体系敏感性**：不强行合并标签，分别报告原生攻击族上的Macro-F1和少数类表现；
3. **数据协议敏感性**：同时报告全局去重、训练侧去重、自然分布和类别封顶结果；
4. **概率质量与部署代价**：将Log Loss、Brier、ECE与P50/P95/P99延迟并列，而不是只报告Accuracy；
5. **可复现审计链**：公开哈希、来源字段、逐样本预测、配置文件和统计检验结果。

## 7. 最终建议

当前最稳妥的实施顺序为：

1. 先新增 **UNSW-NB15**，完成独立十分类基准；
2. 若首轮结果稳定，再增加 **Edge-IIoTset** 作为IoT/IIoT外部场景；
3. CSE-CIC-IDS2018和CIC-DDoS2019仅作为可选补充，不作为主要“跨数据集独立性”证据；
4. 暂不下载IoT-23原始pcap，除非准备投入额外的流特征提取和标签审计工作；
5. 不在没有许可证核验、哈希记录和统一协议的情况下把任何新增数据写入主结论。

## 8. 主要一手来源

- UNSW-NB15: <https://research.unsw.edu.au/projects/unsw-nb15-dataset>
- TON_IoT: <https://research.unsw.edu.au/projects/toniot-datasets>
- BoT-IoT: <https://research.unsw.edu.au/projects/bot-iot-dataset>
- CSE-CIC-IDS2018: <https://www.unb.ca/cic/datasets/ids-2018.html>
- CIC-DDoS2019: <https://www.unb.ca/cic/datasets/ddos-2019.html>
- IoT-23: <https://www.stratosphereips.org/datasets-iot23>
- Edge-IIoTset: <https://data.mendeley.com/datasets/2fjmq8rmn6/1>

> 注：本文档是数据集选择和实验设计备忘录，不替代各数据集官网的最新许可证、下载条款和版本说明。正式投稿时应把实际下载页面、哈希值和版本写入数据可用性声明与补充材料。
