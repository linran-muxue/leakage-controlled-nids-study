"""Diagnose remaining DOI markers."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
    text = (BASE / name).read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if ("[DOI" in l)]
    print(f"{name}: lines containing '[DOI' = {len(lines)}")
    for l in lines[:15]:
        print("   ", l[-70:])
