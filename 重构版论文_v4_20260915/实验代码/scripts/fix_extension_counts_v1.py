"""Repair the extension-set counts after the two recent-corpus rounds.

Two counts were never updated when the corpus rounds landed:

* the extension report's header still announced six experiments while the report
  grew to eight sections (the 2020-2023 and 2025 corpus sections were appended);
* Section 5.8 of both manuscripts still announced five extensions while listing
  six blocks of results;
* the bundle README enumerated the extension material without the three 2025
  corpora.

Everything here is an assertion-anchored rewrite; the report itself is then
rebuilt from the released summaries, and the gate re-derives every number.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def replace(path: Path, old: str, new: str, note: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        print(f"{path.name}: already applied ({note})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note}")


def main() -> None:
    builder = ROOT / "scripts" / "build_extension_report_v1.py"
    replace(builder,
            "             \"> 六个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、\"\n"
            "             \"CIC-IDS2018、CIC-IoT-2023。每个实验的逐种子数据都保存在对应的 \"\n"
            "             \"`results_*` 目录中，本报告只从那些文件读数字。\", \"\"]",
            "             \"> 八个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、\"\n"
            "             \"CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份。\"\n"
            "             \"每个实验的逐种子数据都保存在对应的 `results_*` 目录中，\"\n"
            "             \"本报告只从那些文件读数字。\", \"\"]",
            "report header count")

    bundle = ROOT / "scripts" / "package_submission_bundle_v18.py"
    replace(bundle,
            "扩展实验报告（十个补充语料与实验：专家家族与数量、按天留出、外部十种子、部署指标、"
            "CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、ACI-IoT-2023，含结果摘要）",
            "扩展实验报告（八个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"
            "CIC-IDS2018、CIC-IoT-2023、2020–2023 年语料四份、2025 年语料三份，含结果摘要）",
            "bundle README enumeration")

    en = BASE / "English_SCI_Manuscript_v4.md"
    replace(en, "Five extensions probe the boundaries of the main result;",
            "Six extensions probe the boundaries of the main result;", "English §5.8 count")
    zh = BASE / "中文SCI论文_v4_重构版.md"
    replace(zh, "五个扩展实验界定了主结论的边界；",
            "六个扩展实验界定了主结论的边界；", "中文 §5.8 计数")
    print("EXTENSION_COUNTS_FIXED")


if __name__ == "__main__":
    main()
