# JISA 投稿准备清单（2026-09-05）

目标期刊：Journal of Information Security and Applications (JISA)

官方页面：

- 主页：https://www.sciencedirect.com/journal/journal-of-information-security-and-applications
- Guide for Authors：https://www.sciencedirect.com/journal/journal-of-information-security-and-applications/publish/guide-for-authors
- 投稿入口：https://www.editorialmanager.com/jisa/default.aspx

## 当前已准备

- 英文主稿 Markdown：`results_paper_materials_v3/english_sci_manuscript_v1.md`
- 英文可编辑 Word：`results_paper_materials_v3/english_sci_manuscript_v1.docx`
- 中文完整实验稿：`论文完整正文_v6_数据处理完善稿.docx`
- 数据和结果 Manifest：`results_publication_final/MANIFEST.json`
- 数据来源元数据：`results_publication_final/external_data_metadata_template.json`
- Cover letter 草稿：`results_paper_materials_v3/cover_letter_template_en.md`

## 投稿前必须核对

1. 在投稿当天重新打开 Guide for Authors，确认文章类型、摘要限制、关键词数量、图表上传方式、补充材料和是否需要 Highlights/Graphical Abstract。
2. 下载投稿系统当前提供的模板；若 JISA 不提供专用 Word 模板，则使用单栏可编辑稿并按系统预览结果调整。
3. 补齐真实作者、单位、通信作者、E-mail、ORCID、基金和利益冲突声明。
4. 对参考文献 DOI、作者、题名、卷期和页码逐条核对；当前英文稿采用作者—年份制，正文中的学术文献引用已与文献表对应，数据集来源单列为 Data references。
5. 保存三个数据来源页面的 PDF 或截图，并将实际许可证/Terms 原文写入 `external_data_metadata_template.json`；无明确许可证时保留“不声明标准 SPDX 许可证”。
6. 在 Editorial Manager 生成审稿 PDF 后，人工检查公式、图表分辨率、表题、参考文献链接和分页。

## 作者填写记录

- 文章类型：投稿系统当天确认；建议选择 Original Research Article（若系统名称不同，以系统为准）。
- 摘要限制：已按官方指南控制在 250 词以内。
- 关键词数量：已控制为 7 个。
- Highlights 要求：已生成 3–5 条、每条不超过 85 个字符的独立可编辑文件。
- Graphical Abstract 要求：已按鼓励提交项生成 PNG/PDF；投稿当天复核系统接受的文件类型。
- 图表上传要求：正文已包含可编辑表格；图件另存并按编号上传。
- 补充材料要求：已建立 S1–S14 索引；正文已引用相关补充材料。
- Data Availability/CRediT/Funding/Conflict of Interest 要求：已加入正文声明，作者信息和最终贡献归属需提交前确认。
- 参考文献格式与 DOI 规则：已采用作者—年份制并单列 Data references；投稿前逐条核验 DOI。
- JISA 指南证据：当前依据作者提供的官方指南文本；投稿前重新下载并归档官方页面/PDF。

## 已按指南落实（2026-09-05）

- 摘要：218 个英文单词，低于 250 词限制。
- 关键词：7 个英文关键词。
- Highlights：`results_paper_materials_v3/Highlights_JISA.docx`，4 条，每条少于 85 个字符。
- Graphical Abstract：`results_paper_materials_v3/Graphical_Abstract_JISA.png` 和 `.pdf`；PNG 为 1350×544 像素，使用可复核的流程和结果。
- Word：`results_paper_materials_v3/english_sci_manuscript_v1.docx`，可编辑单栏稿。
- 声明段落：Data/Code Availability、CRediT、Funding、Conflict of Interest、Acknowledgements、Generative AI 已置于参考文献之前。
- 自动审计：`JISA_AUDIT_OK abstract_words=218 keywords=7 paragraphs=92 tables=3`。
- 测试与编译：`66 passed`，`PY_COMPILE_OK`。
- 参考文献：英文稿已改为作者—年份制；正文不再保留数字引用标记。

## 表述边界

- 不把 3,365 条 CIC 数据写成全量性能。
- 不把 UNSW-NB15 写成无偏外部验证或跨数据集迁移成功。
- 不把加权随机森林写成显著优于等权投票。
- 不把离线延迟写成真实网关部署。
- 不把数据页面没有声明的内容推断为 MIT、CC-BY 或其他许可证。
