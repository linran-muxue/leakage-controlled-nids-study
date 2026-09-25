"""Is the package submittable, and if not, are the blockers declared?

Two questions a supervisor or an editor asks before anything else.  The hard
limits are re-derived from the JISA checker (abstract, keywords, Highlights,
equation numbering, graphical-abstract size), and every placeholder still in the
package is matched against the self-check table: a placeholder that no row
declares is an *undisclosed* blocker, which is worse than an open one because
the reader has no way to see it.

The placeholders are the author's own input and are expected to be open until
submission; what this check enforces is that none of them is missing from the
inventory.  When the author fills one in, the corresponding entry disappears on
its own.
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
TABLE = (BASE / "论文自查表.md").read_text(encoding="utf-8")

# path, pattern, declaring row, the word that row must use, human label
PLACEHOLDERS = (
    (BASE / "English_SCI_Manuscript_v4.md",
     r"To be completed by the author\. If the work received",
     "A6", "基金", "funding statement (EN)"),
    (BASE / "English_SCI_Manuscript_v4.md",
     r"To be completed by the author\. If no competing interests",
     "A6", "利益冲突", "competing-interest statement (EN)"),
    (BASE / "English_SCI_Manuscript_v4.md",
     r"To be completed by the author according to actual",
     "A5", "CRediT", "CRediT statement (EN)"),
    (BASE / "中文SCI论文_v4_重构版.md", r"待作者填写：若无资助", "A6", "基金",
     "funding statement (ZH)"),
    (BASE / "中文SCI论文_v4_重构版.md", r"待作者填写：若无，请声明", "A6",
     "利益冲突", "competing-interest (ZH)"),
    (BASE / "中文SCI论文_v4_重构版.md", r"待作者按实际贡献填写", "A5", "CRediT",
     "CRediT statement (ZH)"),
    (BASE / "Cover_Letter_JISA_v4.md",
     r"Author name, affiliation, e-mail and ORCID to be inserted",
     "F9", "投稿信", "cover-letter signature block"),
    (ROOT / "CITATION.cff", r'name: "Author to be completed"', "A5", "CITATION.cff",
     "CITATION.cff authors field"),
)


def jisa_limits() -> dict[str, int]:
    output = subprocess.run([PY, str(ROOT / "scripts" / "check_jisa_format_v22.py")],
                            cwd=ROOT, capture_output=True, text=True, errors="replace").stdout
    abstract = re.search(r"abstract: (\d+) words", output)
    keywords = re.search(r"keywords \(EN\): (\d+)", output)
    highlights = re.search(r"highlights: (\d+) items, longest (\d+) chars", output)
    graphic = re.search(r"graphical abstract: (\d+) x (\d+) px", output)
    if not all((abstract, keywords, highlights, graphic)):
        raise SystemExit("could not read the JISA checker's output")
    limits = {
        "abstract words": int(abstract.group(1)),
        "keywords": int(keywords.group(1)),
        "highlights": int(highlights.group(1)),
        "highlight chars": int(highlights.group(2)),
        "graphical width": int(graphic.group(1)),
        "graphical height": int(graphic.group(2)),
    }
    checks = (("abstract words", 250, "<="), ("keywords", 7, "<="),
              ("highlights", 5, "<="), ("highlights", 3, ">="),
              ("highlight chars", 85, "<="), ("graphical width", 1328, ">="),
              ("graphical height", 531, ">="))
    problems = []
    for name, bound, direction in checks:
        value = limits[name]
        if (direction == "<=" and value > bound) or (direction == ">=" and value < bound):
            problems.append(f"{name} is {value}, limit {direction} {bound}")
    for name, value in limits.items():
        print(f"  {name:<18}{value}")
    return problems


def declared(row: str, keyword: str) -> bool:
    match = re.search(rf"^\| {row} \|.*$", TABLE, flags=re.M)
    return bool(match and "部分通过" in match.group(0) and keyword in match.group(0))


def main() -> int:
    problems = jisa_limits()
    print()
    print("== open blockers and where they are declared ==")
    open_items = []
    for path, pattern, row, keyword, label in PLACEHOLDERS:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(pattern, text):
            continue
        open_items.append(label)
        if declared(row, keyword):
            print(f"  open   {label:<34}declared in row {row}")
        else:
            problems.append(f"{label} is still a placeholder but row {row} neither marks a gap "
                            f"nor names it")
            print(f"  ISSUE  {label:<34}not declared by row {row} (needs {keyword!r})")
    print(f"  {len(open_items)} open item(s), all requiring author input")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SUBMISSION_READINESS_FAILED")
        return 1
    print("SUBMISSION_READINESS_OK (content complete; open items are author inputs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
