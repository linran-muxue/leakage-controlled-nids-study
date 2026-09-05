"""Build the manuscript using the v6 data-processing section and audit tables."""
from pathlib import Path

source = Path(__file__).with_name("build_complete_paper_v5.py").read_text(encoding="utf-8")
source = source.replace('SOURCE = ROOT / "results_paper_materials_v3" / "full_paper_body_v5_unsw.md"', 'SOURCE = ROOT / "results_paper_materials_v3" / "full_paper_body_v6_data_processing.md"')
source = source.replace('OUTPUT = ROOT / "论文完整正文_v5_UNSW类别分析稿.docx"', 'OUTPUT = ROOT / "论文完整正文_v6_数据处理完善稿.docx"')
source = source.replace('for name, title, rows in legacy: add_table(doc, table_dir / name, title, rows)', 'for name, title, rows in legacy: add_table(doc, table_dir / name, title, rows)\n    add_table(doc, UNSW_TABLES / "table_v6_processing_stage_counts.csv", "表A29 数据处理阶段计数", 12)\n    add_table(doc, UNSW_TABLES / "table_v6_raw_file_processing_audit.csv", "表A30 原始文件逐文件处理审计", 12)\n    add_table(doc, UNSW_TABLES / "table_v6_feature_quality_and_leakage_checks.csv", "表A31 特征质量与泄漏检查", 12)\n    add_table(doc, UNSW_TABLES / "table_v6_file_external_generalization.csv", "表A32 文件外泛化与类别覆盖审计", 20)\n    add_table(doc, UNSW_TABLES / "table_v6_unsw_cross_split_sensitivity.csv", "表A33 UNSW-NB15跨split重复敏感性", 10)\n    add_table(doc, UNSW_TABLES / "table_v6_open_set_matrix.csv", "表A34 开放集未知攻击拒识组合", 10)')
Path(__file__).with_name("_generated_build_complete_paper_v6_impl.py").write_text(source, encoding="utf-8")
ns = {"__file__": str(Path(__file__).with_name("_generated_build_complete_paper_v6_impl.py"))}
exec(compile(source, str(Path(__file__).with_name("_generated_build_complete_paper_v6_impl.py")), "exec"), ns)
ns["main"]()

