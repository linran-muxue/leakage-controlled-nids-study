# 现代语料阶梯（2026-10-03 批次）脚本索引

这一批把「主语料换成现代语料」的验证从单点扩到规模档位、分布位移与机制分解。
全部脚本保留在 `scripts/` 根目录（论文与扩展报告按路径引用它们，移动会打断
`check_cited_paths_v1.py` 的引用检查），这里只做索引。

## 取数与准备

| 脚本 | 作用 |
|---|---|
| `fetch_2025_corpora_v1.py` | 下载 2025 年语料（UAVIDS-2025、GeNIS、IDS2025） |
| `fetch_2026_corpora_v1.py` | 下载 2026 年语料（CTU-IDSEVAL-6、6TiSCHSet-2026、RTN） |
| `fetch_gotham2025_v1.py` | 分块续传 Gotham-2025（Zenodo 14502760，24 GB）并校验 MD5 |
| `prepare_2026_corpora_v1.py` | 处理 2026 语料，支持 `--processed-dir/--audit-dir` 与截断档位 |
| `prepare_gotham2025_v1.py` | 处理 Gotham-2025，支持每类 20 万档与不限上限全档 |
| `prepare_grouped_corpus_v1.py` | 构造逐设备/逐运行分组语料（留出用，含 `all.csv`） |
| `proxy_node_switch_v1.py` | Clash 命名管道切节点，长下载断流时用 |

## 训练与评测

| 脚本 | 作用 |
|---|---|
| `run_native_label_benchmark_v1.py` | 主评测器：门控、同成员等权融合、两个单视图对照，十种子；`--resume` 种子级续跑、`--n-jobs` 与内存守卫、`JOBLIB_TEMP_FOLDER` |
| `run_source_holdout_v1.py` | 留一来源评测（Gotham 逐设备、6TiSCHSet 逐运行），分层且每类至少两行进入校准确认集 |
| `run_feature_budget_sweep_v1.py` | CIC-IoT-2023 特征预算扫描 k=8/16/32/60，逐档写 `results_rccf_cic_iot2023_k*/` |
| `analyze_margin_bound_v5.py` | 边距上界：逐行判定「改判能否翻转 argmax」 |
| `analyze_weight_mechanism.py` | 树权重分布、概率 L1、预测不一致计数 |
| `run_diversity_suite_v5.py` | 多样性剂量—反应（五组专家配置 × 三种子，含互斥特征视图） |

## 编排与监控

| 脚本 | 作用 |
|---|---|
| `run_modern_ladder_queue_v1.py` | 幂等总队列：B/C 档 → Gotham 全档 → 留出 → 补档 → 预算扫描 → 机制套件 → 等价性重算 |
| `run_modern_ladder_phase2_v1.py` | 等待 Gotham 全档、进程消失时以 resume 模式续跑；Gotham 未完成时不启动后续步骤 |
| `launch_gotham_full_run_v1.py` | 只重启 Gotham 全档（跳过 40 分钟准备），带重复写入守卫 |
| `sync_desktop_delivery_v1.py` | 桌面交付目录同步 + 关键文件 SHA-256 校验 |

## 汇总与写稿

| 脚本 | 作用 |
|---|---|
| `analyse_modern_replication_v1.py` | 从逐样本预测重算跨语料配对差与合并等价性 |
| `analyse_modern_evidence_v1.py` | 次生指标（门控 ECE、改判标签数、预测一致率） |
| `add_modern_ladder_to_paper_v1.py` | 断言锚点写稿：扩展报告新增三节、§5.8/§5.9/§6.5、数据来源总表、清单补齐 |
| `fix_extension_metrics_v1.py` | 逐种子指标文件与 `test_samples_mean` 的记账修复（含阶梯全部结果目录） |

## 运行顺序（可直接照抄）

```powershell
& $py scripts\run_modern_ladder_queue_v1.py          # 幂等；中断后重跑即可
& $py scripts\run_modern_ladder_phase2_v1.py         # 守护：等 Gotham 全档并补齐后续步骤
& $py scripts\add_modern_ladder_to_paper_v1.py       # 把结果写进论文与报告（幂等）
& $py scripts\build_restructured_manuscript_v4.py --only all
& $py scripts\convert_equations_word_v41.py
& $py scripts\build_experiment_record_v1.py
& $py scripts\fix_deliverable_counts_v1.py
& $py scripts\build_material_index_v1.py
& $py scripts\build_publication_manifest.py
& $py scripts\package_submission_bundle_v18.py
& $py scripts\verify_all_v8.py                       # 53 项闸门
& $py scripts\sync_desktop_delivery_v1.py
```
