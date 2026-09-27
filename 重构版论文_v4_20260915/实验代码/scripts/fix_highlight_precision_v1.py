"""Use the exact full-corpus difference in the Highlights and the GA.

The summary documents must quote a number the manuscript actually contains;
``check_aux_documents_v13.py`` enforces that and rejected the rounded 0.00553.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

TARGETS = [
    (BASE / "Highlights_v4.md", [
        ("loses 0.00553 on the full corpus", "loses 0.005533 on the full corpus"),
        ("全语料上反而落后 0.00553", "全语料上反而落后 0.005533"),
    ]),
    (ROOT / "scripts" / "build_graphical_abstract_v5.py", [
        ("(-0.0055)", "(-0.005533)"),
    ]),
]


def main() -> int:
    for path, pairs in TARGETS:
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            if new in text:
                print(f"  [{path.name}] already: {new[:40]}")
                continue
            if old not in text:
                raise SystemExit(f"anchor missing in {path.name}: {old}")
            text = text.replace(old, new, 1)
            print(f"  [{path.name}] {old} -> {new}")
        path.write_text(text, encoding="utf-8")
    print("HIGHLIGHT_PRECISION_FIXED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
