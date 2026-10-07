"""Build the Chinese-named submission bundle from the released artifacts.
Everything inside the archive is copied from the canonical locations recorded
in the self-check table and the publication manifest, so the bundle cannot
disagree with the paper. The archive also carries its own checksum list.
"""
from __future__ import annotations
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from supplementary_paths_v1 import supplementary_bundle
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUILD = ROOT / "submission_package"
TAG = "v1.11.0"
NAME = f"论文投稿包_{TAG}"
# each entry is (folder inside the archive, root used to derive relative paths, files)
SUPPLEMENTARY = supplementary_bundle(BASE)
LAYOUT: list[tuple[str, Path, list[Path]]] = [
    ("01_正式稿件", BASE, [BASE / "English_SCI_Manuscript_v4.docx",
                           BASE / "English_SCI_Manuscript_v4.md",
                           BASE / "中文SCI论文_v4_重构版.docx",
                           BASE / "中文SCI论文_v4_重构版.md"]),
    ("02_投稿文件", BASE, [BASE / "Highlights_v4.docx",
                           BASE / "Highlights_v4.md",
                           BASE / "Cover_Letter_JISA_v4.docx",
                           BASE / "Cover_Letter_JISA_v4.md",
                           BASE / "Graphical_Abstract_v4.png",
                           BASE / "Graphical_Abstract_v4.pdf"]),
    ("03_图片/英文版", BASE / "figures_en", sorted((BASE / "figures_en").glob("*.png"))),
    ("03_图片/中文版", BASE / "figures", sorted((BASE / "figures").glob("*.png"))),
    ("04_补充材料", SUPPLEMENTARY, sorted(p for p in SUPPLEMENTARY.rglob("*") if p.is_file())),
    ("05_自查与审查", BASE, [BASE / "论文自查表.docx", BASE / "论文自查表.md",
                             BASE / "遗漏问题审查报告.docx", BASE / "遗漏问题审查报告.md"]),
    ("06_研究与写作方案", BASE, [BASE / "论文结构诊断与重构方案.docx", BASE / "论文结构诊断与重构方案.md",
                                 BASE / "研究缺口审计与优先级清单.docx", BASE / "研究缺口审计与优先级清单.md",
                                 BASE / "P0_P1执行手册.docx", BASE / "P0_P1执行手册.md",
                                 ]),
    # the work log travels as Markdown and as Word, like the other working docs
    ("06_研究与写作方案", BASE, [BASE / "工作日志_论文项目.md",
                                 BASE / "工作日志_论文项目.docx"]),
    ("07_复现材料", ROOT, [ROOT / "results_publication_final" / "MANIFEST.json",
                           ROOT / "README.md", ROOT / "CITATION.cff",
                           ROOT / "requirements-lock.txt"]),
    ("07_复现材料", BASE, [BASE / "数据与资料来源总表.md", BASE / "数据与资料来源总表.docx",
                           BASE / "公式来源与核验.md", BASE / "公式来源与核验.docx",
                           BASE / "数据处理代码与流程.md", BASE / "数据处理代码与流程.docx",
                           BASE / "figures_pipeline" / "fig_pipeline_run.png",
                           BASE / "项目流程图.md", BASE / "项目流程图.docx",
                           BASE / "figures_project" / "flow_project.png",
                           BASE / "figures_project" / "flow_project.pdf"]),
    # every experiment: the record document, its rendered run-record panels, the
    # scripts it cites (byte-identical copies) and the run logs that were kept
    ("07_复现材料", BASE, [BASE / "实验代码与运行记录.md", BASE / "实验代码与运行记录.docx"]),
    ("07_复现材料", BASE, [BASE / "材料完整性清单.md", BASE / "材料完整性清单.docx"]),
    ("07_复现材料", BASE, [BASE / "数据产物清单.md", BASE / "数据产物清单.docx"]),
    # the six extension experiments: the report plus the summary files each one
    # produced (the per-seed predictions stay in the repository, whose size the
    # archive already pins)
    ("07_复现材料/扩展实验", BASE,
     [BASE / "扩展实验报告.md", BASE / "扩展实验报告.docx"]),
    ("07_复现材料/扩展实验/结果摘要", ROOT,
     [ROOT / "results_member_family_v1" / "member_family_summary.json",
      ROOT / "results_member_family_v1" / "gate_results_by_config.csv",
      ROOT / "results_day_holdout_v1" / "day_holdout_summary.json",
      ROOT / "results_day_holdout_v1" / "day_holdout_metrics.csv",
      ROOT / "results_day_holdout_v1" / "day_class_support.csv",
      ROOT / "results_deployment_metrics_v1" / "deployment_summary.json",
      ROOT / "results_deployment_metrics_v1" / "deployment_metrics_by_seed.csv",
      ROOT / "results_rccf_cic_ids2018_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_cic_ids2018_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_cic_ids2018_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_cic_iot2023_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_cic_iot2023_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_cic_iot2023_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_nsl_v10" / "metrics_aggregate.csv",
      ROOT / "results_rccf_nsl_v10" / "metrics_by_seed.csv",
      ROOT / "results_rccf_nsl_v10" / "run_manifest.json",
      ROOT / "results_rccf_unsw_v10" / "metrics_aggregate.csv",
      ROOT / "results_rccf_unsw_v10" / "metrics_by_seed.csv",
      ROOT / "results_rccf_unsw_v10" / "run_manifest.json",
      ROOT / "results_rccf_nbaiot_v10" / "metrics_aggregate.csv",
      ROOT / "results_rccf_nbaiot_v10" / "metrics_by_seed.csv",
      ROOT / "results_rccf_nbaiot_v10" / "run_manifest.json",
      ROOT / "results_rccf_litnet2020_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_litnet2020_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_litnet2020_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_iot23_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_iot23_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_iot23_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_rt_iot2022_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_rt_iot2022_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_rt_iot2022_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_aci_iot2023_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_aci_iot2023_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_aci_iot2023_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_uavids2025_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_uavids2025_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_uavids2025_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_genis2025_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_genis2025_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_genis2025_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_ids2025_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_ids2025_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_ids2025_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_gotham2025_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_gotham2025_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_gotham2025_v1_k8" / "benchmark_summary.json",
      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_aggregate.csv",
      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_by_seed.csv",
      ROOT / "results_rccf_ctu_idseval6_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_ctu_idseval6_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_ctu_idseval6_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_6tisch2026_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_6tisch2026_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_6tisch2026_v1" / "metrics_by_seed.csv",
      ROOT / "results_rccf_rtn2026_v1" / "benchmark_summary.json",
      ROOT / "results_rccf_rtn2026_v1" / "metrics_aggregate.csv",
      ROOT / "results_rccf_rtn2026_v1" / "metrics_by_seed.csv"]),
    # the code base travels with everything needed to rebuild it: image, licence,
    # data and model cards, dependency lists, the CI definition and the tests
    ("07_复现材料/元数据", ROOT, [ROOT / "LICENSE", ROOT / "DATA_CARD.md", ROOT / "MODEL_CARD.md",
                                  ROOT / "Dockerfile", ROOT / "requirements-direct.txt",
                                  ROOT / "pytest.ini"]),
    ("07_复现材料/ci", ROOT / ".github",
     sorted(p for p in (ROOT / ".github").rglob("*") if p.is_file())),
    ("07_复现材料/docs", ROOT / "docs",
     sorted(p for p in (ROOT / "docs").rglob("*") if p.is_file())),
    ("07_复现材料/tests", ROOT / "tests",
     sorted(p for p in (ROOT / "tests").glob("*.py"))),
    ("07_复现材料/退役材料/superseded", ROOT / "superseded",
     sorted(p for p in (ROOT / "superseded").glob("*") if p.is_file())),
    ("07_复现材料/退役材料/superseded_docs", ROOT / ".quarantine" / "superseded_docs",
     sorted(p for p in (ROOT / ".quarantine" / "superseded_docs").glob("*") if p.is_file())),
    ("07_复现材料/发布快照", ROOT / "results_publication_final",
     sorted(p for p in (ROOT / "results_publication_final").glob("*")
            if p.is_file() and p.name != "MANIFEST.json")
     + sorted((ROOT / "results_publication_final" / "figures").glob("*"))
     + sorted((ROOT / "results_publication_final" / "deployment").glob("*"))),
    ("07_复现材料/归档索引", ROOT,
     [ROOT / "FULL_RESEARCH_ARCHIVE_README_20260912.md",
      ROOT / "RCCF_FULL_RESEARCH_ARCHIVE_20260912.sha256",
      ROOT / "RCCF_FULL_RESEARCH_ARCHIVE_v2_20260912.tar.gz.sha256",
      ROOT / "RCCF_FULL_RESEARCH_ARCHIVE_v2_20260912.tar.gz.manifest.json",
      ROOT / "RCCF_完整研究档案_v2_20260912.tar.gz.sha256",
      ROOT / "RCCF_完整研究档案_v2_20260912.tar.gz.manifest.json",
      ROOT / "RCCF_v3b_package_manifest_20260912.json",
      ROOT / "RCCF_v3b_package_checksums_20260912.txt"]),
    ("07_复现材料/figures_experiments", BASE / "figures_experiments",
     sorted((BASE / "figures_experiments").glob("*.png"))),
    ("07_复现材料/实验代码", BASE / "实验代码",
     sorted(p for p in (BASE / "实验代码").rglob("*") if p.is_file())),
    ("07_复现材料/实验日志", BASE / "实验日志",
     sorted(p for p in (BASE / "实验日志").glob("*") if p.is_file())),
    ("08_主表", ROOT / "results_publication_final" / "main_tables",
     sorted((ROOT / "results_publication_final" / "main_tables").glob("*"))),
    ("09_投稿文本", ROOT / "results_publication_final" / "submission_text",
     sorted((ROOT / "results_publication_final" / "submission_text").glob("*"))),
    ("10_论文介绍与汇报", BASE,
     [BASE / "论文介绍.md", BASE / "论文介绍.docx",
      BASE / "向老师汇报要点.md", BASE / "向老师汇报要点.docx",
      BASE / "汇报用_论文介绍.pptx"]),
    # 计算机学报版式的中文稿（作者 2026-10-07 要求按该刊布局重排）
    ("11_计算机学报排版版", BASE,
     [BASE / "中文SCI论文_计算机学报排版版.md", BASE / "中文SCI论文_计算机学报排版版.docx"]),
]

# The README inside the archive quotes the self-check totals and the figure
# count; both drift every round, so derive them instead of hard-coding.
def _selfcheck_totals() -> str:
    import re
    text = (BASE / "论文自查表.md").read_text(encoding="utf-8")
    match = re.search(r"\| \*\*合计\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", text)
    if not match:
        return "未知"
    total, passed, partial, missing = match.groups()
    return f"{total} 项：{passed} 通过 / {partial} 部分通过 / {missing} 缺失"


def _figure_count() -> int:
    return len(sorted((BASE / "figures_en").glob("*.png")))


def _report_range() -> str:
    """The round range the review report documents, read from its own headings."""
    import re
    text = (BASE / "遗漏问题审查报告.md").read_text(encoding="utf-8")
    rounds = re.findall(r"^#{2,3} .*?第([一二三四五六七八九十]+)轮", text, flags=re.M)
    return f"第一至第{rounds[-1]}轮" if rounds else "轮次未知"


_SUPP_RANGE = SUPPLEMENTARY.name.replace("补充材料_S01_", "S01–")

README = f"""# 论文投稿包 {TAG}

本包由 `scripts/package_submission_bundle_v18.py` 从仓库中的规范化位置直接复制生成，
内容与《论文自查表》（{_selfcheck_totals()}）及 `MANIFEST.json` 一致。

## 目录

| 目录 | 内容 |
|---|---|
| 01_正式稿件 | 英文稿与中文稿（可编辑 Word + Markdown 源文件） |
| 02_投稿文件 | Highlights、投稿信（JISA）、图形摘要（PNG/PDF） |
| 03_图片 | 正文插图（英文版与中文版，各 {_figure_count()} 张） |
| 04_补充材料 | {_SUPP_RANGE}，含索引 README 与 SHA-256 校验清单 |
| 05_自查与审查 | 论文自查表、遗漏问题审查报告（{_report_range()}） |
| 06_研究与写作方案 | 结构诊断、缺口审计、P0/P1 执行手册（均标注为历史快照）、项目工作日志 |
| 07_复现材料 | 材料完整性清单、数据产物清单、扩展实验报告（十四个扩展实验，含 2026-10-03 现代语料阶梯：规模档位、来源留出、特征预算扫描、机制套件；八个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份，含结果摘要）、数据与资料来源总表、公式来源与核验、数据处理代码与流程、项目流程图、实验代码与运行记录（18 个主线实验 + 全部代码 + 25 张运行记录面板 + 4 份原始日志）、元数据、CI 定义、docs 来源记录与截图、138 项单元测试、退役材料清单、发布快照、归档索引、发布清单、仓库说明、CITATION |
| 08_主表 | 正文 8 张主表（含表 4 的两个面板共 9 个 CSV）与导出索引 |
| 09_投稿文本 | 中英标题、摘要与关键词（投稿系统字段用的纯文本） |
| 10_论文介绍与汇报 | 论文介绍（背景、判据、完整数字、术语表、读稿路线）、汇报要点（30 秒/3 分钟/10 分钟口径、逐页讲稿、数字速查、24 问预判问答、措辞红线、汇报前检查清单）与 12 页汇报 PPT（含讲稿备注，末尾两页为数字速查与复现入口）|

## 投稿前仍需作者完成的三件事

1. 按 JISA 官方模板排版（Guide for Authors 获取当天版本）。
2. 填写署名、单位、通信作者、ORCID、基金与利益冲突声明，以及 `CITATION.cff` 的
   `authors` 字段（自查表 A5/A6 行列出全部位置）。
3. 送一次母语润色（E6）。

代码与逐样本预测公开于 https://github.com/linran-muxue/leakage-controlled-nids-study （标签 {TAG}）。
"""
def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    # regenerate the derived exports so the archive cannot ship a stale one
    for script in ("export_manuscript_tables_v1.py", "export_submission_text_v1.py"):
        subprocess.run([sys.executable, str(Path(__file__).resolve().parent / script)],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    archive = BUILD / f"{NAME}.zip"
    if archive.exists():
        archive.unlink()
    staged: list[tuple[str, Path]] = []
    for folder, root, files in LAYOUT:
        for path in files:
            if not path.exists():
                raise SystemExit(f"missing artifact: {path}")
            relative = path.relative_to(root)
            staged.append((f"{NAME}/{folder}/{relative.as_posix()}", path))
    checksums = []
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr(f"{NAME}/00_说明.md", README)
        for arcname, path in staged:
            bundle.write(path, arcname)
            checksums.append(f"{digest(path)}  {arcname}")
        bundle.writestr(f"{NAME}/checksums.sha256", "\n".join(checksums) + "\n")
    print(f"BUNDLE={archive}")
    print(f"BUNDLE_FILES={len(staged)}")
    print(f"BUNDLE_MB={archive.stat().st_size / 1024 / 1024:.2f}")
if __name__ == "__main__":
    main()
