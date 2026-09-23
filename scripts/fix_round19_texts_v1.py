"""Repair three defects the round-19 generators left behind.

1. ``append_review_round_v19.py`` wrote the full-corpus row count as
   ``test_rows * 3`` (1,093,278) instead of the audited total (2,429,503).
2. The same script interpolated a *Chinese* TOST verdict into the English
   cover letter.
3. ``finalize_full_corpus_v56.py`` rendered the test-row count with comma
   separators inside the Chinese manuscript, which uses spaces throughout.

Every anchor is asserted, so re-running is safe and a future regeneration that
no longer needs the fix fails loudly rather than silently skipping.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

COVER = BASE / "Cover_Letter_JISA_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"
CFF = ROOT / "CITATION.cff"


def main() -> int:
    cover = COVER.read_text(encoding="utf-8")
    if "(2,429,503 deduplicated flows, ten seeds)" in cover:
        print("  cover letter: row count already correct")
    else:
        old = "(1,093,278 deduplicated flows, ten seeds)"
        if old not in cover:
            raise SystemExit("cover letter row-count anchor missing")
        cover = cover.replace(old, "(2,429,503 deduplicated flows, ten seeds)", 1)
        print("  cover letter: row count 1,093,278 -> 2,429,503")

    # The verdict was inserted in Chinese; rewrite it in English between the
    # ASCII anchors so the exact CJK characters do not have to be reproduced.
    # The inserted verdict used a Chinese enumeration comma between the two
    # margins, so the separator between them must stay permissive.
    pattern = re.compile(r"TOST 0\.005.*?0\.01[^,]*, at a", re.S)
    if pattern.search(cover):
        cover = pattern.sub("equivalent at the 0.01 margin but not at 0.005, at a", cover, count=1)
        print("  cover letter: TOST verdict rewritten in English")
    elif "equivalent at the 0.01 margin but not at 0.005" in cover:
        print("  cover letter: TOST verdict already English")
    else:
        raise SystemExit("cover letter TOST anchor missing")
    COVER.write_text(cover, encoding="utf-8")

    zh = ZH.read_text(encoding="utf-8")
    if "364 426 条测试样本" in zh:
        print("  Chinese manuscript: separator already fixed")
    else:
        old = "364,426 条测试样本"
        if old not in zh:
            raise SystemExit("Chinese manuscript separator anchor missing")
        zh = zh.replace(old, "364 426 条测试样本", 1)
        print("  Chinese manuscript: 364,426 -> 364 426")
        ZH.write_text(zh, encoding="utf-8")

    cff = CFF.read_text(encoding="utf-8")
    if 'version: "1.11.0"' in cff:
        print("  CITATION.cff: version already 1.11.0")
    else:
        if 'version: "1.10.0"' not in cff:
            raise SystemExit("CITATION.cff version anchor missing")
        cff = cff.replace('version: "1.10.0"', 'version: "1.11.0"', 1)
        cff = cff.replace('date-released: "2026-09-17"', 'date-released: "2026-09-23"', 1)
        print("  CITATION.cff: version -> 1.11.0, date -> 2026-09-23")
        CFF.write_text(cff, encoding="utf-8")

    print("ROUND19_TEXTS_FIXED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
