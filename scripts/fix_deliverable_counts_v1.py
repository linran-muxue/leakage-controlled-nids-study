"""Bring the deliverables' self-descriptions back in line with the artefacts.

``check_deliverable_counts_v1.py`` recomputes nine counts and found all nine
stale: the self-check table still described 118 tests, 12,761 English words,
35,338 Chinese characters, 507 numeric tokens and 7 tables, README announced a
34-check gate, and the three working documents that open with a snapshot of the
current state still quoted the pre-Round-18 totals (66 checks, 62 passing).

The counts are re-measured here through that check rather than typed in, and
every replacement is asserted to be unique before it is written.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

spec = importlib.util.spec_from_file_location(
    "check_deliverable_counts_v1", ROOT / "scripts" / "check_deliverable_counts_v1.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def main() -> None:
    counts = checker.measure()
    spaced_words = f"{counts['en_words']:,}".replace(",", " ")
    spaced_chars = f"{counts['zh_chars']:,}".replace(",", " ")
    snapshot_old = "66 项检查，62 项通过、4 项部分通过、0 项缺失"
    snapshot_new = (f"{counts['sc_items']} 项检查，{counts['sc_passed']} 项通过、"
                    f"{counts['sc_partial']} 项部分通过、0 项缺失")
    edits: dict[Path, list[tuple[str, str]]] = {
        BASE / "论文自查表.md": [
            (f"{counts['figures']} 图 7 表", f"{counts['figures']} 图 {counts['tables']} 表"),
            ("英文 12,761 词（整篇含参考文献）、11 图、7 主表；中文 35,338 字",
             f"英文 {counts['en_words']:,} 词（整篇含参考文献）、{counts['figures']} 图、"
             f"{counts['tables']} 主表；中文 {counts['zh_chars']:,} 字"),
            ("正文数值 token 英文 507 : 中文 507",
             f"正文数值 token 英文 {counts['tokens_en']} : 中文 {counts['tokens_zh']}"),
            ("118 项单元测试通过", f"{counts['tests']} 项单元测试通过"),
            ("运行 118 项测试、编译全部源码", f"运行 {counts['tests']} 项测试、编译全部源码"),
        ],
        BASE / "研究缺口审计与优先级清单.md": [
            (snapshot_old, snapshot_new),
            ("约 10 800 词、11 图、10 表",
             f"{spaced_words} 词、{counts['figures']} 图、{counts['tables']} 表"),
        ],
        BASE / "P0_P1执行手册.md": [(snapshot_old, snapshot_new)],
        BASE / "论文结构诊断与重构方案.md": [(snapshot_old, snapshot_new)],
    }
    for path, pairs in edits.items():
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            if old == new:
                continue
            if old in text:
                if text.count(old) != 1:
                    raise SystemExit(f"{path.name}: anchor not unique: {old!r}")
                text = text.replace(old, new, 1)
            elif new not in text:
                raise SystemExit(f"{path.name}: neither the old nor the new text is present: "
                                 f"{old!r}")
        path.write_text(text, encoding="utf-8")
        print(f"updated {path.name}")

    # README announces the gate size as "(N checks"; the number there changes
    # whenever a check is added, so it is rewritten by pattern rather than by
    # anchor.
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    new_text, changes = re.subn(r"\(\d+ checks", f"({counts['gate_checks']} checks", text)
    if changes != 1:
        raise SystemExit(f"README.md declares the gate size {changes} times, expected once")
    if new_text != text:
        readme.write_text(new_text, encoding="utf-8")
        print(f"updated README.md ({counts['gate_checks']} checks)")

    # the guard is the authority: run it again and require it to pass
    if checker.main() != 0:
        raise SystemExit("the counts still disagree after the edit")
    print(f"counts: {counts['tests']} tests, {counts['gate_checks']} gate checks, "
          f"{counts['en_words']:,} English words, {counts['zh_chars']:,} Chinese characters, "
          f"{counts['figures']} figures, {counts['tables']} tables, "
          f"{counts['sc_items']}/{counts['sc_passed']}/{counts['sc_partial']} self-check items, "
          f"{counts['tokens_en']}:{counts['tokens_zh']} numeric tokens")
    print("DELIVERABLE_COUNTS_FIXED")


if __name__ == "__main__":
    main()
