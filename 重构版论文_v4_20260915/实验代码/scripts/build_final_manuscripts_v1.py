"""Build final bilingual manuscript DOCX files from the final Markdown sources.

The script deliberately uses the canonical final manuscript sources and the
publication evidence package. It does not read historical v2/v3 manuscript
sources as narrative input.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results_paper_materials_v3"
FIG_DIR = ROOT / "results_publication_final" / "figures"
TABLE_DIR = ROOT / "results_publication_final"


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [
            "_".join(str(part) for part in col if str(part) != "nan").strip("_")
            for col in df.columns
        ]
    return df


def add_table(doc: Document, path: Path, title: str, max_rows: int = 20) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    df = flatten_columns(pd.read_csv(path)).head(max_rows)
    p = doc.add_paragraph()
    p.add_run(title).bold = True
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = clean_inline(str(col))
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, value in enumerate(row):
            if isinstance(value, float):
                cells[i].text = f"{value:.6f}"
            else:
                cells[i].text = clean_inline(str(value))
    style_table(table)


def add_figure(doc: Document, path: Path, caption: str) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    doc.add_picture(str(path), width=Inches(6.2))
    p = doc.add_paragraph(caption)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def clean_inline(text: str) -> str:
    """Remove lightweight Markdown delimiters that Word must not display."""
    return text.replace("**", "").replace("`", "").replace("$", "")


def add_inline_paragraph(doc: Document, text: str, *, style: str | None = None, bold: bool = False):
    """Render prose and inline LaTeX spans without visible Markdown delimiters."""
    paragraph = doc.add_paragraph(style=style)
    for part in re.split(r"(\$[^$]+\$)", text):
        if not part:
            continue
        is_math = part.startswith("$") and part.endswith("$")
        run = paragraph.add_run(part[1:-1] if is_math else clean_inline(part))
        run.bold = bold
        if is_math:
            run.font.name = "Cambria Math"
    return paragraph


def style_table(table) -> None:
    table.autofit = True
    for row_index, row in enumerate(table.rows):
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(8)
                    if row_index == 0:
                        run.bold = True


def render_markdown(doc: Document, source: Path, language: str, figures: list[tuple[Path, str]]) -> None:
    lines = source.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-:") for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                table = doc.add_table(rows=1, cols=len(rows[0]))
                table.style = "Table Grid"
                for j, value in enumerate(rows[0]):
                    table.rows[0].cells[j].text = clean_inline(value)
                for row in rows[1:]:
                    cells = table.add_row().cells
                    for j, value in enumerate(row[:len(cells)]):
                        cells[j].text = clean_inline(value)
                style_table(table)
            continue
        if line.startswith("# "):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
        elif line.startswith("**Keywords:**"):
            p = doc.add_paragraph()
            p.add_run("Keywords: ").bold = True
            p.add_run(line.split("**Keywords:**", 1)[1].strip())
        elif line.startswith("- "):
            add_inline_paragraph(doc, line[2:].strip(), style="List Bullet")
        elif line.startswith("> "):
            doc.add_paragraph(line[2:].strip())
        elif stripped.startswith("$$") and stripped.endswith("$$"):
            p = doc.add_paragraph()
            run = p.add_run(stripped[2:-2].strip())
            run.font.name = "Cambria Math"
            run.font.size = Pt(10.5)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif stripped.startswith("**Table ") or stripped.startswith("**表"):
            add_inline_paragraph(doc, stripped, bold=True)
        else:
            add_inline_paragraph(doc, stripped)
        if language == "en" and "summarized in Table 1 and Figure 1" in stripped:
            add_figure(doc, *figures[0])
        elif language == "zh" and "完整比较见表1和图1" in stripped:
            add_figure(doc, *figures[0])
        elif (language == "en" and stripped.startswith("Figure 2 shows")) or (language == "zh" and stripped.startswith("图2给出")):
            for figure in figures[1:]:
                add_figure(doc, *figure)
        i += 1


def build(language: str) -> Path:
    # Supplementary Table S10 carries the completed UNSW-NB15 split-
    # sensitivity protocol; the NSL-KDD class-support table follows as S11.
    if language == "en":
        source = OUT_DIR / "english_sci_manuscript_final.md"
        output = OUT_DIR / "english_sci_manuscript_final.docx"
        evidence_title = "Supplementary evidence tables and figures"
        tables = [
            (ROOT / "results_cic_natural_baselines_v3b" / "metrics_aggregate_flat.csv", "Supplementary Table S0. CIC-IDS2017 observed-prior primary protocol", 10),
            (ROOT / "results_rccf_evidence_v3b" / "model_metrics.csv", "Supplementary Table S1. Locked CIC-IDS2017 model comparison", 10),
            (ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv", "Supplementary Table S2. RCCF CIC probability and selective metrics", 10),
            (ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv", "Supplementary Table S3. NSL-KDD independent native-label benchmark", 10),
            (ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv", "Supplementary Table S4. UNSW-NB15 independent native-label benchmark", 10),
            (ROOT / "results_rccf_evidence_v3b" / "macro_f1_paired_tests.csv", "Supplementary Table S5. Paired Macro-F1 tests", 10),
            (ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv", "Supplementary Table S6. Shared-perturbation robustness", 12),
            (ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv", "Supplementary Table S7. P50/P95/P99 latency", 12),
            (ROOT / "results_rccf_evidence_v3b" / "paired_bootstrap_macro_f1.csv", "Supplementary Table S8. Paired bootstrap intervals", 12),
            (ROOT / "results_rccf_evidence_v3b" / "file_label_coverage.csv", "Supplementary Table S9. Raw-file label coverage", 12),
            (ROOT / "results_file_external_generalization_v3b" / "file_external_results.csv", "Supplementary Table S12. Strict file-external pressure test", 12),
            (ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics.csv", "Supplementary Table S10. UNSW-NB15 split-sensitivity protocols", 12),
            (ROOT / "results_rccf_nsl_v2_final" / "class_counts_seed2024.csv", "Supplementary Table S11. NSL-KDD class support and predictions", 12),
        ]
        figures = [
            (FIG_DIR / "fig_rccf_model_performance.png", "Figure 1. Locked CIC-IDS2017 comparison on the balanced research subset."),
            (FIG_DIR / "fig_rccf_calibration.png", "Figure 2. Test-set probability calibration under the locked protocol."),
            (FIG_DIR / "fig_rccf_robustness.png", "Figure 3. Shared-perturbation robustness under identical masks."),
            (FIG_DIR / "fig_rccf_latency_percentiles.png", "Figure 4. Offline P50/P95/P99 latency; this is not end-to-end gateway latency."),
            (FIG_DIR / "fig_rccf_file_label_coverage.png", "Figure 5. Raw-file by label coverage audit."),
            (FIG_DIR / "fig_rccf_confusion_matrix.png", "Figure 6. Normalized CIC confusion matrix (seed 2024)."),
        ]
    elif language == "zh":
        source = OUT_DIR / "chinese_sci_manuscript_final.md"
        output = OUT_DIR / "chinese_sci_manuscript_final.docx"
        evidence_title = "补充证据表与图"
        tables = [
            (ROOT / "results_cic_natural_baselines_v3b" / "metrics_aggregate_flat.csv", "补充表S0 CIC-IDS2017观测先验主要协议", 10),
            (ROOT / "results_rccf_evidence_v3b" / "model_metrics.csv", "补充表S1 受控CIC-IDS2017模型比较", 10),
            (ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv", "补充表S2 RCCF CIC概率与选择性指标", 10),
            (ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv", "补充表S3 NSL-KDD原生标签独立基准", 10),
            (ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv", "补充表S4 UNSW-NB15原生标签独立基准", 10),
            (ROOT / "results_rccf_evidence_v3b" / "macro_f1_paired_tests.csv", "补充表S5 Macro-F1成对检验", 10),
            (ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv", "补充表S6 共享扰动鲁棒性", 12),
            (ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv", "补充表S7 P50/P95/P99延迟", 12),
            (ROOT / "results_rccf_evidence_v3b" / "paired_bootstrap_macro_f1.csv", "补充表S8 成对Bootstrap区间", 12),
            (ROOT / "results_rccf_evidence_v3b" / "file_label_coverage.csv", "补充表S9 原始文件标签覆盖", 12),
            (ROOT / "results_file_external_generalization_v3b" / "file_external_results.csv", "补充表S12 严格文件外压力测试", 12),
            (ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics.csv", "补充表S10 UNSW-NB15划分敏感性协议", 12),
            (ROOT / "results_rccf_nsl_v2_final" / "class_counts_seed2024.csv", "补充表S11 NSL-KDD类别支持数与预测数", 12),
        ]
        figures = [
            (FIG_DIR / "fig_rccf_model_performance.png", "图1 平衡研究子集上的受控CIC-IDS2017模型比较。"),
            (FIG_DIR / "fig_rccf_calibration.png", "图2 锁定协议下的测试集概率校准曲线。"),
            (FIG_DIR / "fig_rccf_robustness.png", "图3 相同扰动掩码下的共享鲁棒性比较。"),
            (FIG_DIR / "fig_rccf_latency_percentiles.png", "图4 离线P50/P95/P99延迟；不代表端到端网关延迟。"),
            (FIG_DIR / "fig_rccf_file_label_coverage.png", "图5 原始文件—标签覆盖审计。"),
            (FIG_DIR / "fig_rccf_confusion_matrix.png", "图6 CIC归一化混淆矩阵（seed 2024）。"),
        ]
    else:
        raise ValueError(language)

    if not source.exists():
        raise FileNotFoundError(source)
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(10.5)
    render_markdown(doc, source, language, figures)
    doc.add_page_break()
    doc.add_heading(evidence_title, level=1)
    for path, title, max_rows in tables:
        add_table(doc, path, title, max_rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=["en", "zh", "both"], default="both")
    args = parser.parse_args()
    languages = ["en", "zh"] if args.language == "both" else [args.language]
    for language in languages:
        print(f"DOCX_WRITTEN={build(language)}")


if __name__ == "__main__":
    main()
