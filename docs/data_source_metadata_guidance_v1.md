# 数据集来源、版本与使用条款记录指南（v1）

本文档用于填写 `results_publication_final/external_data_metadata_template.json`。日期均以项目本地文件时间戳为**下载完成日期的代理证据**；正式投稿前应由作者打开来源页面核对并保存截图或 PDF 网页存档。

## 1. CIC-IDS2017

| 字段 | 建议填写值 | 证据/说明 |
|---|---|---|
| 官方 URL | `https://www.unb.ca/cic/datasets/ids-2017.html` | Canadian Institute for Cybersecurity（UNB）数据集页面；打开页面后保存网页截图/PDF。 |
| 下载日期 | `2026-09-02`（待人工确认） | `D:\\UserData\\27677\\Downloads\\MachineLearningCSV.zip` 的本地时间为 2026-09-02 22:40；这是下载完成时间的本地代理，不是服务器时间。 |
| 数据版本 | `CIC-IDS2017 / MachineLearningCSV archive (snapshot; no numeric release version stated)` | 项目使用的压缩包文件名为 `MachineLearningCSV.zip`；仓库中未发现官方数字版本号。不要填写臆造的 v1/v2。 |
| 许可证/使用条款 | `UNB CIC dataset terms; no SPDX license identifier verified (AUTHOR_TO_VERIFY)` | 公开可下载不等于 OSI/CC 许可证。请在官方页面查找 Terms of Use、Citation、Redistribution 或 License 文本并保存证据；若页面未给出明确许可证，正文应写“按官方页面使用条款用于研究，未声明统一 SPDX 许可证”。 |
| 原始压缩包 MD5 | `4f83860afbf29cac8163854095bf6cf7` | 来自 `MachineLearningCSV.md5`；该文件中的名称为 `MachineLearningCVE.zip`，与本地压缩包命名存在差异，需在补充材料中说明。 |
| 原始压缩包 SHA-256 | `c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928` | 已对本地 `MachineLearningCSV.zip` 计算。 |

建议正文表述：

> CIC-IDS2017 was obtained from the UNB Canadian Institute for Cybersecurity dataset page. We used the `MachineLearningCSV` archive available at the time of retrieval (2026-09-02 local timestamp); no numeric release version was stated on the source page. The archive checksum was recorded, and use was limited to research under the terms displayed on the source page.

## 2. NSL-KDD

| 字段 | 建议填写值 | 证据/说明 |
|---|---|---|
| 镜像 URL | `https://github.com/defcom17/NSL_KDD` | 这是项目实际使用的公开维护镜像，不应称为 NSL-KDD 官方机构数据页。原始数据集论文另行引用 Tavallaee 等。 |
| 访问/下载日期 | `2026-09-03`（待人工确认） | 本地 `E:\\论文\\data\\external\\NSL-KDD\\KDDTrain+.txt` 和 `KDDTest+.txt` 的时间戳为 2026-09-03 17:31；该日期是本地文件落盘时间代理。 |
| commit/快照 | `AUTHOR_TO_VERIFY` | 当前仓库只记录镜像名和文件哈希，未记录 commit。打开 GitHub 页面复制实际 commit SHA；若无法取得 commit，写“snapshot downloaded on 2026-09-03”并保存页面截图。 |
| 许可证/使用条款 | `No explicit license identifier verified for the mirror (AUTHOR_TO_VERIFY)` | GitHub 公开仓库不能自动推断许可证。检查仓库根目录的 LICENSE、README 和数据引用说明；若没有 LICENSE，正文应明确“镜像未声明标准开源许可证，按仓库说明仅作研究使用”。 |
| `KDDTrain+.txt` MD5/SHA-256 | `f5592a95d1d1428348dfa6ca9652a800` / `1b86d2f957b33082081bba410fe129b475efebcc13c9014c3f447c8271aadf95` | 来自 `results_nsl_kdd_fair_v2/raw_file_hashes_v4.json`。 |
| `KDDTest+.txt` MD5/SHA-256 | `7c6d1b1af246690766394920d6b4c751` / `fa46b0935342616aa83b7c2578db355b6a7aaabbc492248172c7a1e8b7ab8f84` | 来自 `results_nsl_kdd_fair_v2/raw_file_hashes_v4.json`。 |

建议正文表述：

> NSL-KDD was retrieved from the public `defcom17/NSL_KDD` repository (mirror snapshot; retrieval date recorded by the authors). Because the mirror does not provide a verified standard license identifier, the files are used under the repository/source instructions for non-commercial research, subject to author verification of the current LICENSE/README.

## 3. UNSW-NB15

| 字段 | 建议填写值 | 证据/说明 |
|---|---|---|
| 官方 URL | `https://research.unsw.edu.au/projects/unsw-nb15-dataset` | UNSW Canberra Cyber 官方项目页面；打开页面保存数据下载说明和使用条款。 |
| 下载日期 | `2026-09-04`（待人工确认） | 本地两个 CSV 时间戳均为 2026-09-04 23:44；这是下载完成时间的本地代理。 |
| 数据版本 | `UNSW-NB15 official training/testing CSV snapshot (no numeric release version stated)` | 使用文件名 `UNSW-NB15_training-set.csv` 和 `UNSW-NB15_testing-set.csv`；仓库未发现官方数字版本号。不要自行命名 v1/v2。 |
| 许可证/使用条款 | `UNSW Canberra Cyber project-page terms; no SPDX license identifier verified (AUTHOR_TO_VERIFY)` | 在官方页面查找 Data use、Citation、Terms、License 或 Redistribution 说明。若无明确许可证，正文只写“按官方项目页研究使用条款使用”，不要写 CC-BY/MIT 等未经核验的许可证。 |
| 训练集 SHA-256 | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` | 已记录在 `results_unsw_nb15_audit/audit_v2.json`。 |
| 测试集 SHA-256 | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` | 已记录在 `results_unsw_nb15_audit/audit_v2.json`。 |

建议正文表述：

> UNSW-NB15 was downloaded from the UNSW Canberra Cyber project page. The study uses the official training/testing CSV snapshot available on 2026-09-04 (local retrieval timestamp); no numeric release version was stated. SHA-256 checksums and the project-page usage terms were recorded.

## 4. 作者需要完成的人工核验

1. 打开三个来源页面，确认页面当前显示的 URL、页面标题、发布日期/版本和 Terms/License 文本。
2. 将页面打印为 PDF 或截图，保存到 `docs/source_records/`，文件名建议：
   - `cic_ids2017_source_2026-09-05.pdf`
   - `nsl_kdd_mirror_2026-09-05.pdf`
   - `unsw_nb15_source_2026-09-05.pdf`
3. 在模板中将 `AUTHOR_TO_VERIFY` 替换为页面实际内容；无法核验时保留该标记，并在论文中明确“不声明标准许可证/数字版本”。
4. 对本地文件重新计算哈希并与文档核对：

```powershell
Get-FileHash -Algorithm SHA256 "D:\UserData\27677\Downloads\MachineLearningCSV.zip"
Get-FileHash -Algorithm SHA256 "E:\论文\data\external\NSL-KDD\KDDTrain+.txt"
Get-FileHash -Algorithm SHA256 "E:\论文\data\external\NSL-KDD\KDDTest+.txt"
Get-FileHash -Algorithm SHA256 "E:\论文\data_external\UNSW-NB15\UNSW-NB15_training-set.csv"
Get-FileHash -Algorithm SHA256 "E:\论文\data_external\UNSW-NB15\UNSW-NB15_testing-set.csv"
```

## 5. 不应写入论文的表述

- “CIC-IDS2017 v1.0”或其他没有来源证据的数字版本；
- “NSL-KDD 官方官网”——当前使用的是 GitHub 镜像；
- “数据集采用 MIT/Apache/CC-BY 许可证”——除非来源页面明确写出；
- “下载日期”若没有保存证据却写成精确服务器时间；应说明为作者本地检索/下载日期；
- 把文件哈希当作许可证或版本号。

