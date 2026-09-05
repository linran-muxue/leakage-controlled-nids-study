# SCI级网络入侵检测论文升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前论文从“中文期刊可复现实验稿”升级为面向 SCI 信息安全/机器学习应用期刊的英文实证研究稿，重点补齐方法创新边界、公平基线、嵌套验证、自然分布评估、统计证据和可复现材料。

**Architecture:** 以 `data_processed_audit_v4` 作为 CIC-IDS2017 的审计后源数据，以 `data_external_nsl_kdd_processed_v2` 作为 NSL-KDD 独立基准。新增实验全部使用统一配置文件和可追溯 CSV/JSON 输出；论文正文只引用由脚本生成的结果表，避免手工改数字。模型贡献定位为“leakage-controlled reproducible evaluation and feature-selection applicability analysis”，不再把加权投票描述为已证实的强算法创新。

**Tech Stack:** Python 3.11、pandas、scikit-learn、XGBoost 或 LightGBM、SciPy、statsmodels、matplotlib、seaborn、python-docx、pytest。

## Global Constraints

- CIC-IDS2017 的 3,365 条样本必须称为“平衡研究子集”，不得称为全量数据结果。
- 主模型当前配置为 χ² Top-60、100 棵树、`min_samples_leaf=2`；升级实验若改变配置，必须单独命名并记录。
- NSL-KDD 仅作为独立公开数据集基准，不宣称跨数据集迁移或泛化成功。
- 加权随机森林与等权随机森林逐样本一致、显著性检验未显示优势时，不得写“显著提升”。
- 固定三个 seed 只表示模型随机状态；泛化稳定性必须来自外层重复划分或嵌套交叉验证。
- 真实校园网关、在线流量和端到端吞吐未测量时，只能报告离线 `predict` 延迟。
- 所有新增实验必须保存逐样本预测、预测概率、配置、随机种子和运行环境。

---

### Task 1: 固化 SCI 研究问题、威胁模型和贡献边界

**Files:**
- Modify: `results_paper_materials_v2/full_paper_body_v3.md`
- Create: `docs/sci_scope_and_claims.md`
- Modify: `scripts/generate_v2_paper_materials.py`

**Interfaces:**
- Consumes: `results_publication_final/`, `results_additional_evidence_v4/`, `docs/sci_journal_target_research_2026-09.md`
- Produces: SCI英文题目、摘要、研究问题、假设、威胁模型、贡献声明和禁用表述清单。

- [ ] 将题目改为：`Leakage-Controlled Feature Selection and Random-Forest Ensembles for Network Intrusion Detection: A Reproducible Multi-Dataset Study`。
- [ ] 在引言中明确三个研究问题：特征选择的性能—维度权衡、投票策略适用性、协议/分布变化对结果的影响。
- [ ] 在方法章节加入威胁模型：攻击者目标、检测器输入为流统计特征、研究不执行主动扫描/渗透、标签来自公开数据集。
- [ ] 将“创新点”改写为三项可验证贡献：泄漏控制流程、统一比较协议、跨数据集独立证据链。
- [ ] 删除或改写“显著提升”“SOTA”“真实网关部署”“跨数据集迁移成功”等表述。

### Task 2: 建立统一调参和强基线实验

**Files:**
- Create: `src/sci_nested_evaluation.py`
- Create: `scripts/run_sci_baselines_v1.py`
- Create: `results_sci_baselines_v1/`
- Test: `tests/test_sci_nested_evaluation.py`

**Interfaces:**
- Consumes: `data_processed_audit_v4/{train,validation,test}.csv`
- Produces: 同一外层划分下的 RF、χ²-RF、全特征RF、ExtraTrees、XGBoost/LightGBM、SVM、决策树的配置、预测、概率和指标。

- [ ] 统一基线搜索预算：每个模型使用相同外层划分、相同内层折数、相同候选配置数量上限。
- [ ] 至少加入一个强梯度提升基线（XGBoost 或 LightGBM），记录版本和 CPU 线程数。
- [ ] 所有模型输出 Accuracy、Balanced Accuracy、Macro-F1、Macro-Precision、Macro-Recall、Log Loss、宏平均 Brier 和 ECE。
- [ ] 对每个外层测试折保存 `predictions_<model>_fold<id>.csv` 和 `probabilities_<model>_fold<id>.csv`。
- [ ] 编写测试确认测试折未参与特征选择、归一化器拟合和超参数选择。

### Task 3: 实施嵌套交叉验证和重复外层划分

**Files:**
- Modify: `src/sci_nested_evaluation.py`
- Create: `scripts/run_nested_cv_v1.py`
- Create: `results_nested_cv_v1/`

**Interfaces:**
- Consumes: 审计后的 CIC 五分类研究子集和统一基线配置。
- Produces: 外层 10 次重复分层划分或 5×2 外层划分的逐折结果、均值、95% CI 和配对差异。

- [ ] 外层使用分层划分，内层使用 5 折交叉验证选择 `k`、树数、叶节点和模型专属参数。
- [ ] 每个外层折重新拟合缺失值处理、归一化和特征选择。
- [ ] 报告外层 Macro-F1 的均值、标准差、百分位 CI，以及 RF 与强基线的配对差值。
- [ ] 将现有固定测试集结果降级为补充结果，不与嵌套CV结果混称。

### Task 4: 重新定义自然分布与抽样敏感性分析

**Files:**
- Create: `scripts/run_distribution_sensitivity_v1.py`
- Create: `results_distribution_sensitivity_v1/`
- Modify: `scripts/generate_v2_paper_materials.py`

**Interfaces:**
- Consumes: `data_processed_audit_v4/`、不平衡数据准备结果。
- Produces: 不同样本规模和类别先验下的类别级指标、Macro-F1、Balanced Accuracy、预测数量和置信区间。

- [ ] 至少比较平衡子集、每类上限20,000的不平衡集和一个中等规模分层子集。
- [ ] 对每个分布报告真实支持数、预测数量、混淆矩阵、每类 Precision/Recall/F1。
- [ ] 增加样本规模曲线，展示性能随训练样本量变化，而不是只报告单点数字。
- [ ] 正文明确类别先验变化会导致 Accuracy 与 Macro-F1 分离。

### Task 5: 完善统计检验和多重比较控制

**Files:**
- Create: `src/sci_statistics.py`
- Create: `scripts/run_sci_statistics_v1.py`
- Create: `results_sci_statistics_v1/`
- Test: `tests/test_sci_statistics.py`

**Interfaces:**
- Consumes: 外层逐折 Macro-F1、逐样本预测和概率。
- Produces: 配对置换检验、McNemar、Bootstrap CI、Cliff效应量、Holm校正后的p值。

- [ ] 预先定义比较族：χ²-RF vs 全特征RF、χ²-RF vs ExtraTrees、χ²-RF vs XGBoost/LightGBM、加权RF vs 等权RF。
- [ ] 对外层折 Macro-F1 使用配对置换检验，并报告差值 CI 和效应量。
- [ ] 对同一测试样本的分类错误使用 McNemar 检验；比较数量增加后执行 Holm 校正。
- [ ] 在表格中同时给出未经校正和校正后的 p 值，并说明检验假设和方向。

### Task 6: 补充可解释性和误差分析

**Files:**
- Create: `scripts/run_error_analysis_v1.py`
- Create: `results_error_analysis_v1/`
- Modify: `scripts/generate_v2_paper_materials.py`

**Interfaces:**
- Consumes: 主模型逐样本预测概率、来源文件字段、类别标签。
- Produces: 类别混淆对、置信度分布、来源文件误差统计、Top特征稳定性和可解释性图。

- [ ] 按真实类别分析最高置信度错误样本和主要混淆对。
- [ ] 按原始文件统计错误率，避免把文件/日期耦合误读成算法泛化。
- [ ] 保存 Top-20 特征的选择频次、平均排名和跨折 Jaccard 相似度。
- [ ] 若使用 SHAP，只在外层训练折拟合解释器，并将其定位为描述性分析而非因果解释。

### Task 7: NSL-KDD独立基准的SCI级报告

**Files:**
- Modify: `scripts/run_nsl_kdd_fair_v2.py`
- Create: `results_nsl_kdd_sci_v1/`
- Modify: `scripts/generate_v2_paper_materials.py`

**Interfaces:**
- Consumes: `data/external/NSL-KDD/`、现有处理脚本和哈希文件。
- Produces: 官方划分、多 seed 或重复训练、Balanced Accuracy、Macro-F1、每类支持/预测数量、R2L/U2R CI。

- [ ] 保持 KDDTrain+/KDDTest+ 官方划分，不从测试集重新抽样调参。
- [ ] 明确三种离散特征编码、未知类别处理和 χ²特征选择步骤。
- [ ] 报告 R2L/U2R 的支持数、召回率、F1、被误判为 Normal 的比例和 Bootstrap CI。
- [ ] 正文只称“独立基准”，不称“跨数据集迁移验证”。

### Task 8: 英文稿、图表和投稿包

**Files:**
- Create: `paper/sci_manuscript_v1.md`
- Create: `paper/supplementary_materials_manifest.md`
- Create: `scripts/build_sci_manuscript_v1.py`
- Generate: `paper/SCI_manuscript_v1.docx`

**Interfaces:**
- Consumes: Tasks 1–7 的结果 CSV/JSON/PNG。
- Produces: 英文主稿、补充材料清单、投稿信初稿、数据/代码可用性声明。

- [ ] 按目标期刊的 Guide for Authors 设置摘要、Highlights、图表、参考文献和数据声明。
- [ ] 正文主表压缩为：数据与协议、主性能、自然分布、独立NSL-KDD、统计检验、部署/鲁棒性；其余放补充材料。
- [ ] 全文统一术语：balanced subset、natural-distribution sensitivity、independent benchmark、nested evaluation。
- [ ] 参考文献扩充至近五年为主，并逐条核验 DOI、作者、卷期和页码。
- [ ] 生成投稿信，明确本文不是 SOTA 声称，而是 leakage-controlled reproducible empirical study。

### Task 9: 最终验证和投稿前门禁

**Files:**
- Modify: `scripts/build_publication_manifest.py`
- Create: `scripts/check_sci_submission_readiness.py`
- Test: `tests/test_sci_submission_readiness.py`

**Interfaces:**
- Consumes: 所有 SCI 主稿、实验结果和配置文件。
- Produces: `results_sci_submission_readiness/report.json` 和最终 manifest。

- [ ] 检查所有正文数字均能在 CSV/JSON 中找到来源。
- [ ] 检查未出现“显著提升”“全量性能”“真实部署已完成”“跨数据集迁移成功”等越界表述。
- [ ] 检查所有预测文件、概率文件、配置文件和哈希文件均存在。
- [ ] 运行：

```powershell
& "E:\论文\.venv\Scripts\python.exe" -m pytest -q
$files = Get-ChildItem -LiteralPath src,scripts,tests -Filter "*.py" -Recurse | ForEach-Object { $_.FullName }
& "E:\论文\.venv\Scripts\python.exe" -m py_compile $files
```

- [ ] 只有在测试、编译、结果来源和投稿格式检查全部通过后，才将稿件标记为“SCI投稿候选稿”。

## 当前执行顺序

先执行 Task 1 和 Task 2，确定 SCI 论文定位并补齐 XGBoost/LightGBM 强基线；再执行 Task 3 和 Task 5，解决嵌套验证与统计有效性；随后执行 Task 4、Task 6、Task 7；最后执行 Task 8 和 Task 9。20 次重复划分和第三个数据集属于 Task 3/Task 7 完成后的可选扩展，不应先于核心缺口修复。
