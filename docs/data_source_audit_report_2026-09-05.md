# 数据源全面审计报告（2026-09-05）

## 结论摘要

三套数据的本地文件、文件规模和 SHA-256 与实验审计结果一致；CIC-IDS2017 和 UNSW-NB15 的来源 URL 已与正文主要表述一致。NSL-KDD 存在一张截图对应 `Jehuty4949/NSL_KDD`、而实际下载记录对应 `defcom17/NSL_KDD` 的来源旁证差异，已按实际下载命令和哈希记录统一为 `defcom17/NSL_KDD`，并不把截图当作本地文件来源证明。

## 逐项核对

| 数据集 | 来源与本地文件 | 日期证据 | 版本/快照 | 许可证/条款 | 哈希状态 | 状态 |
|---|---|---|---|---|---|---|
| CIC-IDS2017 | 官方页面 `https://www.unb.ca/cic/datasets/ids-2017.html`；本地 `MachineLearningCSV.zip` 与 8 个 CSV | 2026-09-02 本地压缩包时间戳代理 | `MachineLearningCSV` archive snapshot；页面未显示数字版本 | 截图未显示 SPDX 许可证；正文应写按 UNB 页面条款研究使用 | MD5 `4f83860afbf29cac8163854095bf6cf7`；SHA-256 `c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928` | 已核对；条款仍应以页面存档为准 |
| NSL-KDD | 实际下载来源记录为 `https://github.com/defcom17/NSL_KDD`；本地 `KDDTrain+.txt`、`KDDTest+.txt` | 2026-09-03 本地文件时间戳代理 | mirror snapshot；精确 commit 未记录 | 未核验到标准许可证；不应称官方数据页 | KDDTrain+ SHA-256 `1b86d2f957b33082081bba410fe129b475efebcc13c9014c3f447c8271aadf95`；KDDTest+ SHA-256 `fa46b0935342616aa83b7c2578db355b6a7aaabbc492248172c7a1e8b7ab8f84` | 已统一；截图中的 `Jehuty4949` 仅作旁证 |
| UNSW-NB15 | 官方项目页 `https://research.unsw.edu.au/projects/unsw-nb15-dataset`；训练/测试 CSV | 2026-09-04 本地 CSV 时间戳代理 | official training/testing CSV snapshot；页面未显示数字版本 | 页面明确要求学术/公开使用者引用相关论文；未显示 SPDX 许可证 | 训练 SHA-256 `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`；测试 SHA-256 `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` | 已核对；应补充原始论文引用 |

## 实验属性而非来源许可

- CIC-IDS2017 主数据是经全局去重、冲突排除和五类平衡抽样得到的研究子集，不是全量数据。
- NSL-KDD 保留公开镜像中的 KDDTrain+/KDDTest+ 文件边界；项目引用应同时包含 Tavallaee 等人的原始论文。
- UNSW-NB15 官方训练/测试文件之间存在跨 split 特征键重复，已在 `results_unsw_nb15_audit/cross_split_overlap_audit.json` 中量化；这属于数据属性，不应隐藏。
- `id` 和 `label` 等字段已从 UNSW 预测特征中排除；`attack_cat` 为目标列。

## 尚未完全清除的人工核验项

1. CIC-IDS2017 页面没有在截图中呈现完整使用条款；正式投稿时建议保存包含 Terms/Citation 的页面 PDF。
2. UNSW 页面截图显示了引用要求，但没有展示标准许可证；正文不要写 CC-BY、MIT 等未经证实的许可证。
3. NSL-KDD 精确 commit 未记录；若无法从原始下载环境恢复，应诚实写 `mirror snapshot`，不伪造 commit SHA。

## 可复现性判定

当前来源链达到“文件可定位、哈希可复核、处理过程可追溯”的水平；达到完全可复现还需要读者获得相同镜像快照和明确的页面条款存档。上述限制应在 Data Availability/Limitations 中说明。
