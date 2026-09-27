"""Fixes from the full read-through review (English side)."""
from __future__ import annotations

import re
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

    # 1. duplicate header row in Table 4(a)
    dup = ("| Model | Accuracy | Balanced accuracy | Macro-F1 | Log Loss | Brier | ECE | Train (s) | Predict (s) |\n"
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
           "| Model | Accuracy | Balanced accuracy | Macro-F1 | Log Loss | Brier | ECE | Train (s) | Predict (s) |\n"
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    single = ("| Model | Accuracy | Balanced accuracy | Macro-F1 | Log Loss | Brier | ECE | Train (s) | Predict (s) |\n"
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    if dup in t:
        t = t.replace(dup, single, 1)
    print("table4a duplicate header removed:", dup not in t)

    # 2. Fourth reading: reconcile the timing figures with the ten-seed table
    t = fix(t,
            "**Fourth, the cost is certain while the gain is not.** On the natural-prior protocol RCCF takes 61.0 s "
            "to train against 0.78 s for the equal-weight forest, and 0.244 s to predict against 0.046 s on a whole "
            "test batch, about 5.3 times slower. The two ratios measure different quantities and must not be "
            "conflated: 5.9 is the batch prediction-time ratio, whereas the single-row P50 latency ratio reported in "
            "Section 5.6 is 4.9 (14.62 ms against 2.96 ms). The gap widens on the balanced control: 9.13 s against "
            "0.45 s. The most favourable summary of what these costs buy is that Macro-F1 moves within +/- 0.01.",
            "**Fourth, the cost is certain while the gain is not.** On the natural-prior protocol, averaged over the "
            "ten seeds of Table 4(a), RCCF takes 93.3 s to train against 1.16 s for the equal-weight forest, and "
            "0.244 s to predict against 0.046 s on a whole test batch - about 5.3 times slower at inference. That "
            "batch ratio must not be conflated with the single-row latency ratio of 4.9 reported in Section 5.6 "
            "(14.62 ms against 2.96 ms): one measures throughput on 7,986 rows, the other a single call. The gap "
            "widens on the balanced control, where training takes 9.13 s against 0.45 s. The most favourable summary "
            "of what these costs buy is that Macro-F1 moves within +/- 0.01.",
            "fourth-reading")

    # 3. contribution 3: five sources, not four
    t = fix(t, "On one experiment set we measure four sources of variation: aggregation (0.0005)",
            "On one experiment set we measure five sources of variation: aggregation (0.0005)", "contrib-five")

    # 4. section 2.5 positioning wording
    t = fix(t, "(iii) the relative magnitude of protocol and model effects",
            "(iii) the relative magnitude of protocol and aggregation-rule effects", "2.5-effects")

    # 5. Condition 3 dangling reference to an earlier formulation
    t = fix(t,
            "An earlier, purely definitional formulation used the normalised weight entropy",
            "The corresponding observable is the normalised weight entropy", "cond3-dangling")

    # 6. Table 5 commentary: two substantial gaps exist
    t = fix(t,
            "**Versus extremely randomised trees.** The difference is large and unambiguous (d_z = 19.7, all ten "
            "seeds), and is the only substantial model-to-model gap in this study.",
            "**Versus extremely randomised trees.** The difference is large and unambiguous (d_z = 19.7, all ten "
            "seeds). Together with the neural baseline of the fifth reading, these are the only substantial "
            "model-to-model gaps in this study; both concern the model family, not the aggregation rule.",
            "table5-comment")

    # 7. section 6.2 item 1: the claim must survive the larger model-family gaps
    t = fix(t,
            "1. **Split noise.** The split-to-split standard deviation over ten repetitions is about 0.011, enough to "
            "mask every model-to-model difference observed here (at most 0.0078).",
            "1. **Split noise.** The split-to-split standard deviation over ten repetitions is about 0.011. That is "
            "larger than every aggregation-rule and tuning-budget difference observed here (at most 0.0078), though "
            "not larger than the model-family gaps of 0.032 and 0.092.",
            "6.2-split")

    # 8. section 6.2 item 2: align the class-prior figure
    t = fix(t, "Changing the class prior from balanced to natural moves Macro-F1 by +0.0719",
            "Changing the class prior from balanced to natural moves Macro-F1 by +0.0725", "6.2-prior")

    # 9. conclusion headings and closing paragraph
    t = fix(t, "**Third, protocol effects dominate model effects.**",
            "**Third, protocol effects dominate aggregation-rule differences.**", "concl-head")
    t = fix(t, "a quantitative map that separates protocol effects from model effects.",
            "a quantitative map that separates protocol effects from aggregation-rule effects.", "concl-map")

    # 10. section 1.2 H3 phrasing
    t = fix(t, "H3 is the most consequential because it is never stated explicitly",
            "H3 is the most consequential because, in the literature, it is never stated explicitly",
            "1.2-h3")

    # 11. citations must precede the sentence-ending period
    before = len(re.findall(r"[a-z)]\. \[\d", t))
    t = re.sub(r"([a-z\)])\. \[(\d[\d,\- ]*)\]", r"\1 [\2].", t)
    after = len(re.findall(r"[a-z)]\. \[\d", t))
    print(f"citations moved before the period: {before} -> {after}")

    # 12. merge the two redundant label-space sentences in 3.3
    t = fix(t,
            "The three datasets use incompatible label spaces. Their scores are therefore never pooled, averaged or "
            "interpreted as evidence of transfer.",
            "Because these label spaces are incompatible, the three sets of scores are never pooled or averaged here, "
            "and they are never interpreted as evidence of transfer.", "3.3-merge")

    MD.write_text(t, encoding="utf-8")
    print("EN_READTHROUGH_FIXES_APPLIED")


if __name__ == "__main__":
    main()
