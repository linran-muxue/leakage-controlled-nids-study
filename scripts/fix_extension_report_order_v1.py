"""Emit the 2026 corpus section after the Gotham section, not before it."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "scripts" / "build_extension_report_v1.py"
START = "    y2026 = []\n"
END = '    full = read_json(ROOT / "results_rccf_gotham2025_v1" / "benchmark_summary.json")\n'
DEST = '    text = "\\n".join(lines) + "\\n"\n'


def main() -> None:
    text = REPORT.read_text(encoding="utf-8")
    # an earlier partial run left two copies of the 2026 block; keep one
    while text.count(START) > 1:
        first = text.index(START)
        second = text.index(START, first + 1)
        following = text.index(DEST, second)
        text = text[:second] + text[following:]
        print("build_extension_report_v1.py: duplicate 2026 block removed")
    REPORT.write_text(text, encoding="utf-8")
    text = REPORT.read_text(encoding="utf-8")
    if text.index(START) > text.index(END):
        print("build_extension_report_v1.py: order already fixed")
        return
    block = text[text.index(START):text.index(END)]
    text = text.replace(block, "", 1)
    if text.count(DEST) != 1:
        raise SystemExit("destination anchor is not unique")
    text = text.replace(DEST, block + DEST, 1)
    REPORT.write_text(text, encoding="utf-8")
    print("build_extension_report_v1.py: 2026 section moved after Gotham")


if __name__ == "__main__":
    main()
