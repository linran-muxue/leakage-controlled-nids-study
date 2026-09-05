# SCI 目标期刊与投稿资料核验（官方来源）

**核验日期：2026-09-05（Asia/Shanghai）**

## 1. 首选目标：Journal of Information Security and Applications（JISA）

- 期刊主页（Elsevier/ScienceDirect）：
  <https://www.sciencedirect.com/journal/journal-of-information-security-and-applications>
- 官方 Aims & Scope：
  <https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/about/aims-and-scope>
- 官方 Guide for Authors：
  <https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/publish/guide-for-authors>
- 官方投稿入口（Submit your paper）：
  <https://www.editorialmanager.com/jisa/default.aspx>

### 与本稿的匹配

本稿属于网络入侵检测、公开流量数据分析、特征选择、集成学习和可复现实验，主题上与 JISA 的信息安全应用方向相符。建议将稿件定位为：

> *A leakage-controlled and reproducible empirical study of feature selection and ensemble voting for network intrusion detection.*

标题、摘要和结论应强调可复现评测、数据审计、类别不平衡和跨数据集独立验证，不应把加权投票写成已被统计检验确认的显著优势。

### 正式投稿前需从 Guide for Authors 页面确认的项目

1. 可接受的文章类型（优先选择 Original Research Article；具体名称以投稿系统当前下拉选项为准）。
2. 摘要字数、关键词数量、图表上传方式和补充材料规则。
3. 参考文献样式是否采用编号制，以及 DOI 的显示规则。
4. 是否要求 Highlights、Graphical Abstract、CRediT 作者贡献和数据/代码声明。
5. 投稿系统要求的推荐审稿人、利益冲突声明、基金信息和作者 ORCID。
6. 订阅发表与 Gold Open Access 的可选许可及 APC；这些费用和许可应以投稿系统显示为准，不应写入论文正文作为固定承诺。

## 2. 次选目标：Computers & Security

- 期刊主页：
  <https://www.sciencedirect.com/journal/computers-and-security>
- 官方 Aims & Scope：
  <https://www.sciencedirect.com/journal/computers-and-security/about/aims-and-scope>
- 官方 Guide for Authors：
  <https://www.sciencedirect.com/journal/computers-and-security/publish/guide-for-authors>
- 官方投稿入口：
  <https://www.editorialmanager.com/cose/default.aspx>

该刊与网络安全和入侵检测高度匹配，但安全意义和现实威胁模型通常需要更充分的论证。若选择该刊，应在正文增加：威胁模型、攻击标签映射、数据覆盖限制、离线实验边界、自然分布结果、泄漏防控和统计不确定性；不要将平衡抽样子集结果表述为 CIC-IDS2017 全量性能，也不要宣称真实网关部署已经完成。

## 3. 投稿格式和 Word 模板策略

Elsevier 期刊的官方 Guide for Authors 页面是格式的最终依据。当前不应把第三方“期刊模板”或过期样稿当作官方模板。操作顺序如下：

1. 打开目标期刊的 Guide for Authors，下载页面提供的 Word/LaTeX 模板（若该刊不提供专用模板，则按其在线投稿格式准备单栏可编辑稿）。
2. 按官方要求设置标题页、摘要、关键词、正文层级、图题、表题、补充材料和参考文献。
3. 保留可编辑的图表和公式；不要只提交 PDF。
4. 将图、表、补充数据和代码说明按投稿系统要求分别上传，同时保留一个整合 Word/PDF 供审稿。
5. 投稿前在 Editorial Manager 中预览生成的审稿 PDF，逐项检查字体、分页、公式、图题和参考文献链接。

## 4. 本稿建议采用的英文参考文献规范

在目标期刊未明确要求前，使用**编号制顺序引用**：正文按首次出现顺序标注 `[1]`、`[2]`；参考文献表按编号排列。每条记录至少包含：作者、题名、期刊/会议、年份、卷(期)、页码或文章编号、DOI（如有）。

建议核验顺序：

1. 先从出版商官网、IEEE Xplore、ACM Digital Library、SpringerLink 或 DOI 官方解析页取得元数据；
2. 用 Crossref 查询 DOI 与题名、作者、年份是否一致；
3. 在正文中逐条使用引用，删除未被正文引用的条目；
4. 对数据集论文、随机森林、χ²/互信息/ANOVA、XGBoost/ExtraTrees、校准、数据泄漏、类别不平衡、开放集识别和概念漂移分别配置文献；
5. 不要仅为了增加数量加入与研究问题无关的文献。

投稿前还需检查 JISA 或 Computers & Security 的 Guide for Authors 是否要求“缩写期刊名”、是否显示 DOI、是否使用 et al.，以及参考文献管理软件导出的格式是否与在线系统一致。

## 5. 英文语言润色要求

当前稿件可先进行技术英语校对，再进行母语级润色。重点不是把结论写得更强，而是确保：

- 方法、数据划分和统计协议使用过去时，普遍事实使用现在时；
- `accuracy`、`macro-F1`、`balanced accuracy`、`log loss`、`Brier score`、`ECE` 等术语前后一致；
- `significantly improves` 仅在给出检验、效应量和校正后的显著性时使用；否则使用 `showed a small/non-significant difference`；
- 明确 `balanced research subset`、`natural-distribution sensitivity analysis` 和 `independent benchmark` 三种实验边界；
- 不把 `independent dataset` 写成跨数据集迁移成功；
- 不把离线延迟测量写成真实在线部署；
- 图表中的小数位、百分号和置信区间格式统一。

建议由作者在提交前进行一次人工母语审校，或使用具有学术编辑资质的英文润色服务；任何润色服务不得修改实验数字、数据划分或统计结论。

## 6. 数据集来源、许可证和可用性声明

论文应在“Data availability”或“Materials and methods”中分别记录每个数据集的官方来源、版本/发布日期、下载日期、文件 SHA-256、许可或使用条款。可使用以下保守声明模板，待人工核对具体条款后再提交：

```text
The CIC-IDS2017, NSL-KDD, and UNSW-NB15 datasets were obtained from their
respective public distribution pages. The exact source URLs, access dates,
file hashes, preprocessing scripts, random seeds, and derived audit records
are archived with this study. The datasets are used only for non-commercial,
offline research in accordance with the terms stated by their respective
providers. Redistribution of the original files is not intended.
```

项目现有数据源记录和哈希表可作为附件，但作者仍须逐项打开官方页面确认：

- CIC-IDS2017 官方页面和下载/使用条款；
- NSL-KDD 的实际镜像页面、镜像维护者和许可说明；
- UNSW-NB15 官方页面、下载版本和使用条款。

如果某个数据集没有明确的开源许可证，不要自行填写 MIT、CC BY 或其他许可证；应写成“terms of use specified by the provider”并在补充材料中保存网页或 PDF 证据。

## 7. 必须人工确认的投稿元数据

- 目标期刊最终选择（JISA 或 Computers & Security）；
- 该期刊投稿当日的 SCI/JCR 与学校认定情况（以 Clarivate 和学校目录为准）；
- 作者顺序、单位、通信作者、邮箱、ORCID、基金和利益冲突；
- 数据集官方条款和可否再分发派生文件；
- 参考文献 DOI 与正文引用逐条对应；
- 英文稿的最终语言质量和官方模板排版。

## 官方来源（均为第一方页面）

- JISA 主页与作者指南：<https://www.sciencedirect.com/journal/journal-of-information-security-and-applications>；<https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/publish/guide-for-authors>
- Computers & Security 主页与作者指南：<https://www.sciencedirect.com/journal/computers-and-security>；<https://www.sciencedirect.com/journal/computers-and-security/publish/guide-for-authors>
- Elsevier Researcher Academy（投稿、开放获取和出版政策教育页面）：<https://researcheracademy.elsevier.com/>
- Crossref DOI 元数据查询：<https://search.crossref.org/>
- Clarivate Master Journal List（索引状态核验）：<https://mjl.clarivate.com/>

