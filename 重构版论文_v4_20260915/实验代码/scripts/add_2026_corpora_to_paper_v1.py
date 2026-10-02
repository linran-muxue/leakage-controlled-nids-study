"""Integrate the three 2026 corpora: CTU-IDSEVAL-6, 6TiSCHSet-2026, RTN traffic.

All three are inert (two exactly, one by -0.000026), so the paper's conclusion is
unchanged and the abstract does not need to move.  What changes is the corpus
count (fourteen -> seventeen), the vintage paragraph, the extension report, the
sources table and the bundle.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"
SOURCES = ROOT / "scripts" / "build_data_sources_doc_v1.py"
REPORT = ROOT / "scripts" / "build_extension_report_v1.py"
REPORT_CHECK = ROOT / "scripts" / "check_extension_report_v1.py"
BUNDLE = ROOT / "scripts" / "package_submission_bundle_v18.py"
METRICS_FIX = ROOT / "scripts" / "fix_extension_metrics_v1.py"
TALK = ROOT / "scripts" / "build_talk_script_v1.py"
INTRO = ROOT / "scripts" / "build_paper_intro_v1.py"
DECK = ROOT / "scripts" / "build_talk_deck_v1.py"

RUNS = (("results_rccf_ctu_idseval6_v1", "CTU-IDSEVAL-6"),
        ("results_rccf_6tisch2026_v1", "6TiSCHSet-2026"),
        ("results_rccf_rtn2026_v1", "RTN-traffic-2026"))


def summary(folder: str) -> dict:
    return json.loads((ROOT / folder / "benchmark_summary.json").read_text(encoding="utf-8"))


def feature_count(processed: str) -> int:
    config = json.loads((ROOT / processed / "preprocess_config.json").read_text(encoding="utf-8"))
    return len(config["features"])


def insert_after(path: Path, marker: str, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new_line in text:
        print(f"{path.name}: paragraph already present")
        return
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(marker)]
    if len(hits) != 1:
        raise SystemExit(f"{path.name}: {marker!r} starts {len(hits)} lines")
    ending = "\r\n" if lines[hits[0]].endswith("\r\n") else "\n"
    lines.insert(hits[0] + 1, new_line + ending)
    path.write_text("".join(lines), encoding="utf-8")
    print(f"{path.name}: inserted paragraph after {marker}")


def patch(path: Path, pairs: list[tuple[str, str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, note in pairs:
        if new in text and old not in text:
            print(f"{path.name}: already applied ({note})")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
        text = text.replace(old, new, 1)
        print(f"{path.name}: {note}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ctu, tisch, rtn = (summary(folder) for folder, _ in RUNS)
    tisch_features = feature_count("data_processed_6tisch2026_v1")
    # Chinese prose uses a space, not a comma, as the thousands separator
    ctu_rows = f"{ctu['test_rows']:,}".replace(",", " ")
    tisch_rows = f"{tisch['test_rows']:,}".replace(",", " ")
    en = (
        f"**Three more corpora from 2026.** The three newest openly licensed corpora "
        f"reproduce the inert result on the same ten seeds. CTU-IDSEVAL-6 (Zeek "
        f"connection logs, {len(ctu['classes'])} classes, {ctu['test_rows']:,} test flows) gives "
        f"{ctu['rccf_mean_macro_f1']:.6f} for the gate against "
        f"{ctu['equal_fusion_mean_macro_f1']:.6f} for the same-members fusion, a "
        f"{ctu['same_members_difference']:+.6f} difference; 6TiSCHSet-2026, a leakage-aware "
        f"6TiSCH benchmark whose own schema defines the {tisch_features}-feature "
        f"input, reaches {tisch['rccf_mean_macro_f1']:.6f} for both arms over "
        f"{len(tisch['classes'])} classes and {tisch['test_rows']:,} records; the RTN packet "
        f"table saturates at {rtn['rccf_mean_macro_f1']:.6f} for every model. Seventeen "
        f"corpora now span 1998-2026.")
    zh = (
        f"**2026 年的三份语料。** 三份许可证开放的最新语料在同一组十个种子上复现了惰性结论。"
f"CTU-IDSEVAL-6（Zeek 连接日志，{len(ctu['classes'])} 类、{ctu_rows} 条测试流）"
        f"上门控为 {ctu['rccf_mean_macro_f1']:.6f}，同成员等权融合为 "
        f"{ctu['equal_fusion_mean_macro_f1']:.6f}，差 {ctu['same_members_difference']:+.6f}；"
        f"6TiSCHSet-2026 是自带泄漏感知协议的 6TiSCH 基准，其模式文档规定 "
        f"{tisch_features} 维输入，两个分支在 {len(tisch['classes'])} 类、"
f"{tisch_rows} 条记录上同为 {tisch['rccf_mean_macro_f1']:.6f}；"
        f"RTN 数据包表上所有模型都饱和于 {rtn['rccf_mean_macro_f1']:.6f}。"
        f"本文评测的语料现已覆盖 1998–2026 年共十七个。")
    insert_after(EN, "**A 2025 packet-level corpus, and the condition under which the gate helps.**",
                 en)
    insert_after(ZH, "**2025 年数据包级语料，以及门控在什么条件下有用。**", zh)

    patch(EN, [
        ("**Fourteen corpora were evaluated, and every corpus comes from one collection "
         "programme.**",
         "**Seventeen corpora were evaluated, and every corpus comes from one collection "
         "programme.**", "EN limitation heading"),
        ("the 2025 corpora (UAVIDS-2025, GeNIS, IDS2025, Gotham-2025) were added as extension "
         "corpora",
         "the recent corpora (from UAVIDS-2025 and GeNIS in early 2025 to CTU-IDSEVAL-6, "
         "6TiSCHSet-2026 and the RTN packet table in 2026) were added as extension corpora",
         "EN limitation list"),
        ("None of the fourteen represents production traffic.",
         "None of the seventeen represents production traffic.", "EN limitation count"),
        ("**Corpus vintage.** The thirteen corpora span 1998-2025;",
         "**Corpus vintage.** The seventeen corpora span 1998-2026;", "EN vintage span"),
    ])
    patch(ZH, [
        ("**评测了十四个语料，但它们来自同一批采集计划的有限覆盖。**",
         "**评测了十七个语料，但它们来自同一批采集计划的有限覆盖。**", "中文局限标题"),
        ("其余十个语料（CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、"
         "ACI-IoT-2023 与 2025 年的 UAVIDS-2025、GeNIS、IDS2025、Gotham-2025）作为 5.8 节的扩展语料"
         "复现了主比较。",
         "其余十三个语料（CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、"
         "ACI-IoT-2023，2025 年的 UAVIDS-2025、GeNIS、IDS2025、Gotham-2025，以及 2026 年的 "
         "CTU-IDSEVAL-6、6TiSCHSet-2026 与 RTN 数据包表）作为 5.8 节的扩展语料复现了主比较。",
         "中文局限列表"),
        ("十四个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
         "十七个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。", "中文局限计数"),
        ("**语料年代。** 本文的十三个语料跨越 1998–2025；",
         "**语料年代。** 本文的十七个语料跨越 1998–2026；", "中文年代跨度"),
    ])

    patch(SOURCES, [
        ('                       Path(r"E:\\论文\\data\\external\\y2025\\Gotham2025"\n'
         '                            r"\\gotham2025_manifest.json"))',
         '                       Path(r"E:\\论文\\data\\external\\y2025\\Gotham2025"\n'
         '                            r"\\gotham2025_manifest.json"),\n'
         '                       Path(r"E:\\论文\\data\\external\\y2026"\n'
         '                            r"\\corpora_2026_manifest.json"))', "2026 manifest"),
        ('    ("Gotham-2025", "2025",\n'
         '     "Zenodo record 14502760（Gotham 测试床，78 台 IoT 设备，CC BY 4.0）", "CC BY 4.0",\n'
         '     "GothamDataset2025"),\n)',
         '    ("Gotham-2025", "2025",\n'
         '     "Zenodo record 14502760（Gotham 测试床，78 台 IoT 设备，CC BY 4.0）", "CC BY 4.0",\n'
         '     "GothamDataset2025"),\n'
         '    ("CTU-IDSEVAL-6", "2026", "Zenodo record 21027042（Zeek 连接日志，CTU）", "CC BY 4.0",\n'
         '     "CTU-IDSEVAL-6"),\n'
         '    ("6TiSCHSet-2026", "2026",\n'
         '     "Zenodo record 22113022（6TiSCH 遥测，自带泄漏感知基准）", "CC BY 4.0",\n'
         '     "6TiSCHSet-2026"),\n'
         '    ("RTN-traffic-2026", "2026", "Zenodo record 18910837（数据包级 CSV）", "CC BY 4.0",\n'
         '     "RTN-traffic"),\n)', "2026 corpora added"),
        ('**扩展语料（第 5.8 节，十项）**', '**扩展语料（第 5.8 节，十三项）**', "sources count"),
        ('这十项与上面四项一样，都在同一套处理与评估协议下运行',
         '这十三项与上面四项一样，都在同一套处理与评估协议下运行', "sources sentence"),
        ('"`scripts/fetch_2025_corpora_v1.py`、`scripts/fetch_gotham2025_v1.py` 重新取得，"',
         '"`scripts/fetch_2025_corpora_v1.py`、`scripts/fetch_gotham2025_v1.py`、"\n'
         '                 "`scripts/fetch_2026_corpora_v1.py` 重新取得，"', "fetch scripts"),
    ])

    patch(REPORT, [
        ('             "> 九个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份、"\n'
         '             "2025 年数据包级语料 Gotham-2025。"',
         '             "> 十个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料四份、"\n'
         '             "2026 年语料三份。"', "report header"),
        ('    full = read_json(ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json")',
         '    y2026 = []\n'
         '    for name, label in (("results_rccf_ctu_idseval6_v1", "CTU-IDSEVAL-6（2026）"),\n'
         '                        ("results_rccf_6tisch2026_v1", "6TiSCHSet-2026（2026）"),\n'
         '                        ("results_rccf_rtn2026_v1", "RTN 数据包表（2026）")):\n'
         '        detail = read_json(ROOT / name / "benchmark_summary.json")\n'
         '        if detail:\n'
         '            y2026.append((f"{label}：{len(detail[\'classes\'])} 类，测试 "\n'
         '                          f"{detail[\'test_rows\']:,} 条",\n'
         '                          f"RCCF {detail[\'rccf_mean_macro_f1\']:.6f}，同成员等权融合 "\n'
         '                          f"{detail[\'equal_fusion_mean_macro_f1\']:.6f}，差 "\n'
         '                          f"{detail[\'same_members_difference\']:+.6f}"))\n'
         '    if y2026:\n'
         '        lines += section(\n'
         '            "十、2026 年语料（最新一批）",\n'
         '            "最新发布的开放语料是否改变结论？",\n'
         '            "三份 2026 年发布、CC BY 4.0 的语料，同一水库协议、同一组十个种子；"\n'
         '            "6TiSCHSet-2026 按它自己的模式文档剔除三个标识列。",\n'
         '            r"& $py scripts\\fetch_2026_corpora_v1.py"\n'
         '            "\\n" r"& $py scripts\\prepare_2026_corpora_v1.py --dataset ctu"'
         ' "\\n" r"& $py scripts\\prepare_2026_corpora_v1.py --dataset 6tisch"'
         ' "\\n" r"& $py scripts\\prepare_2026_corpora_v1.py --dataset rtn",\n'
         '            "`E:\\论文\\data\\external\\y2026\\`（原始文件 + `corpora_2026_manifest.json` "\n'
         '            "的 MD5）；处理与结果在 `data_processed_*2026_v1/`、`results_rccf_*2026_v1/`",\n'
         '            y2026,\n'
         '            "三份最新语料上门控与同成员等权融合的差值在 -0.000026–0.000000 之间，"\n'
         '            "其中 RTN 已饱和；结论不随语料年代改变。")\n'
         '    full = read_json(ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json")',
         "2026 report section"),
    ])
    patch(REPORT_CHECK, [
        ('        "results_rccf_gotham2025_v1_k8": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                          "benchmark_summary.json"],',
         '        "results_rccf_gotham2025_v1_k8": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                          "benchmark_summary.json"],\n'
         '        "results_rccf_ctu_idseval6_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                         "benchmark_summary.json"],\n'
         '        "results_rccf_6tisch2026_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                       "benchmark_summary.json"],\n'
         '        "results_rccf_rtn2026_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",\n'
         '                                    "benchmark_summary.json"],', "check dirs"),
        ('                          ("results_rccf_gotham2025_v1_k8", "Gotham-2025 (8/16 features)")):',
         '                          ("results_rccf_gotham2025_v1_k8", "Gotham-2025 (8/16 features)"),\n'
         '                          ("results_rccf_ctu_idseval6_v1", "CTU-IDSEVAL-6"),\n'
         '                          ("results_rccf_6tisch2026_v1", "6TiSCHSet-2026"),\n'
         '                          ("results_rccf_rtn2026_v1", "RTN 数据包表")):', "check values"),
        ('    print(f"EXTENSION_OK experiments=14 quoted={len(checks)} "',
         '    print(f"EXTENSION_OK experiments=17 quoted={len(checks)} "', "check count"),
    ])
    patch(BUNDLE, [
        ('      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_by_seed.csv"]),',
         '      ROOT / "results_rccf_gotham2025_v1_k8" / "metrics_by_seed.csv",\n'
         '      ROOT / "results_rccf_ctu_idseval6_v1" / "benchmark_summary.json",\n'
         '      ROOT / "results_rccf_ctu_idseval6_v1" / "metrics_aggregate.csv",\n'
         '      ROOT / "results_rccf_ctu_idseval6_v1" / "metrics_by_seed.csv",\n'
         '      ROOT / "results_rccf_6tisch2026_v1" / "benchmark_summary.json",\n'
         '      ROOT / "results_rccf_6tisch2026_v1" / "metrics_aggregate.csv",\n'
         '      ROOT / "results_rccf_6tisch2026_v1" / "metrics_by_seed.csv",\n'
         '      ROOT / "results_rccf_rtn2026_v1" / "benchmark_summary.json",\n'
         '      ROOT / "results_rccf_rtn2026_v1" / "metrics_aggregate.csv",\n'
         '      ROOT / "results_rccf_rtn2026_v1" / "metrics_by_seed.csv"]),',
         "bundle summaries"),
    ])
    patch(METRICS_FIX, [
        ('        "results_rccf_gotham2025_v1_k8"]',
         '        "results_rccf_gotham2025_v1_k8", "results_rccf_ctu_idseval6_v1",\n'
         '        "results_rccf_6tisch2026_v1", "results_rccf_rtn2026_v1"]', "metrics list"),
    ])
    patch(TALK, [
        ('         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"\n'
         '         "结论不随语料年代改变。"),',
         '         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"\n'
         '         "结论不随语料年代改变；2026 年新发布的三份（CTU-IDSEVAL-6、6TiSCHSet-2026、"\n'
         '         "RTN 数据包表）差值在 -0.000026 到 0.000000 之间，同样不改变结论。"),',
         "2026 in the recency answer"),
    ])
    patch(INTRO, [
        ('                 f"Gotham-2025 另给出全文唯一一个门控为正的案例：视图重合时差值恰为 0.000000，"\n'
         '                 f"把 16 列拆成 8 列让视图分化后增益 +0.0063（十个种子方向一致）。")',
         '                 f"Gotham-2025 另给出全文唯一一个门控为正的案例：视图重合时差值恰为 0.000000，"\n'
         '                 f"把 16 列拆成 8 列让视图分化后增益 +0.0063（十个种子方向一致）。"\n'
         '                 f"2026 年新发布的三份语料（CTU-IDSEVAL-6、6TiSCHSet-2026、RTN 数据包表）"\n'
         '                 f"差值在 -0.000026 到 0.000000 之间，结论不变。")',
         "2026 in the intro"),
    ])
    print("CORPORA_2026_INTEGRATED")


if __name__ == "__main__":
    main()
