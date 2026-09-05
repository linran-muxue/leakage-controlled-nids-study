# SCI Publication Upgrade Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将现有中文实验稿升级为证据边界清晰、可复现、适合SCI初投的中英文材料包。

**Architecture:** 以`data_processed_audit_v4`、`results_publication_final`、`results_nsl_kdd_fair_v2`和`results_unsw_nb15_*`为证据源；先修正来源与结论边界，再生成英文稿件和投稿附属材料。所有数字只从已有CSV/JSON读取，不手工编造。

**Tech Stack:** Python 3.11、python-docx、pandas、scikit-learn、现有审计/生成脚本。

## Global Constraints

- 不把CIC平衡研究子集表述为全量数据性能。
- 不把加权随机森林表述为显著优于普通随机森林。
- NSL-KDD和UNSW-NB15仅作独立标签体系基准，不宣称跨数据集迁移成功。
- 未核验许可证、数字版本或完整commit时必须明确写“未核验/快照”。
- 不改动原始数据文件，不进行网络攻击或扫描。

### Task 1: 统一数据来源和实验边界

**Files:**
- Modify: `results_publication_final/external_data_metadata_template.json`
- Modify: `results_paper_materials_v3/full_paper_body_v6_data_processing.md`
- Create: `results_paper_materials_v3/tables/table_data_source_provenance_v1.csv`
- Create: `docs/data_source_audit_report_2026-09-05.md`

- [ ] 核对三个数据集URL、日期代理、快照、许可证状态和SHA-256。
- [ ] 将NSL-KDD实际来源统一为`defcom17/NSL_KDD`，保留精确commit未记录的边界。
- [ ] 在正文说明CIC为3,365条平衡研究子集，UNSW存在跨split重复，文件外实验不是完整五分类时间泛化。

### Task 2: 统计证据和外部基准

**Files:**
- Use: `results_publication_final/*`
- Use: `results_repeated_splits_v3/*`
- Use: `results_nsl_kdd_fair_v2/*`
- Use: `results_open_set_matrix_v2/*`
- Use: `results_unsw_nb15_cross_split_sensitivity_v1/*`

- [ ] 把已有Macro-F1、Bootstrap、重复划分、开放集和UNSW敏感性结果整理为主文可引用的证据表。
- [ ] 明确单seed NSL-KDD与三seed UNSW的证据等级不同。
- [ ] 将统计检验解释限定为对应指标，不把Accuracy检验转写为Macro-F1显著性。

### Task 3: 生成英文SCI稿件

**Files:**
- Create: `results_paper_materials_v3/english_sci_manuscript_v1.md`
- Create: `results_paper_materials_v3/english_sci_manuscript_v1.docx`
- Create: `results_paper_materials_v3/cover_letter_template_en.md`

- [ ] 英文稿包含Title、Abstract、Introduction、Methods、Experimental Protocol、Results、Limitations、Data/Code Availability和Conclusion。
- [ ] 所有核心数字从现有结果文件读取并注明研究子集/独立基准边界。
- [ ] 不写无法由现有结果支持的“significant improvement”“real-time deployment”或“cross-dataset transfer”。

### Task 4: 最终质量门禁

- [ ] 运行`audit_manuscript_claims_v1.py`。
- [ ] 运行Python编译检查。
- [ ] 运行完整pytest。
- [ ] 检查Word文件存在、JSON有效、MANIFEST哈希一致。

