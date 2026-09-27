"""Recompute the counts the deliverables state about themselves.

Every number in this check is a statement a deliverable makes about its own
artefacts - how many tests pass, how long the manuscripts are, how many tables
they carry, how many checks the self-check table holds, how many checks the
gate runs.  Nothing in the gate recomputed them, so seven had drifted:

    test count            118 claimed, 138 collect
    gate checks            34 claimed,  39 run
    English length     12,761 claimed, 14,563 words
    Chinese length     35,338 claimed, 39,816 characters
    main tables             7 claimed,   8 captioned
    numeric tokens        507 claimed, 589 per manuscript
    self-check totals  66/62 claimed, 69/65 in the table

The last group is quoted by the three working documents that open with a
snapshot of the current state, so a stale total there misleads a reader who
starts from them rather than from the table itself.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as repo_counts  # noqa: E402


def run(args: list[str]) -> str:
    proc = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True,
                          errors="replace")
    return proc.stdout + proc.stderr


def measure() -> dict[str, int]:
    english = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    chinese = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
    selfcheck = (BASE / "论文自查表.md").read_text(encoding="utf-8")
    head = selfcheck.split("## 自查结论与行动清单")[0]
    tests = re.search(r"(\d+) tests collected", run(["-m", "pytest", "--collect-only", "-q"]))
    tokens = re.search(r"numeric tokens: en=(\d+) zh=(\d+)",
                       run([str(ROOT / "scripts" / "cross_language_number_diff_v10.py")]))
    if not tests or not tokens:
        raise SystemExit("could not measure the test count or the numeric tokens")
    return {
        "en_words": len(english.split()),
        "zh_chars": len(re.sub(r"\s", "", chinese)),
        # shared with the document generators, so a document that quotes one of
        # these numbers cannot disagree with the gate that recomputes it
        "figures": repo_counts.figures(),
        "tables": repo_counts.tables(),
        "tests": int(tests.group(1)),
        "gate_checks": repo_counts.gate_checks(),
        "bundle_files": repo_counts.bundle_files(),
        "sc_items": len(re.findall(r"^\| [A-G]\d+ \|", head, flags=re.M)),
        "sc_passed": len(re.findall(r"^\| [A-G]\d+ \|.*\*\*通过\*\*", head, flags=re.M)),
        "sc_partial": len(re.findall(r"^\| [A-G]\d+ \|.*\*\*部分通过\*\*", head, flags=re.M)),
        "tokens_en": int(tokens.group(1)),
        "tokens_zh": int(tokens.group(2)),
    }


def declarations(counts: dict[str, int]) -> list[tuple[str, Path, str]]:
    table = BASE / "论文自查表.md"
    header = f"{counts['sc_items']} 项检查，{counts['sc_passed']} 项通过、" \
             f"{counts['sc_partial']} 项部分通过、0 项缺失"
    covered = report_coverage()
    return [
        ("self-check E3 figure and table count", table,
         f"{counts['figures']} 图 {counts['tables']} 表"),
        ("self-check E7 length and table count", table,
         f"英文 {counts['en_words']:,} 词（整篇含参考文献）、{counts['figures']} 图、"
         f"{counts['tables']} 主表；中文 {counts['zh_chars']:,} 字"),
        ("self-check E9 numeric tokens", table,
         f"正文数值 token 英文 {counts['tokens_en']} : 中文 {counts['tokens_zh']}"),
        ("self-check F5 test count", table, f"{counts['tests']} 项单元测试通过"),
        ("self-check F7 test count", table, f"运行 {counts['tests']} 项测试"),
        # The cover letter quotes the suite size too, and the front-matter check
        # could not see it: the number is three digits and the reference list was
        # part of the comparison, so "1189-1232" vouched for "118-test suite".
        ("cover letter test count", BASE / "Cover_Letter_JISA_v4.md",
         f"A {counts['tests']}-test suite runs in continuous integration"),
        ("README gate-check count", ROOT / "README.md", f"({counts['gate_checks']} checks"),
        # The working documents quote the same three numbers.  They drifted -
        # 45, 46 and 47 against the 48 the gate actually ran - because each was
        # typed into its own generator; the generators now measure them.
        ("data-source table gate size", BASE / "数据与资料来源总表.md",
         f"已接入 {counts['gate_checks']} 项验证闸门"),
        ("data-source table archive size", BASE / "数据与资料来源总表.md",
         f"（{counts['bundle_files']} 个文件）"),
        ("briefing script gate size", BASE / "向老师汇报要点.md",
         f"{counts['gate_checks']} 项自动检查每次提交前全绿"),
        ("work log gate size", BASE / "工作日志_论文项目.md",
         f"| 验证闸门 | {counts['gate_checks']} 项检查全绿"),
        ("paper introduction gate size", BASE / "论文介绍.md",
         f"（闸门 {counts['gate_checks']} 项自动复核）"),
        ("gap audit state snapshot", BASE / "研究缺口审计与优先级清单.md", header),
        ("gap audit manuscript length", BASE / "研究缺口审计与优先级清单.md",
         f"{counts['en_words']:,}".replace(",", " ") + f" 词、{counts['figures']} 图、"
         f"{counts['tables']} 表"),
        ("P0/P1 manual state snapshot", BASE / "P0_P1执行手册.md", header),
        ("structure plan state snapshot", BASE / "论文结构诊断与重构方案.md", header),
        # The three working documents describe the review report's coverage in
        # their header block. All three said "第一至第十一轮" while the report
        # documents nineteen rounds, so the range is recomputed from the report's
        # own headings.
        ("gap audit review-report range", BASE / "研究缺口审计与优先级清单.md", covered),
        ("P0/P1 manual review-report range", BASE / "P0_P1执行手册.md", covered),
        ("structure plan review-report range", BASE / "论文结构诊断与重构方案.md", covered),
    ]


def report_coverage() -> str:
    """The round range the review report documents, spelled as its last heading does."""
    text = (BASE / "遗漏问题审查报告.md").read_text(encoding="utf-8")
    rounds = re.findall(r"^#{2,3} .*?第([一二三四五六七八九十]+)轮", text, flags=re.M)
    if not rounds:
        raise SystemExit("the review report carries no round headings")
    return f"第一至第{rounds[-1]}轮"


def main() -> int:
    counts = measure()
    for name, value in counts.items():
        print(f"  measured {name:<12}{value}")
    problems = []
    print()
    for label, path, expected in declarations(counts):
        text = path.read_text(encoding="utf-8")
        if expected in text:
            print(f"OK    {label:<42}{expected}")
        else:
            problems.append(f"{label}: {path.name} does not state {expected!r}")
            print(f"ISSUE {label:<42}{expected}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("DELIVERABLE_COUNTS_FAILED")
        return 1
    print("DELIVERABLE_COUNTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
