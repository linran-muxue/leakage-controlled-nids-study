"""Check that the DOCX deliverables carry the current manuscript content.
The DOCX files are what gets submitted and what the advisor reads, but they are
generated artifacts: editing the Markdown and forgetting to rebuild leaves a
stale DOCX behind. This check reads the DOCX text and looks for the markers
that only the current revision contains.
"""
from __future__ import annotations
import sys
from pathlib import Path
from docx import Document
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from supplementary_paths_v1 import latest_bundle_name
import artifact_counts_v1 as repo_counts  # noqa: E402
BASE = ROOT / "重构版论文_v4_20260915"
EXPECTED = {
    "English_SCI_Manuscript_v4.docx": ["v1.11.0", "3,469", "aggregation-rule differences"],
    "中文SCI论文_v4_重构版.docx": ["v1.11.0", "3469", "聚合规则差异"],
    "论文自查表.docx": ["E9", latest_bundle_name()],
    "遗漏问题审查报告.docx": ["第十一轮"],
    "论文结构诊断与重构方案.docx": ["状态说明"],
    "研究缺口审计与优先级清单.docx": ["状态说明"],
    "P0_P1执行手册.docx": ["状态说明"],
    "Highlights_v4.docx": ["0.005", "0.0725"],
    "Cover_Letter_JISA_v4.docx": ["v1.11.0", "0.000456"],
    # the work log is generated from the records, so it must carry the current
    # guard count and the round ledger rather than an earlier snapshot
    "工作日志_论文项目.docx": ["工作日志", f"{repo_counts.gate_checks()} 项检查", "Round 20"],
    "论文介绍.docx": ["一句话结论", "0.889278", "2 429 503"],
    "向老师汇报要点.docx": ["30 秒版本", "0.005533", "Q8"],
    "数据与资料来源总表.docx": ["数据与资料来源总表", "2 830 743", "CC BY 4.0", "python-pptx"],
    "公式来源与核验.docx": ["公式来源与核验", "二阶展开", "3.19"],
    "数据处理代码与流程.docx": ["数据处理代码与流程", "2,830,743", "prepare_dataset",
                                "audit_data_processing_v1"],
    "项目流程图.docx": ["项目流程图", "① 数据获取", "⑥ 论文与交付", "flow_project.pdf"],
    "实验代码与运行记录.docx": ["实验代码与运行记录", "非屏幕截图", "exp18"],
    "材料完整性清单.docx": ["材料完整性清单", "本地保留", "docs/source_records"],
}
def docx_text(path: Path) -> str:
    document = Document(str(path))
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)
def main() -> int:
    problems: list[str] = []
    for name, markers in EXPECTED.items():
        path = BASE / name
        if not path.exists():
            problems.append(f"{name} is missing")
            print(f"  {name}: MISSING")
            continue
        text = docx_text(path)
        missing = [m for m in markers if m not in text]
        print(f"  {name}: {len(text)} chars, missing markers {missing or 'none'}")
        if missing:
            problems.append(f"{name} is out of date (missing {missing}); rebuild it from the Markdown")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("DOCX_STALE")
        return 1
    print("DOCX_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
