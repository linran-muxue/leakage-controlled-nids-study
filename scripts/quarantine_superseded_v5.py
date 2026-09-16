"""Move superseded result files into a clearly labelled folder (audit finding G2)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "superseded"

FILES = [
    "results_publication_final/deployment/robustness_metrics.csv",
    "results_unified_final/deployment/robustness_metrics.csv",
    "results_publication_stage2/deployment/robustness_metrics.csv",
    "results_recheck_unified_v4/deployment/robustness_metrics.csv",
    "results_paper_materials_v2/tables/table_v2_robustness.csv",
]

NOTE = """# Superseded artifacts

The files below were produced under an **earlier robustness protocol** (tree-level
weighted forest, separate perturbation seeds per model) and are **not** the source of
any number in the current manuscript. They are kept only for provenance.

The manuscript reports robustness from `results_rccf_evidence_v3b/robustness_shared.csv`,
which applies an identical perturbation mask to every model. Under the old protocol the
gap between the weighted forest and extremely randomised trees reaches about 0.12
Macro-F1; under the shared-mask protocol used in the paper the corresponding gaps are
43.30% versus 11.57% relative degradation for 1% Gaussian noise. The two protocols must
not be mixed.

| File | Reason |
|---|---|
{rows}
"""


def main() -> None:
    DEST.mkdir(exist_ok=True)
    rows = []
    moved = 0
    for rel in FILES:
        src = ROOT / rel
        if not src.exists():
            rows.append(f"| {rel} | not present |")
            continue
        target = DEST / rel.replace("/", "__")
        shutil.move(str(src), str(target))
        rows.append(f"| {rel} | superseded robustness protocol |")
        moved += 1
    (DEST / "README.md").write_text(NOTE.format(rows="\n".join(rows)), encoding="utf-8")
    print(f"QUARANTINED={moved}")


if __name__ == "__main__":
    main()
