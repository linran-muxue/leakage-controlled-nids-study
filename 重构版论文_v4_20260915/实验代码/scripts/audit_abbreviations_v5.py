"""Check that abbreviations are expanded at first use."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

ABBR = {
    "en": ["RCCF", "SESOI", "ECE", "MCE", "TOST", "ANOVA", "MI", "AUROC", "AURC",
           "OOB", "CV", "RF", "MLP", "kNN", "IDS", "NIDS", "Mondrian", "Brier"],
    "zh": ["RCCF", "SESOI", "ECE", "TOST", "ANOVA", "AUROC", "AURC", "CV", "MLP", "kNN", "NIDS"],
}


def main() -> None:
    for label in ("en", "zh"):
        path = BASE / ("English_SCI_Manuscript_v4.md" if label == "en" else "中文SCI论文_v4_重构版.md")
        text = path.read_text(encoding="utf-8")
        body = text.split("## References")[0] if label == "en" else text.split("## 参考文献")[0]
        print(f"=== {label} ===")
        for a in ABBR[label]:
            first = body.find(a)
            if first < 0:
                print(f"  {a:<10} not used")
                continue
            window = body[max(0, first - 120):first + 120]
            expanded = bool(re.search(r"\(([^)]*" + re.escape(a) + r"[^)]*)\)", window))
            print(f"  {a:<10} first use at char {first:>6}  expanded nearby: {expanded}")
            if not expanded:
                print(f"      context: ...{window.strip()[:110]}...")


if __name__ == "__main__":
    main()
