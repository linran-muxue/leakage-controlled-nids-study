# SCI 严格投稿审查报告（2026-09-10）

## 总判定

当前材料具备“可复现实验研究”的基础，但**不应直接按算法创新论文投稿**，也不能宣称已经达到 SCI 可发表状态。更准确的状态是：

> 数据和代码证据链部分可用；主张边界已开始收紧；稿件结构、图表主文呈现、版本统一和投稿元数据仍未闭合。

当前建议的论文定位是：

> *A leakage-controlled and reproducible evaluation framework for network intrusion detection under duplicate overlap, class imbalance, and open-set uncertainty.*

这比“加权随机森林显著提升的全新算法”与已有证据更一致。

## Blocker：投稿前必须解决

### B1. 主稿没有形成可核验的主结果表体系

英文 Markdown 只明确引用 `Table 1`、`Figure 1` 和 `Figure 2`，而完整的模型比较、类别指标、概率指标、鲁棒性和外部数据集结果主要留在 CSV 或补充材料目录中。SCI 审稿人不能只依赖代码仓库重建主结论。主文至少应包含：

- 主模型和统一基线的 Accuracy、Balanced Accuracy、Macro-F1、训练/推理耗时；
- χ²、互信息、ANOVA、全特征公平对照；
- seed=42 的类别级 Precision/Recall/F1 和混淆矩阵；
- 独立数据集结果的单独表格；
- 主要效应量和置信区间。

**处理要求：** 将主文压缩为 4–6 张核心表，其他逐样本结果放补充材料；每张表必须有唯一来源文件和生成配置。

### B2. 图表、补充材料和结果目录未完全采用单一规范

补充材料索引 S1–S14 中仍有多个路径指向 `results_paper_materials_v2`，而当前主结果目录为 `results_publication_final` 或 `results_additional_evidence_v4`。这会造成审稿人下载发布包后无法按正文引用复核。

**处理要求：** 建立图表交叉表，所有正文图表改为当前 canonical artifacts；旧目录只能作为历史结果，不得在最终稿中作为证据来源。

### B3. CIC 冲突计数的语义必须统一

`data_processed_audit_v4/dedup_audit.json` 同时给出：

- `cross_label_mismatch_rows = 4524`：标签不一致的重复记录行数；
- `cross_label_conflict_rows = 5048`：属于冲突特征向量组的全部记录行数；
- `conflicting_feature_hash_count = 133`：冲突唯一特征向量组数；
- `unique_rows_removed_for_conflicts = 133`：冲突组中移除的唯一向量数。

正文若只写“跨标签冲突 4,524 条”而不定义统计口径，会被误读为全部冲突组规模。必须在数据审计表和正文中同时报告四个字段，并明确后续删除的是 133 个冲突唯一向量。

### B4. “无泄漏”表述仍需降级为“训练变换无标签泄漏 + 数据集级清理已披露”

全局去重和冲突处理在最终划分前使用了整个可见 CIC 语料。它不是模型拟合参数泄漏，但也不等同于测试语料完全 untouched。正文应避免绝对化的“零泄漏”或“完全独立测试集”，并把该步骤定义为 dataset-level curation protocol。

### B5. 作者、单位、Funding 和期刊模板仍是硬阻断项

稿件不能在没有以下真实信息时进入正式投稿：作者单位、部门、通讯作者、邮政地址、ORCID（如有）、CRediT、Funding、Conflict of Interest、作者简介和目标期刊官方模板版式。Funding 只有在作者确认没有学校、导师、实验室、设备、奖学金或项目支持后，才能写 no funding。

## High：强烈建议修复

### H1. 算法创新证据不足

加权 RF 与等权 RF 的逐样本预测一致，McNemar p=1.0，重复划分也没有稳定优势；权重变异很小。该方法应作为 applicability/ablation，而不是核心算法突破。论文贡献应转为协议、审计、开放集和不确定性证据。

### H2. 统一配置与独立调参层级必须显式分开

主锁定配置是 `χ² Top-60 + 100 trees + min_samples_leaf=2`。独立调参结果、旧版 200/300 棵树实验和主锁定消融不能混在一个表中。每一张结果表需要标注 `locked`, `tuned`, `nested`, 或 `independent benchmark`。

### H3. 主实验样本外推范围有限

3,365 条记录是每类 673 条的平衡研究子集，不能写成 CIC-IDS2017 全量性能，不能用该结果支持校园网或真实网关部署结论。自然分布实验必须作为敏感性分析单列。

### H4. 文件级实验不是完整时间外泛化

CIC 原始文件的类别覆盖不完整，不能形成每个测试文件都包含五类的严格时间外协议。现有结果应写成 file/scene coverage audit 或 partial leave-file-out analysis，缺失类别必须标为 N/A。

### H5. 外部数据集只能写 independent benchmark

NSL-KDD 和 UNSW-NB15 标签体系与 CIC 五分类不同。结果不能合并平均，也不能表述为 cross-dataset transfer 或 universal generalization。

### H6. 统计推断层级不足以支持“显著优于”

CIC 重复分层比较的 Macro-F1 配对检验没有显示 χ² 优势；加权与等权无 discordant pair；嵌套 XGBoost 对 RF 的五折置换 p=0.0625。摘要、标题和结论不得写显著提升或 SOTA。

### H7. 概率指标和鲁棒性需要主文解释其适用范围

1% 高斯噪声导致约 30% 相对 Macro-F1 下降，说明模型对连续特征扰动敏感；5% 屏蔽较稳定。离线 predict 延迟不包含抓包、流构造、特征提取、网络 I/O 和告警处理，不能写成端到端网关延迟。

### H8. 参考文献数量和近年文献覆盖不足

当前主体约 15 条学术文献，经典文献占比高。需要增加 2021–2026 年关于数据泄漏、重复流、开放集识别、概率校准、概念漂移、边缘部署和可复现评估的直接研究，并逐条完成 DOI/卷期/页码核验。

## Medium：应修复

- 中文稿没有与英文稿对应的 Table/Figure/Supplementary 交叉引用体系；中英文应由同一 canonical table registry 生成。
- `results_publication_final/metrics_aggregate.csv` 是双层表头格式，投稿表格需要转为普通列名并明确 mean/std。
- NSL-KDD 的 R2L/U2R 类别级支持数、预测数量和归一化混淆矩阵应在主文或补充表中同时出现，不能只写一句“识别较差”。
- UNSW 的 overlap 是规范化特征键重叠，不等于完全重复流；正文必须使用 feature-key overlap，避免夸大为 duplicate leakage。
- 论文应给出研究问题对应的 estimand、比较方向、测试集、统计检验和效应量，而不是只罗列指标。
- 图题应包含数据协议、seed/重复次数、指标定义和是否为离线测量。

## Low：格式与表达

- 统一 `Macro-F1`、`macro-F1` 和 `Macro F1` 写法。
- 统一百分比和小数表示，不在同一表混用 95.78% 与 0.9578。
- 统一 `DoS/DDoS`、`Web Attack`、`R2L`、`U2R` 的大小写和连字符。
- 删除“完美数据梯度”“稳妥可中”“必过”等非学术表述。
- 将“校园网络适用”改为“受控离线特征推理场景下的潜在适用性”。

## 当前可确认的证据

- CIC 原始记录 2,830,743；映射后 2,671,766；有效 2,669,025；重复记录 239,101；平衡研究集 3,365。
- CIC 锁定 RF-χ²：Accuracy 0.9577558 ± 0.0011433，Macro-F1 0.9578600 ± 0.0011446。
- RF-χ² 与 weighted RF 在锁定测试行上预测一致，McNemar p=1.0。
- NSL-KDD ExtraTrees-χ²：Accuracy 0.7799414，Balanced Accuracy 0.5706523，Macro-F1 0.5990663。
- UNSW RF-all：Accuracy 0.7038171，Balanced Accuracy 0.5677376，Macro-F1 0.4823574。

## 不能由程序代替确认的事项

1. 作者单位、通讯作者、邮政地址和 ORCID；
2. Funding 是否确实为无；
3. 三个数据源当前页面的实际使用条款；
4. 投稿当天的官方 Word 模板和系统文件要求；
5. 最终 PDF 的分页、公式、图像清晰度和在线补充材料链接；
6. 每一条参考文献 DOI 页面的人工作者核验。

## 结论

在完成 B1–B5 之前，不建议投稿。即使完成这些阻断项，论文也应以“严格、可复现的评估协议研究”而不是“加权随机森林显著优于基线的算法论文”投稿。SCI 审稿能否接受仍取决于目标期刊、同行评审和作者提供的真实投稿信息，无法由代码测试保证。
