"""Align the cover letter with the narrowed headline claim."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "Cover_Letter_JISA_v4.md"


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    old_title = "Protocol Sensitivity Dominates Model Choice in Flow-Based Network Intrusion Detection"
    new_title = ("Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network "
                 "Intrusion Detection")
    if old_title not in text:
        raise SystemExit("title anchor missing")
    text = text.replace(old_title, new_title)
    anchor = "with the per-seed sign split five to five."
    addition = ("with the per-seed sign split five to five. The headline ordering concerns the aggregation rule: "
                "its effect is an order of magnitude below the protocol effects we measure (class prior 0.0725, "
                "tuning budget 0.0078, deduplication order up to 0.0060). Model-family differences are larger "
                "still, and the paper says so - the multilayer perceptron trails the forests by 0.0916 Macro-F1 "
                "and extremely randomised trees by 0.0318.")
    if anchor in text and "The headline ordering concerns" not in text:
        text = text.replace(anchor, addition, 1)
    MD.write_text(text, encoding="utf-8")
    print("COVER_LETTER_ALIGNED")


if __name__ == "__main__":
    main()
