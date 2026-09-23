"""Check the manuscript against the verified JISA Guide for Authors limits.
The limits are the ones recorded in docs/jisa_requirements_verified_2026-09-05.md:
abstract at most 250 words, 1-7 keywords, Highlights of 3-5 items within 85
characters, numbered equations, and a graphical abstract of at least 531 x 1328
pixels (height x width).
"""
from __future__ import annotations
import re
import struct
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")
def section(text: str, start: str, stop: str) -> str:
    return text.split(start, 1)[1].split(stop, 1)[0].strip()
def abstract_only(text: str, start: str, stop: str, keyword_marker: str) -> str:
    body = section(text, start, stop)
    return body.split(keyword_marker)[0].strip()
def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        head = handle.read(24)
    width, height = struct.unpack(">II", head[16:24])
    return width, height
def main() -> int:
    problems: list[str] = []
    abstract = abstract_only(EN, "## Abstract", "\n## ", "**Keywords:**")
    words = len(abstract.split())
    print(f"abstract: {words} words (limit 250)")
    if words > 250:
        problems.append(f"abstract is {words} words, limit is 250")
    zh_chars = len(re.sub(r"\s", "", abstract_only(ZH, "## 摘要", "\n## ", "**关键词：**")))
    print(f"Chinese abstract: {zh_chars} characters")
    for label, text, pattern in (("EN", EN, r"\*\*Keywords:\*\*\s*(.+)"),
                                 ("ZH", ZH, r"\*\*关键词：\*\*\s*(.+)"),
                                 ):
        line = re.search(pattern, text)
        count = len([k for k in re.split(r"[;；]", line.group(1)) if k.strip()]) if line else 0
        print(f"keywords ({label}): {count} (limit 1-7)")
        if not 1 <= count <= 7:
            problems.append(f"{label} keywords: {count}")
    highlights = [l for l in (BASE / "Highlights_v4.md").read_text("utf-8").splitlines()
                  if l.startswith("- ")]
    english = highlights[:5]
    longest = max((len(l) - 2) for l in english) if english else 0
    print(f"highlights: {len(english)} items, longest {longest} chars (limit 3-5 items, 85 chars)")
    if not 3 <= len(english) <= 5:
        problems.append(f"highlights count {len(english)}")
    if longest > 85:
        problems.append(f"highlight of {longest} characters exceeds 85")
    for label, text in (("EN", EN), ("ZH", ZH)):
        numbers = [int(m) for m in re.findall(r"\$\$.+?\((\d+)\)\$\$", text)]
        print(f"equations ({label}): {numbers}")
        if numbers != list(range(1, len(numbers) + 1)) or not numbers:
            problems.append(f"{label} equations are not numbered sequentially: {numbers}")
    width, height = png_size(BASE / "Graphical_Abstract_v4.png")
    print(f"graphical abstract: {width} x {height} px (minimum width 1328, height 531)")
    if width < 1328 or height < 531:
        problems.append(f"graphical abstract is {width}x{height}")
    for label, text, heading in (("EN", EN, "## Supplementary material"),
                                 ("ZH", ZH, "## 补充材料清单")):
        # Derive the required range from the manuscript's own list instead of
        # hard-coding it: the check silently stopped at S26 when S27-S29 were
        # added, so three items were never verified to be cited from the text.
        body, _, listing = text.partition(heading)
        listed = [int(m) for m in re.findall(r"^\| S(\d{2}) \|", listing, flags=re.M)]
        cited: set[int] = set()
        for first, last in re.findall(r"S(\d{2})\s*[-–]\s*S?(\d{2})", body):
            cited.update(range(int(first), int(last) + 1))
        cited.update(int(m) for m in re.findall(r"S(\d{2})", body))
        missing = [n for n in listed if n not in cited]
        print(f"supplementary items cited in the {label} text: "
              f"{len(listed) - len(missing)}/{len(listed)}")
        if missing:
            problems.append(f"{label} text never cites supplementary {missing}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("JISA_FORMAT_MISMATCH")
        return 1
    print("JISA_FORMAT_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
