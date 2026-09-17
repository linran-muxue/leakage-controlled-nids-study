# Public code release plan

> **状态说明（2026-09-17 更新）**
>
> 本文档是**历史记录**（写作日期见文件名或以正文标注为准），其中的版本号、稿件路径、引用条数与待办清单反映的是当时状态，可能已被后续轮次取代。
> 当前状态以 `重构版论文_v4_20260915/论文自查表.md`（66 项：62 通过 / 4 部分通过 / 0 缺失）与 `重构版论文_v4_20260915/遗漏问题审查报告.md`（第一至第十一轮）为准。
> 例如：发布标签已推进到 v1.10.0；正式稿件为 `English_SCI_Manuscript_v4` / `中文SCI论文_v4_重构版`；参考文献为 45 条且 DOI 已核验；补充材料为 `补充材料_S01_S26/`。

The public repository URL supplied by the author is https://github.com/linran-muxue/leakage-controlled-nids-study. The local project is prepared for a selective reproducibility release; the original datasets remain excluded.

## Files safe to publish

- `src/`
- `scripts/`
- `tests/`
- `docs/`
- `results_paper_materials_v3/` (manuscript-supporting text, tables, figures, Highlights, Graphical Abstract)
- `results_publication_final/` (derived results, hashes, configuration, Manifest)
- `results_nsl_kdd_fair_v2/` (derived NSL-KDD results only)
- `results_unsw_nb15_independent_v4/` and related derived result summaries
- `README.md`, `LICENSE`, `requirements-direct.txt`, `requirements-lock.txt`

## Files not to publish

- Original CIC-IDS2017, NSL-KDD, and UNSW-NB15 files.
- PCAP files, ZIP archives, and local virtual environments.
- Any file containing personal author information before the title page is finalized.

## Author actions required

1. Confirm that the supplied repository is owned by the author and is public.
2. Upload the safe files listed above, or allow the local Git push from the project directory.
3. Create a tagged release or archive and record the commit SHA/DOI in `results_publication_final/MANIFEST.json`.

The manuscript cites the supplied public URL and release tag `v1.0.2`. The tag should be created after the final submission-material commit and pushed to GitHub.
