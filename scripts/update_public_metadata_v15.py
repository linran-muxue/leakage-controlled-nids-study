"""Update the public repository metadata that still cites the previous release.
README.md announced "Submission release: v1.0.2" and carried the title of a
manuscript that no longer exists (Provenance-Aware and Uncertainty-Aware...);
CITATION.cff still declared version 1.2.0. All three are read by anyone who
follows the code-availability statement in the paper, so they must match the
submission.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TAG = "v1.10.0"
TITLE_EN = ("Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based "
            "Network Intrusion Detection: A Leakage-Controlled Study of Conditional "
            "Ensemble Weighting")
README_EDITS = [
    ("Submission release: `v1.0.2` (tag present in the local checkout; verify the remote tag before submission)",
     f"Submission release: `{TAG}` (pushed to the remote; the archive cited in the manuscript availability statement)"),
    ("Reproducibility materials for the manuscript *Provenance-Aware and Uncertainty-Aware Evaluation of Network Intrusion Detection Models: A Cross-Fitted Risk-Gated Forest Study*.",
     f"Reproducibility materials for the manuscript *{TITLE_EN}*."),
    ("The exact release commit used for submission should be recorded in the manuscript and Manifest after the release is pushed.",
     f"The exact release commit used for submission is recorded in the manuscript availability statement and in "
     f"`results_publication_final/MANIFEST.json` (release `{TAG}`)."),
]
CFF_EDITS = [
    ('version: "1.2.0"', f'version: "1.10.0"'),
    ('date-released: "2026-09-16"', 'date-released: "2026-09-17"'),
    ('title: "Leakage-controlled evaluation of conditional ensemble weighting for flow-based network intrusion detection"',
     f'title: "Reproducibility archive for: {TITLE_EN}"'),
]
def apply(name: str, edits: list[tuple[str, str]]) -> None:
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            print(f"  [{name}] anchor absent: {old[:60]}...")
    path.write_text(text, encoding="utf-8")
    print(f"{name}: {applied}/{len(edits)} applied")
def main() -> None:
    apply("README.md", README_EDITS)
    apply("CITATION.cff", CFF_EDITS)
if __name__ == "__main__":
    main()
