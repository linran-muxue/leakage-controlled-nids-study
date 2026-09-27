"""Complete the submission-readiness inventory in the self-check table.

Two gaps, both found by ``check_submission_readiness_v1.py``:

1. ``CITATION.cff`` still carries ``name: "Author to be completed"``.  The
   self-check table declared the manuscript's CRediT placeholder (row A5) and
   the cover letter's signature block (row F9), but nothing named the CFF, so a
   reader inventorying the author inputs would have missed one.
2. Row E10 quoted the longest Highlight as 83 characters; the longest is 84
   ("Weighting matches equal voting on capped data but loses 0.005533 on the
   full corpus."), inside the 85-character limit either way but wrong as stated.

Both are recomputed here rather than typed in.
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
TABLE = BASE / "论文自查表.md"
CFF = ROOT / "CITATION.cff"
HIGHLIGHTS = BASE / "Highlights_v4.md"


def measured_highlight_length() -> int:
    text = HIGHLIGHTS.read_text(encoding="utf-8")
    english = text.partition("# 中文要点")[0]
    items = [line[2:].strip() for line in english.splitlines() if line.startswith("- ")]
    return max(len(item) for item in items)


def main() -> None:
    if 'name: "Author to be completed"' not in CFF.read_text(encoding="utf-8"):
        raise SystemExit("CITATION.cff no longer carries the placeholder; update the check")
    longest = measured_highlight_length()
    print(f"source: CITATION.cff authors are a placeholder; longest Highlight is {longest} chars")

    text = TABLE.read_text(encoding="utf-8")
    edits = (
        ("| A5 | 署名与 CRediT | 章节存在且内容完整 | **部分通过** | 两版均含 CRediT 章节，"
         "但内容为占位符（待作者填写） |",
         "| A5 | 署名与 CRediT | 章节存在且内容完整 | **部分通过** | 两版均含 CRediT 章节，"
         "但内容为占位符（待作者填写）；仓库根目录 `CITATION.cff` 的 authors 字段同为占位符"
         "「Author to be completed」 |"),
        ("| A5 | 署名、单位、通信作者、ORCID | 按投稿系统字段填写 | 作者 |",
         "| A5 | 署名、单位、通信作者、ORCID，以及 `CITATION.cff` 的 authors 字段 | "
         "按投稿系统字段填写 | 作者 |"),
        ("Highlights 5 条且最长 83 字符（上限 85）",
         f"Highlights 5 条且最长 {longest} 字符（上限 85）"),
    )
    for old, new in edits:
        if old in text:
            if text.count(old) != 1:
                raise SystemExit(f"anchor not unique: {old[:40]!r}")
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"neither the old nor the new text is present: {old[:40]!r}")
    TABLE.write_text(text, encoding="utf-8")
    print("updated 论文自查表.md")

    check = subprocess.run([PY, str(ROOT / "scripts" / "check_submission_readiness_v1.py")],
                           cwd=ROOT, capture_output=True, text=True, errors="replace")
    print(check.stdout.strip().splitlines()[-1])
    if check.returncode != 0:
        raise SystemExit("readiness check still fails")
    print("READINESS_INVENTORY_FIXED")


if __name__ == "__main__":
    main()
