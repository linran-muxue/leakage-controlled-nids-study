"""End every reference DOI with an ASCII full stop and nothing else.
The first pass over-corrected and stripped the closing full stop from all 34
DOI-bearing entries (Elsevier's numbered style keeps it). This pass restores
the full stop while removing the non-ASCII characters that caused the original
problem: reference 19 of the Chinese manuscript ended with a full-width
semicolon glued to the DOI.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PATTERN = re.compile(r"DOI:\s*([^\s]+)\s*$", flags=re.M)
def fix(text: str) -> tuple[str, int]:
    changed = 0
    def repl(match: re.Match) -> str:
        nonlocal changed
        raw = match.group(1)
        doi = "".join(ch for ch in raw if ord(ch) < 128).rstrip(".;,;")
        if raw != doi + ".":
            changed += 1
        return f"DOI:{doi}."
    return PATTERN.sub(repl, text), changed
def main() -> None:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        new, changed = fix(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
        print(f"{name}: {changed} line(s) repaired, {len(PATTERN.findall(new))} DOI lines total")
if __name__ == "__main__":
    main()
