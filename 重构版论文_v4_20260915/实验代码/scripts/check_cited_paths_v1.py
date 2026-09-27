"""Every file a current-state deliverable cites must exist.

The self-check table names the artefact behind every check, and the repository
notes cite the scripts they describe, so a path that has been renamed or deleted
turns a claim of evidence into a claim a reader cannot follow.  One such pointer
had rotted: row C1 cited ``final_config.json``, which exists nowhere in the
repository - the gate configuration is now
``results_gate_tuning_v5/selected_gate_config.json``, shipped as S16.

The four dated snapshots - the review report, the gap audit, the P0/P1 execution
manual and the structure plan - are deliberately excluded.  They record what was
planned or found on a particular date and name scripts that were later built
under different names ("create scripts/analyze_expert_diversity_v5.py" and so
on), which is the point of keeping them.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUNDLE = BASE / "补充材料_S01_S30"
SEARCH = (ROOT, BASE, ROOT / "scripts", ROOT / "docs", ROOT / "results_review_v5", BUNDLE)
DELIVERABLES = ("论文自查表.md", "README.md", "DATA_CARD.md", "MODEL_CARD.md")
PATH = re.compile(r"`([A-Za-z0-9_./\\\-\u4e00-\u9fff]+\.(?:py|csv|json|md|txt|cff|yml|yaml|sha256|png|pdf|docx))`")


def resolve(token: str) -> list[Path]:
    cleaned = token.replace("\\", "/")
    return [base / cleaned for base in SEARCH if (base / cleaned).exists()]


def main() -> int:
    problems: list[str] = []
    for name in DELIVERABLES:
        location = (BASE / name) if name.endswith(".md") and name.startswith("论文") else (ROOT / name)
        if not location.exists():
            problems.append(f"{name} is missing")
            continue
        text = location.read_text(encoding="utf-8")
        tokens = sorted(set(PATH.findall(text)))
        missing = [token for token in tokens if not resolve(token)]
        print(f"{name}: {len(tokens)} cited path(s), {len(missing)} unresolved")
        for token in missing:
            print(f"  ISSUE {token}")
            problems.append(f"{name} cites {token}, which does not exist")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("CITED_PATHS_FAILED")
        return 1
    print("CITED_PATHS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
