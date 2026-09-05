# 面向 SCI 投稿的期刊匹配与官方要求核对（2026-09）

> 说明：期刊分区、影响因子、版面费和审稿周期会随年度与文章类型变化。投稿前必须在期刊官网的 **Guide for Authors / Open access / Journal insights** 页面再次核对。本文件不替代学校或学院的期刊认定目录。

## 一、候选期刊与适配度

| 期刊 | 出版社/官方投稿入口 | 主题范围与当前稿件匹配点 | 对当前稿件的主要风险 | 投稿策略 |
|---|---|---|---|---|
| Applied Soft Computing | Elsevier， [Aims & Scope](https://www.sciencedirect.com/journal/applied-soft-computing/about/aims-and-scope)，[Guide for Authors](https://www.sciencedirect.com/journal/applied-soft-computing/publish/guide-for-authors) | 接收软计算、机器学习及其实际应用；入侵检测、特征选择、集成学习属于主题交叉范围 | 该刊通常要求方法学新颖性、充分实验和可复现性；“χ²+RF”若仅为简单拼接，创新强度不足 | 需把贡献从“显著提升”改为可审计的特征选择/协议敏感性研究，并增加强基线、跨数据集及统计证据 |
| Computers & Security | Elsevier， [Aims & Scope](https://www.sciencedirect.com/journal/computers-and-security/about/aims-and-scope)，[Guide for Authors](https://www.sciencedirect.com/journal/computers-and-security/publish/guide-for-authors) | 网络与信息安全、入侵检测、网络流量分析高度匹配 | 安全期刊重视威胁模型、现实场景、可复现性与安全意义；平衡抽样子集和离线评测不能夸大为真实部署 | 明确威胁模型、标签映射、数据泄漏防控、文件级覆盖矩阵和自然分布结果；将校园网关仅作为潜在应用场景 |
| Journal of Information Security and Applications | Elsevier， [Aims & Scope](https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/about/aims-and-scope)，[Guide for Authors](https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/publish/guide-for-authors) | 面向信息安全应用研究，机器学习入侵检测与公开数据集验证匹配 | 仍需证明应用价值；仅在单一平衡子集上比较 Accuracy/Macro-F1 说服力有限 | 适合作为当前稿件的优先 SCI 目标之一，但必须保留自然分布、NSL-KDD 独立基准、延迟和鲁棒性实验 |
| Expert Systems with Applications | Elsevier， [Aims & Scope](https://www.sciencedirect.com/journal/expert-systems-with-applications/about/aims-and-scope)，[Guide for Authors](https://www.sciencedirect.com/journal/expert-systems-with-applications/publish/guide-for-authors) | 接收智能系统、机器学习与决策支持的应用；入侵检测可归入智能安全应用 | 竞争强、通常需要更强算法创新或大规模真实应用；简单加权投票及小样本平衡子集风险较高 | 不建议作为第一投递目标；除非补充更有实质性的集成学习机制、校准/代价敏感目标和多场景验证 |

## 二、各刊官网共同要求（以 Guide for Authors 为准）

1. **原创性与重复投稿声明**：稿件不得同时投往其他期刊；所有作者需同意投稿，利益冲突和基金信息应如实披露。
2. **结构化论文材料**：通常要求题目、摘要、关键词、正文、参考文献、图表及补充材料；具体格式以目标刊最新模板为准。
3. **数据与代码可复现性**：应说明数据来源、版本、下载地址、许可证、预处理、随机种子、超参数和评价协议；不能把公开数据的平衡子集写成全量结果。
4. **伦理与安全边界**：网络安全实验应说明仅使用公开数据和离线分析，不包含未授权扫描、渗透或真实攻击。
5. **开放获取**：上述 Elsevier 期刊通常提供订阅发表与 Gold Open Access 两种路径（具体许可协议和 APC 以投稿系统显示为准）。是否选择 OA 不等同于录用，也不改变同行评审标准。
6. **参考文献核验**：DOI、作者、题名、卷期、页码必须逐条核对；正文引用顺序应与参考文献表一致。

## 三、针对当前项目的 SCI 级技术补强

当前项目已有较好的审计材料，但以下事项直接影响 SCI 审稿结果：

- 将论文定位为“无泄漏特征选择与集成模型的可复现实证研究”，不要声称加权随机森林带来显著提升；现有配对检验显示加权收益不显著。
- 主结果必须同时报告平衡研究子集和自然分布敏感性结果，并明确 3,365 条样本是研究子集而非 CIC-IDS2017 全量。
- 保留 NSL-KDD 作为**独立公开数据集验证**，不要写成跨数据集迁移成功；补充 Balanced Accuracy、R2L/U2R 少数类指标。
- 把全特征 RF、χ²、互信息、ANOVA、ExtraTrees/SVM 等基线放在同一调参协议下，报告 Macro-F1、Balanced Accuracy、Log Loss、Brier、ECE、P50/P95/P99 和置信区间。
- 增加共享扰动鲁棒性、去重协议敏感性、特征入选频次和逐样本预测文件；说明固定随机种子只代表模型随机状态，重复划分才用于稳定性结论。
- 对严格时间外测试、真实在线网关和端到端吞吐保持边界表述；当前数据覆盖不足时，应作为局限性而非已证实结论。

## 四、推荐投稿顺序

1. **首选：Journal of Information Security and Applications** —— 主题匹配度高，适合将工作包装为可复现的信息安全应用研究。
2. **次选：Computers & Security** —— 若进一步强化威胁模型、跨场景验证和安全解释，可尝试；否则拒稿风险较高。
3. **备选：Applied Soft Computing** —— 需要更明确的软计算方法学贡献和更强算法对比。
4. **挑战目标：Expert Systems with Applications** —— 目前证据不足，不建议直接首投。

## 五、投稿前核对清单

- [ ] 在投稿当日重新确认 SCI/JCR、中科院分区及学校认定目录；不要引用过期分区截图。
- [ ] 下载目标期刊最新 Word/LaTeX 模板并逐项套用。
- [ ] 完成作者顺序、单位、通信作者、基金和利益冲突声明。
- [ ] 检查摘要、结论与统计结果一致，不出现“显著提升”“全量达到”“真实部署”等越界表述。
- [ ] 准备数据可用性声明、代码/配置可用性声明和补充材料压缩包。
- [ ] 由所有作者确认最终稿和投稿信，再提交在线系统。

### 官方来源汇总

- Applied Soft Computing: <https://www.sciencedirect.com/journal/applied-soft-computing/about/aims-and-scope>
- Computers & Security: <https://www.sciencedirect.com/journal/computers-and-security/about/aims-and-scope>
- Journal of Information Security and Applications: <https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/about/aims-and-scope>
- Expert Systems with Applications: <https://www.sciencedirect.com/journal/expert-systems-with-applications/about/aims-and-scope>
- Elsevier Researcher Academy（投稿与开放获取政策说明）: <https://researcheracademy.elsevier.com/> 

