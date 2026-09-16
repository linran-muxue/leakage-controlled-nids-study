"""List the references that were flagged for DOI verification."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "results_review_v5" / "doi_verification.json").read_text("utf-8"))
for r in rows:
    if r["doi_pending_flag"]:
        print(f"[{r['ref']:>2}] overlap={r['title_overlap']:<5} doi={r['crossref_doi']:<38} {r['crossref_title'][:60]}")
