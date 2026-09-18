"""Verify that every section cross-reference points at a real subsection.
The manuscripts cite sections constantly ("Section 5.3", "第 4.3 节", "§6.5").
After several rounds of renumbering nothing checked that those pointers still
land somewhere; a dangling pointer sends a reviewer to the wrong place.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_REF = re.compile(r"(?:Section|Sections|Sec\.)\s*(\d+(?:\.\d+)?)")
ZH_REF = re.compile(r"第\s*(\d+(?:\.\d+)?)\s*节")
def headings(text: str) -> set[str]:
    found = set()
    for line in text.splitlines():
        match = re.match(r"^#{2,3}\s+(\d+(?:\.\d+)?)", line)
        if match:
            found.add(match.group(1))
    return found
def main() -> int:
    problems: list[str] = []
    for name, pattern in (("English_SCI_Manuscript_v4.md", EN_REF),
                          ("中文SCI论文_v4_重构版.md", ZH_REF)):
        text = (BASE / name).read_text(encoding="utf-8")
        body = text.split("## References")[0].split("## 参考文献")[0]
        have = headings(text)
        refs: dict[str, int] = {}
        for number in pattern.findall(body):
            refs[number] = refs.get(number, 0) + 1
        dangling = sorted(n for n in refs if n not in have)
        print(f"{name}: {len(refs)} distinct section references, {len(have)} numbered headings")
        print(f"   referenced but missing: {dangling or 'none'}")
        for number in dangling:
            for line in body.splitlines():
                if pattern.search(line) and any(number == m for m in pattern.findall(line)):
                    print(f"      {number}: {line.strip()[:110]}")
                    break
        if dangling:
            problems.append(f"{name} cites missing sections {dangling}")
        defined = {m for m in re.findall(r"\$\$.+?\((\d+)\)\$\$", text)}
        if name.startswith("English"):
            # after each equation mention, also take numbers joined by "and"
            cited = set()
            for match in re.finditer(r"(?:Equations?|Eq\.?)\s*\((\d+)\)", body):
                cited.add(match.group(1))
                tail = body[match.end():match.end() + 24]
                cited.update(re.findall(r"\((\d+)\)", tail))
        else:
            cited = set()
            for match in re.finditer(r"式\s*\((\d+)\)", body):
                cited.add(match.group(1))
                tail = body[match.end():match.end() + 24]
                cited.update(re.findall(r"\((\d+)\)", tail))
        bad = sorted(cited - defined)
        print(f"   equation references {sorted(cited)} against defined {sorted(defined)}"
              f" -> missing {bad or 'none'}")
        if bad:
            problems.append(f"{name} cites missing equations {bad}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SECTION_REF_MISMATCH")
        return 1
    print("SECTION_REFS_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
