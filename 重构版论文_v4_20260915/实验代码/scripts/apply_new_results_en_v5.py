"""Add resource profile, cost-sensitive analysis and near-duplicate disclosure (English)."""
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
    text = MD.read_text(encoding="utf-8")

    # Section 5.6: resource footprint and cost-sensitive behaviour
    anchor = ("**Open-set behaviour.** With PortScan, Infiltration and Heartbleed held out as unknown families,")
    addition = (
        "**Resource footprint.** Model size and throughput separate the two designs more sharply than wall-clock "
        "time. The conditional mechanism stores four forests and occupies 9.09 MB when serialised, against 2.21 MB "
        "for the single equal-weight forest - a factor of 4.1 - and it processes about 43,100 rows per second on a "
        "full test batch against 200,300, a factor of 4.6. Peak resident-set growth during fitting was 37.0 MB "
        "against 78.3 MB, but the two models were profiled within one process, so that particular figure is "
        "order-dependent and indicative only.\n\n"
        "**Cost-sensitive behaviour.** Casting the task as attack versus normal and sweeping the decision threshold "
        "for cost ratios C_FN / C_FP from 1 to 100, the normalised expected cost of the conditional mechanism "
        "tracks the equal-weight chi-square forest to within 0.0005 across the whole range - for example 0.00913 "
        "against 0.00867 at ratio 1, and 0.07260 against 0.06753 at ratio 100. Extremely randomised trees are about "
        "twice as costly at low ratios (0.01917 at ratio 1) but become cheaper than both forests once false "
        "negatives dominate (0.06180 at ratio 100). The conditional gate therefore offers no cost-sensitive "
        "advantage either.\n\n"
    )
    text = fix(text, anchor, addition + anchor, "5.6-resources")

    # Section 6.5: near-duplicate disclosure and adversarial scope
    limit_anchor = "**Unknown-family support is uneven.**"
    limits = (
        "**Near-duplicates are removed only in their exact form.** The introduction identifies near-duplicate flows "
        "as a hazard of public datasets, and the audit removes exact duplicate feature vectors. Rounding every "
        "feature to four significant digits and hashing the result shows that a further 0.36% of the study "
        "population forms near-duplicate groups at that resolution, and that 104 test rows (0.21% of the test set) "
        "share a rounded feature vector with a training row. Removing those rows changes Macro-F1 by at most "
        "0.00057 for any of the three models, so the overlap cannot explain the reported differences; coarser "
        "resolutions are reported in the supplementary material.\n\n"
        "**Adversarial robustness was not assessed.** Only random perturbations and feature masking were applied. "
        "No evasion or gradient-based attack was constructed, and the reported degradation figures are not "
        "robustness guarantees against an adaptive adversary.\n\n"
    )
    text = fix(text, limit_anchor, limits + limit_anchor, "6.5-limits")

    # abstract: add the resource/cost clause
    abs_anchor = ("The contribution is a reusable leakage-controlled protocol, an identifiability boundary and a "
                  "quantitative map that separates protocol effects from model effects;")
    text = fix(text, abs_anchor,
               "The conditional mechanism is 4.1 times larger and 4.6 times slower per row than a single "
               "equal-weight forest, and its cost-sensitive behaviour matches that forest across false-negative to "
               "false-positive cost ratios from 1 to 100. " + abs_anchor, "abstract-cost")

    MD.write_text(text, encoding="utf-8")
    print("EN_NEW_RESULTS_APPLIED")


if __name__ == "__main__":
    main()
