"""Bring the two briefing documents in line with the thirteen-corpus evidence.

The supervisor's first objection was that the corpora were too old, yet both
documents that get shown to a supervisor still described four datasets and a
fixed "722 prediction files".  This script gives both builders a helper that
counts the evaluated corpora and the released per-row prediction files from the
working tree, adds an "is the data too old?" entry to the anticipated-questions
list, rewrites the four-corpus statements and updates the question count.

Run scripts/build_paper_intro_v1.py and scripts/build_talk_script_v1.py
afterwards, then rebuild the Word copies.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "scripts" / "build_paper_intro_v1.py"
TALK = ROOT / "scripts" / "build_talk_script_v1.py"
BUNDLE = ROOT / "scripts" / "package_submission_bundle_v18.py"

HELPER_LINES = [
    "",
    "",
    "def corpus_facts() -> tuple[int, int, str]:",
    '    """(evaluated corpora, released prediction files, the 2025 summary line).',
    "",
    "    Counted from the working tree rather than typed: both numbers moved",
    "    twice while the recent corpora were being added.",
    '    """',
    '    extension = [path for path in ROOT.glob("results_rccf_*_v1")',
    '                 if (path / "benchmark_summary.json").exists()]',
    "    corpora = 4 + len(extension)",
    '    predictions = len(list(ROOT.glob("results_*/**/predictions*.csv")))',
    "    y2025 = []",
    '    for folder, label in (("results_rccf_uavids2025_v1", "UAVIDS-2025"),',
    '                          ("results_rccf_genis2025_v1", "GeNIS"),',
    '                          ("results_rccf_ids2025_v1", "IDS2025")):',
    '        path = ROOT / folder / "benchmark_summary.json"',
    "        if not path.exists():",
    "            continue",
    '        data = json.loads(path.read_text(encoding="utf-8"))',
    '        y2025.append(f"{label}（{len(data[\'classes\'])} 类，Macro-F1 "',
    '                     f"{data[\'rccf_mean_macro_f1\']:.4f}，差 "',
    '                     f"{data[\'same_members_difference\']:+.6f}）")',
    '    return corpora, predictions, "、".join(y2025)',
    "",
]
HELPER = "\n".join(HELPER_LINES)


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


def add_helper(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "def corpus_facts()" in text:
        print(f"{path.name}: helper already present")
        return
    if "import json" not in text:
        if text.count("import sys\n") != 1:
            raise SystemExit(f"{path.name}: cannot place the json import")
        text = text.replace("import sys\n", "import json\nimport sys\n", 1)
    anchor = "ROOT = Path(__file__).resolve().parents[1]\n"
    if text.count(anchor) != 1:
        raise SystemExit(f"{path.name}: ROOT anchor not unique")
    text = text.replace(anchor, anchor + HELPER + "\n", 1)
    main_anchor = "def main() -> None:\n"
    if text.count(main_anchor) != 1:
        raise SystemExit(f"{path.name}: main() anchor not unique")
    text = text.replace(
        main_anchor,
        main_anchor + "    corpora, predictions, y2025_line = corpus_facts()\n", 1)
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: helper added and wired into main()")


def main() -> None:
    add_helper(INTRO)
    add_helper(TALK)

    patch(INTRO, [
        ('f"| RQ3 | 结论随规模、先验与语料如何变化？| 三档总体（53 237 / 413 209 / 2 429 503）"\n'
         '                 f"+ 平衡控制总体 + 三个独立原生标签基准 |")',
         'f"| RQ3 | 结论随规模、先验与语料如何变化？| 三档总体（53 237 / 413 209 / 2 429 503）"\n'
         '                 f"+ 平衡控制总体 + 三个独立原生标签基准 + {corpora} 个语料"\n'
         '                 f"（含 2025 年发布的三份）|")',
         "RQ3 row"),
        ('    lines.append("### 4.4 先验、外部基准与文件级外推")',
         '    lines.append(f"- **语料年代不是结论的前提**：本文共评测 {corpora} 个语料，其中八个发布于 "\n'
         '                 f"2020 年及以后、三份发布于 2025 年；2025 年语料上门控与同成员等权融合的"\n'
         '                 f"差值仍在 0.000004-0.000020 量级：{y2025_line}。")\n'
         '    lines.append("")\n'
         '    lines.append("### 4.4 先验、外部基准与文件级外推")',
         "recency paragraph"),
        ('lines.append("- 研究总体是审计后的公开数据子集，**不是生产流量**；四个语料都不提供同一测试床上的时间分离留出集；")',
         'lines.append(f"- 研究总体是审计后的公开数据子集，**不是生产流量**；{corpora} 个语料都不提供"\n'
         '                 "同一测试床上的时间分离留出集；")',
         "boundary corpus count"),
        ('                 "22 问预判问答、检查清单）与 `汇报用_论文介绍.pptx`（12 页）；")',
         '                 "23 问预判问答、检查清单）与 `汇报用_论文介绍.pptx`（12 页）；")',
         "intro FAQ count"),
    ])

    patch(TALK, [
        ('    lines.append("## 七、老师最可能追问的 22 个问题")',
         '    lines.append("## 七、老师最可能追问的 23 个问题")', "heading count"),
        ('    lines.append("前八问每次汇报都会出现；后面十四问按老师追问的方向取用"\n'
         '                 "（设计 4、统计 4、数据 3、流程与边界 3）。")',
         '    lines.append("前八问每次汇报都会出现；后面十五问按老师追问的方向取用"\n'
         '                 "（设计 4、统计 4、数据 4、流程与边界 3）。")',
         "question breakdown"),
        ('        ("数据和代码可信吗？",\n'
         '         "四个数据集的摘要与字节数都与来源记录逐一核对过（CIC 8 个文件 2 830 743 行、"\n'
         '         "NSL/UNSW 官方划分、N-BaIoT 归档 1 772 922 927 字节），722 个逐样本预测全部公开，"\n'
         '         f"仓库带 tag；{counts.gate_checks()} 项自动检查每次提交前全绿。"),',
         '        ("数据和代码可信吗？",\n'
         '         f"{corpora} 个语料的摘要与字节数都与来源记录逐一核对过（CIC 8 个文件 2 830 743 行、"\n'
         '         "NSL/UNSW 官方划分、N-BaIoT 归档 1 772 922 927 字节），"\n'
         '         f"{predictions:,} 个逐样本预测全部公开，"\n'
         '         f"仓库带 tag；{counts.gate_checks()} 项自动检查每次提交前全绿。"),\n'
         '        ("数据集是不是太老了？",\n'
         '         f"评测的 {corpora} 个语料里八个发布于 2020 年及以后，其中三份发布于 2025 年："\n'
         '         f"{y2025_line}；"\n'
         '         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"\n'
         '         "结论不随语料年代改变。"),',
         "trust and recency questions"),
        ('         "四个公开语料都不提供同一测试床上的时间戳，无法构造真正的时间留出集；"',
         '         f"{corpora} 个公开语料都不提供同一测试床上的时间戳，无法构造真正的时间留出集；"',
         "temporal-holdout answer"),
        ('lines.append("- 不说「生产可用」：四个语料都不含生产流量，也没有同一测试床上的时间分离留出集；")',
         'lines.append(f"- 不说「生产可用」：{corpora} 个语料都不含生产流量，"\n'
         '                 "也没有同一测试床上的时间分离留出集；")',
         "taboo wording"),
    ])

    patch(BUNDLE, [("22 问预判问答", "23 问预判问答", "bundle README FAQ count")])
    print("RECENCY_BRIEFINGS_ADDED")


if __name__ == "__main__":
    main()
