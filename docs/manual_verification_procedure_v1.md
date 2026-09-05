# JISA 投稿指南与数据来源人工核验操作步骤

由于投稿网站和部分数据页面可能受浏览器安全策略、地区网络或登录状态影响，以下步骤由作者在本机浏览器执行。记录页面实际显示内容，不要根据搜索摘要或经验推断。

## 一、核对 JISA Guide for Authors

1. 打开：
   `https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/publish/guide-for-authors`
2. 使用浏览器的查找功能（Ctrl+F）依次搜索：
   - `Abstract`
   - `Highlights`
   - `Graphical abstract`
   - `Figures`
   - `Tables`
   - `Supplementary`
   - `References`
   - `Data availability`
   - `CRediT`
3. 记录页面实际要求：
   - 文章类型名称；
   - 摘要是否有字数限制及是否要求结构化摘要；
   - 关键词数量；
   - Highlights 是否必需、条数和每条字数限制；
   - Graphical Abstract 是否必需；
   - 图表是嵌入正文、单独上传还是两者都要；
   - 图片格式、分辨率和颜色要求；
   - 补充材料允许的文件类型；
   - 是否要求 Data Availability、CRediT、Declaration of Competing Interest、Funding 信息；
   - 参考文献格式及 DOI 显示规则。
4. 通过“打印 → 另存为 PDF”保存指南页面，建议文件名：
   `docs/source_records/jisa_guide_for_authors_2026-09-05.pdf`
5. 将实际要求填写到 `docs/jisa_submission_checklist_v1.md`，不要填写页面没有明确给出的数字。

## 二、保存 CIC-IDS2017 来源页面

1. 打开：
   `https://www.unb.ca/cic/datasets/ids-2017.html`
2. 搜索或查看：下载链接、Citation、Terms、License、Usage、Redistribution、Version。
3. 打印为 PDF，保存为：
   `docs/source_records/cic_ids2017_source_2026-09-05.pdf`
4. 若页面包含关键条款，再截取包含 URL、页面标题和条款的屏幕截图，保存为 PNG。
5. 只记录页面明确写出的版本和条款。如果没有标准许可证，填写：
   `No standard SPDX license identifier stated on the source page; used according to the provider's terms.`

## 三、保存 NSL-KDD 镜像页面

1. 打开：
   `https://github.com/defcom17/NSL_KDD`
2. 记录仓库名称、维护者、README 中的数据来源和使用说明。
3. 检查仓库根目录是否存在 `LICENSE` 文件：
   - 有：记录许可证名称和文件链接；
   - 无：填写 `No LICENSE file found in the checked repository snapshot.`
4. 点击仓库的提交记录，复制实际 commit SHA；如果无法确认，就保留：
   `Public mirror snapshot; exact commit not recorded.`
5. 打印仓库首页或 README 为 PDF，保存为：
   `docs/source_records/nsl_kdd_mirror_2026-09-05.pdf`

## 四、保存 UNSW-NB15 来源页面

1. 打开：
   `https://research.unsw.edu.au/projects/unsw-nb15-dataset`
2. 记录下载链接、数据集版本/发布日期、引用要求、Terms、License、Redistribution 信息。
3. 打印为 PDF，保存为：
   `docs/source_records/unsw_nb15_source_2026-09-05.pdf`
4. 如果页面没有数字版本或标准许可证，不要自行填写版本号、MIT、CC-BY 等名称。

## 五、更新元数据文件

打开：
`results_publication_final/external_data_metadata_template.json`

只修改以下字段：

- `retrieval_date`
- `version_or_snapshot`
- `license_or_terms`
- NSL-KDD 的 `commit_or_snapshot`

不要修改已经由本地文件计算得到的 SHA-256，除非重新计算后确认文件确实发生变化。

## 六、完成后运行的检查

在项目目录执行：

```powershell
Set-Location "C:\Users\27677\Documents\ChatGPT\论文"
Get-ChildItem "docs\source_records" -File
Get-Content "results_publication_final\external_data_metadata_template.json"
& "E:\论文\.venv\Scripts\python.exe" scripts\build_publication_manifest.py
& "E:\论文\.venv\Scripts\python.exe" -m pytest -q
```

把三份 PDF/截图的文件名、页面实际条款原文和 JISA 指南中确认的限制发给我，我再替你更新论文正文、英文稿、投稿清单和 Manifest。
