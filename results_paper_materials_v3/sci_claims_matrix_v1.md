# SCI主张—证据矩阵

| 论文主张 | 证据文件 | 当前状态 | 允许表述 |
|---|---|---|---|
| 数据审计与训练集内预处理可复现 | `data_processed_cic_natural_v3b/preprocess_config.json`、`results_data_audit_cic_natural_v3b/data_processing_audit.json`、nested CV protocol | PASS | v3b 的物理范围审计、去重、划分和训练集内参数选择构成可复现流程 |
| χ²减少输入维度 | `results_publication_final/final_config.json`、metrics | PASS | 78维压缩至60维并基本保持当前任务性能 |
| χ²显著提升性能 | paired tests、bootstrap | FAIL | 不得宣称显著提升 |
| 加权RF优于普通RF | McNemar、permutation、weight ablation | FAIL | 当前数据下未观察到可检验增益 |
| CIC跨文件时间泛化 | file-external results | PARTIAL | 文件外覆盖/分布偏移风险审计 |
| UNSW外部验证完全独立 | cross-split audit | FAIL | 官方划分基准，并披露跨split重复影响 |
| NSL-KDD独立基准 | `results_nsl_kdd_fair_v2` | PARTIAL | 单seed独立公开数据集基准 |
| 真实网关部署 | offline latency only | FAIL | 受控CPU上的核心predict延迟 |
