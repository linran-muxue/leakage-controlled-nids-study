"""Repair DOI tokens that carry non-ASCII or stray trailing punctuation.
Reference 19 of the Chinese manuscript ended with a full-width semicolon glued
to the DOI, so copy-pasting it into a browser fails to resolve. This script
normalises every DOI token to ASCII and reports what it changed.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DOI = re.compile(r"DOI:\s*(10\.[^\s]*?)([.;,;、。，；]*)\s*$", flags=re.M)
def clean(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    def repl(match: re.Match) -> str:
        doi = match.group(1)
        trimmed = doi.rstrip(".;,;、。，；")
        # drop any non-ASCII residue that follows the DOI
        trimmed = "".join(ch for ch in trimmed if ord(ch) < 128) or doi
        if trimmed != doi or match.group(2):
            changes.append(f"{doi}{match.group(2)} -> {trimmed}")
        return f"DOI:{trimmed}"
    return DOI.sub(repl, text), changes
def main() -> None:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        new, changes = clean(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
        print(f"{name}: {len(changes)} DOI token(s) normalised")
        for change in changes:
            print(f"    {change}")
if __name__ == "__main__":
    main()
