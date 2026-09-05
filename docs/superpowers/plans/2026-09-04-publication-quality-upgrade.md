# 期刊投稿质量升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在统一、无泄漏的实验口径下补齐概率质量、鲁棒性、延迟、统计效应量和论文证据链，并生成可供《计算机系统应用》进一步套用模板的完整稿件。

**Architecture:** 以 `data_processed_audit_v4` 和 `results_publication_final` 为主数据与主结果源；以 `results_additional_evidence_v4` 承载概率、共享扰动和延迟证据；由材料生成脚本统一产生表格、图和第四章，再由 Word 构建脚本输出稿件。所有新增数字必须来自 CSV/JSON，不手工编造。

**Tech Stack:** Python 3.11、pandas、scikit-learn、matplotlib、seaborn、python-docx、pytest。

## Global Constraints

- 主任务限定为 CIC-IDS2017 五分类平衡研究子集，不能表述为全量数据性能。
- 最终模型配置统一为 χ² Top-60、100 棵树、`min_samples_leaf=2`；若结果目录另有配置，正文必须显式区分。
- NSL-KDD 仅作为独立公开基准，不宣称跨数据集迁移。
- 加权随机森林未通过显著性检验时，不得写成显著提升。
- 离线 predict 延迟不等同于真实网关部署性能。

### Task 1: 生成并审计新增实验材料

**Files:**
- Modify: `scripts/run_additional_evidence_v4.py`
- Modify: `src/additional_metrics.py`
- Test: `tests/test_additional_metrics.py`
- Test: `tests/test_additional_evidence_v4.py`

- [ ] 确认新增实验输出包含四种特征方法、逐样本概率、Log Loss、宏平均 Brier、校准点、共享扰动、P50/P95/P99。
- [ ] 增加 ECE/MCE、相对下降幅度、效应量和 Holm 校正所需的可复用函数及测试。
- [ ] 使用统一 v4 数据和最终模型配置重跑脚本。

### Task 2: 扩展论文图表与正文证据

**Files:**
- Modify: `scripts/generate_v2_paper_materials.py`
- Modify: `results_paper_materials_v2/full_paper_body_v3.md`
- Create/Modify: `results_paper_materials_v2/tables/*`
- Create/Modify: `results_paper_materials_v2/figures/*`

- [ ] 加入研究问题和可证伪假设。
- [ ] 生成数据来源/版本/校验信息表、泄漏防控流程图、归一化混淆矩阵、特征入选频次图。
- [ ] 将 ECE/MCE、P99、相对性能下降、效应量/Holm、NSL-KDD 每类预测数量写入表格和第四章。
- [ ] 统一正文、表题、图题和附录编号，压缩正文核心表并将细节留在附录。

### Task 3: 重建稿件并进行质量闸门

**Files:**
- Modify: `scripts/build_complete_paper_v3.py`
- Generate: `论文完整正文_v3_无泄漏实验统一稿.docx`

- [ ] 重新生成 Markdown、图表和 Word。
- [ ] 检查 Word 中不存在旧目录名、旧数字和“显著提升/全量数据/真实部署”等越界表述。
- [ ] 运行完整 pytest 和 `py_compile`，保存最终 MANIFEST。

## Verification Commands

```powershell
& "E:\论文\.venv\Scripts\python.exe" -m pytest -q
$files = Get-ChildItem -LiteralPath src,scripts,tests -Filter "*.py" -Recurse | ForEach-Object { $_.FullName }
& "E:\论文\.venv\Scripts\python.exe" -m py_compile $files
```
