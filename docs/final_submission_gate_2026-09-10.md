# Final submission gate (2026-09-10)

> **状态说明（2026-09-17 更新）**
>
> 本文档是**历史记录**（写作日期见文件名或以正文标注为准），其中的版本号、稿件路径、引用条数与待办清单反映的是当时状态，可能已被后续轮次取代。
> 当前状态以 `重构版论文_v4_20260915/论文自查表.md`（66 项：62 通过 / 4 部分通过 / 0 缺失）与 `重构版论文_v4_20260915/遗漏问题审查报告.md`（第一至第十一轮）为准。
> 例如：发布标签已推进到 v1.10.0；正式稿件为 `English_SCI_Manuscript_v4` / `中文SCI论文_v4_重构版`；参考文献为 45 条且 DOI 已核验；补充材料为 `补充材料_S01_S26/`。

## Machine-verifiable status

- Canonical protocol written: `docs/canonical_protocol_v1.md`.
- Strict audit written: `docs/sci_strict_submission_audit_2026-09-10.md`.
- Figure/table crosswalk written: `docs/figure_table_crosswalk_v1.csv`.
- Reference verification matrix written: `docs/reference_verification_matrix_v1.csv`.
- Canonical CIC metrics, predictions, bootstrap intervals, paired tests, NSL-KDD metrics, UNSW metrics, calibration, latency, and robustness artifacts exist in the paths named by the crosswalk.

## Open blockers

1. Final manuscript must be regenerated from one canonical source after the crosswalk is adopted.
2. Main text must contain the core tables, not only prose and repository paths.
3. The supplementary package must copy or package v2-generated tables so that final evidence does not depend on a historical directory name.
4. Author identity, affiliation, postal address, corresponding author, ORCID, CRediT, and biography are not machine-inferable.
5. Funding and conflict-of-interest statements require author confirmation.
6. The official target-journal template and submission-day PDF preview require human review.
7. DOI landing pages and current data-provider terms require final manual opening before submission.

## Release rule

No statement that the paper is “SCI-ready” or “publishable” should be made until all open blockers are cleared and the regenerated DOCX/PDF passes visual inspection.
