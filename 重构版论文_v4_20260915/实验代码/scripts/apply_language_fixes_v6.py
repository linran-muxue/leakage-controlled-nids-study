"""Sentence-length and terminology clean-up for the English manuscript."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    t = MD.read_text(encoding="utf-8")

    t = fix(t,
            "This yields the most important mechanistic conclusion of the study: **the gain of conditional "
            "weighting is governed by expert diversity; on flow-feature data, \"multi-view\" experts built from "
            "different filter selectors disagree on only 0.2%-0.4% of samples, so the gate is structurally "
            "incapable of producing a gain.**",
            "This yields the most important mechanistic conclusion of the study: **the gain of conditional "
            "weighting is governed by expert diversity.** On flow-feature data, \"multi-view\" experts built from "
            "different filter selectors disagree on only 0.2%-0.4% of samples, so the gate is structurally "
            "incapable of producing a gain.",
            "mech-sentence")

    t = fix(t,
            "the Macro-F1 difference between conditional weighting and an equal-weight chi-square forest is "
            "-0.000456 with the per-seed sign split five to five; both the seed-level 90% interval",
            "the Macro-F1 difference between conditional weighting and an equal-weight chi-square forest is "
            "-0.000456, with the per-seed sign split five to five. Both the seed-level 90% interval",
            "conclusion-sentence")

    t = fix(t, "starts at 0.75 in order to display", "starts at 0.75 to display", "in-order-to")

    t = fix(t, "expert e in {full, chi2, MI, ANOVA}, with Q = 4 experts",
            "expert e in {full, chi-square, MI, ANOVA}, with Q = 4 experts", "chi2-prose")

    MD.write_text(t, encoding="utf-8")
    print("LANGUAGE_FIXES_APPLIED")


if __name__ == "__main__":
    main()
