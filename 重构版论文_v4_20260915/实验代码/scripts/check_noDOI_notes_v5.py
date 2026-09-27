"""Verify that every 'no DOI' annotation names the correct venue."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
block = EN.split("## References")[-1]
for number, entry in re.findall(r"^(\d+)\.\s+(.*)$", block, flags=re.M):
    if "no DOI" in entry:
        note = re.search(r"\[no DOI[^\]]*\]", entry)
        venue = ""
        for candidate in ("NeurIPS", "JMLR", "PMLR", "USENIX", "Scandinavian", "ICML",
                          "Chapman", "IEEE", "KDD"):
            if candidate.lower() in entry.lower():
                venue = candidate
                break
        note_text = note.group(0) if note else ""
        # A JSTOR stable identifier is the correct handle for the 1979 Scandinavian
        # Journal of Statistics article, so accept it for that venue.
        accepted = venue.lower() in note_text.lower() or (
            venue == "Scandinavian" and "jstor" in note_text.lower())
        consistent = accepted if venue else None
        flag = "OK " if consistent else ("CHECK" if venue else "n/a")
        print(f"[{number:>2}] {flag:<5} venue={venue:<14} note={note_text:<40} | {entry[:60]}")
