"""List the longest sentences in the manuscript body."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
body = EN.split("## 1. Introduction")[-1].split("## References")[0]
sents = [s.strip() for s in re.split(r"(?<=[.])\s+", re.sub(r"\s+", " ", body)) if len(s.split()) > 8]
scored = sorted(sents, key=lambda s: -len(s.split()))
for s in scored[:12]:
    print(f"[{len(s.split())}w] {s}\n")
