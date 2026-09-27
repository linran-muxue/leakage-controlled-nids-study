"""Bring the Highlights and the cover letter back into line with the manuscript.
Both were written while the manuscript still said 3,500, 0.073 and v1.2.0, and
the cover letter still carried the pre-narrowing claim that protocol effects
exceed model effects. None of these were caught because every earlier check
read the manuscript only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
TAG = "v1.11.0"
EDITS: dict[str, list[tuple[str, str]]] = {
    "Highlights_v4.md": [
        ("- Protocol choices move Macro-F1 by 0.073, against 0.0005 for the aggregation rule.",
         "- Protocol choices move Macro-F1 by 0.0725, against 0.0005 for the aggregation rule."),
        ("- 类别先验带来的差异为 0.073，而聚合策略仅 0.0005。",
         "- 类别先验带来的差异为 0.0725，而聚合策略仅 0.0005。"),
    ],
    "Cover_Letter_JISA_v4.md": [
        ("with decision margins roughly 3,500 times that bound",
         "with a median decision margin 3,469 to 5,038 times that bound"),
        ("(release v1.2.0, tag v1.2.0)", f"(release {TAG}, tag {TAG})"),
        ("a quantitative map showing that protocol effects exceed model effects by an order of magnitude",
         "a quantitative map showing that protocol choices exceed aggregation-rule differences by an "
         "order of magnitude, while model-family differences remain larger still"),
    ],
}
def main() -> None:
    total = 0
    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        applied = 0
        for old, new in edits:
            if old in text:
                text = text.replace(old, new, 1)
                applied += 1
            else:
                print(f"  [{name}] anchor absent: {old[:52]}...")
        path.write_text(text, encoding="utf-8")
        print(f"{name}: {applied}/{len(edits)} applied")
        total += applied
    print(f"AUX_ALIGNED={total}")
if __name__ == "__main__":
    main()
