"""Thread the pooled modern-corpus result through the reports and briefings."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def patch(path: Path, pairs: list[tuple[str, str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, note in pairs:
        if new in text:
            print(f"{path.name}: already applied ({note})")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
        text = text.replace(old, new, 1)
        print(f"{path.name}: {note}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    data = json.loads((ROOT / "results_modern_replication_v1" /
                       "summary.json").read_text(encoding="utf-8"))
    five = data["pooled_005"]
    with_pos = data["pooled_with_positive_005"]
    positive = data["positive_case"]

    patch(BASE / "English_SCI_Manuscript_v4.md", [
        ("None of the seventeen represents production traffic.",
         f"None of the seventeen represents production traffic. Pooling the twelve published in "
         f"2020 or later gives {five['n']} seed-level comparisons whose 90% interval, "
         f"[{five['ci90_low']:+.6f}, {five['ci90_high']:+.6f}] on a mean of "
         f"{five['mean']:+.6f}, lies inside the 0.005 margin - so the equivalence claim does not "
         f"rest on the 2017 corpus alone.", "EN limitation pooled sentence"),
    ])
    patch(BASE / "中文SCI论文_v4_重构版.md", [
        ("十七个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
         f"十七个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。"
         f"把其中 2020 年及以后发布的十二个合并起来，得到 {five['n']} 个种子级比较："
         f"均值为 {five['mean']:+.6f}，90% 区间 "
         f"[{five['ci90_low']:+.6f}, {five['ci90_high']:+.6f}]，仍落在 0.005 边界内——"
         f"等价性结论并不只依赖 2017 年那一个语料。", "中文局限合并句"),
    ])

    patch(ROOT / "scripts" / "build_extension_report_v1.py", [
        ('             "> 十个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料四份、"\n'
         '             "2026 年语料三份。"',
         '             "> 十一个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"\n'
         '             "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料四份、"\n'
         '             "2026 年语料三份，以及十二个现代语料的合并等价性检验。"', "report header"),
    ])
    patch(ROOT / "scripts" / "build_extension_report_v1.py", [
        ('    text = "\\n".join(lines) + "\\n"',
         '    pooled = read_json(ROOT / "results_modern_replication_v1" / "summary.json")\n'
         '    if pooled:\n'
         '        five = pooled["pooled_005"]\n'
         '        with_pos = pooled["pooled_with_positive_005"]\n'
         '        positive = pooled["positive_case"]\n'
         '        lines += section(\n'
         '            "十一、现代语料的合并等价性检验",\n'
         '            "把 2020–2026 年的语料合并起来，等价性还成立吗？",\n'
         '            f"十二个 2020–2026 年发布的语料，同一协议、同一组十个种子、同一套同成员对照；"\n'
         '            "每个语料的逐种子配对差由它自己发布的逐样本预测重算。",\n'
         '            r"& $py scripts\\analyse_modern_replication_v1.py",\n'
         '            "`results_modern_replication_v1/`（per_corpus_differences.csv、summary.json）",\n'
         '            [(f"合并（{five[\'n\']} 个种子级比较）",\n'
         '              f"均值 {five[\'mean\']:+.6f}，90% 区间 "\n'
         '              f"[{five[\'ci90_low\']:+.6f}, {five[\'ci90_high\']:+.6f}]，"\n'
         '              f"0.005 边界内等价={five[\'equivalent\']}"),\n'
         '             ("并入 Gotham-2025 降维正例",\n'
         '              f"均值 {with_pos[\'mean\']:+.6f}，90% 区间 "\n'
         '              f"[{with_pos[\'ci90_low\']:+.6f}, {with_pos[\'ci90_high\']:+.6f}]，"\n'
         '              f"仍等价={with_pos[\'equivalent\']}")],\n'
         '            "把等价性结论从 2017 年的单一语料搬到 2020–2026 年的十二个语料上：合并区间"\n'
         '            "比 0.005 边界窄两个数量级，唯一的正例（Gotham 降维）并入后总体仍等价。")\n'
         '    text = "\\n".join(lines) + "\\n"', "report pooled section"),
    ])
    pooled_sentence = (f"把 2020–2026 年的十二个语料合并起来是 {five['n']} 个种子级比较，"
                       f"均值 {five['mean']:+.6f}、90% 区间 "
                       f"[{five['ci90_low']:+.6f}, {five['ci90_high']:+.6f}]，仍在 0.005 边界内。")
    patch(ROOT / "scripts" / "build_talk_script_v1.py", [
        ('         "结论不随语料年代改变；2026 年新发布的三份（CTU-IDSEVAL-6、6TiSCHSet-2026、"\n'
         '         "RTN 数据包表）差值在 -0.000026 到 0.000000 之间，同样不改变结论。"),',
         '         "结论不随语料年代改变；2026 年新发布的三份（CTU-IDSEVAL-6、6TiSCHSet-2026、"\n'
         '         "RTN 数据包表）差值在 -0.000026 到 0.000000 之间。"\n'
         f'         "{pooled_sentence}"),', "talk pooled numbers"),
    ])
    patch(ROOT / "scripts" / "build_paper_intro_v1.py", [
        ('                 f"2026 年新发布的三份语料（CTU-IDSEVAL-6、6TiSCHSet-2026、RTN 数据包表）"\n'
         '                 f"差值在 -0.000026 到 0.000000 之间，结论不变。")',
         '                 f"2026 年新发布的三份语料（CTU-IDSEVAL-6、6TiSCHSet-2026、RTN 数据包表）"\n'
         '                 f"差值在 -0.000026 到 0.000000 之间。"\n'
         f'                 f"{pooled_sentence}")', "intro pooled numbers"),
    ])
    print("MODERN_REPLICATION_REPORTS_ADDED")


if __name__ == "__main__":
    main()
