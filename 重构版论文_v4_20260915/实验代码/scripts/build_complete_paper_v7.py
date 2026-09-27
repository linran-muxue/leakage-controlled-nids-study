from pathlib import Path
source = Path(__file__).with_name("build_complete_paper_v6.py").read_text(encoding="utf-8")
source = source.replace('SOURCE = ROOT / "results_paper_materials_v3" / "full_paper_body_v6_data_processing.md"', 'SOURCE = ROOT / "results_paper_materials_v3" / "full_paper_body_v7_final.md"')
source = source.replace('OUTPUT = ROOT / "论文完整正文_v6_数据处理完善稿.docx"', 'OUTPUT = ROOT / "results_paper_materials_v3" / "chinese_sci_manuscript_v1.docx"')
Path(__file__).with_name("_generated_build_complete_paper_v7_impl.py").write_text(source, encoding="utf-8")
ns = {"__file__": str(Path(__file__).with_name("_generated_build_complete_paper_v7_impl.py"))}
exec(compile(source, str(Path(__file__).with_name("_generated_build_complete_paper_v7_impl.py")), "exec"), ns)
