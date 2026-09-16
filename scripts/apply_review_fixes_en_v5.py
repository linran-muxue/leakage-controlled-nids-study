"""Apply the audit fixes to the English manuscript (rounds 1-3)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    if text.count(old) != 1:
        print(f"  note: anchor '{label}' occurs {text.count(old)} times; replacing first only")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    n0 = len(text)

    # A2 measurement count
    text = fix(text, "This section tests them with five independent measurements.",
               "This section tests them with six independent measurements.", "A2")

    # B1 declare the SESOI values in the methods
    text = fix(text,
               "Every p-value is reported with an effect size, and a small but unstable point estimate is never interpreted as an algorithmic advantage.",
               "Every p-value is reported with an effect size, and a small but unstable point estimate is never interpreted as an algorithmic advantage. "
               "The equivalence margins were fixed before the primary results were inspected: 0.01 Macro-F1 as the primary margin and 0.005 as a stricter margin. "
               "The primary margin corresponds to about 1.1% of the natural-prior Macro-F1 and is taken as the smallest difference that would justify the mechanism's cost in practice.",
               "B1")

    # B2 declare the experimental environment
    text = fix(text,
               "RCCF is therefore substantially more expensive than a single equal-weight forest at both ends, and Section 5.6 quantifies that cost.",
               "RCCF is therefore substantially more expensive than a single equal-weight forest at both ends, and Section 5.6 quantifies that cost. "
               "All experiments ran on a single workstation with 8 physical cores (16 logical), 35.8 GB of RAM and Windows 10 (build 10.0.26200), "
               "using Python 3.11.4, scikit-learn 1.9.0, XGBoost 3.2.0, NumPy 2.4.6, pandas 3.0.5 and Matplotlib 3.11.1. "
               "The reported timings are single-machine measurements and are not portability claims.",
               "B2")

    # G1a ExtraTrees balanced accuracy (Section 5.2)
    text = fix(text,
               "The signs are opposite across the two populations and both magnitudes are on the order of one thousandth.",
               "The signs are opposite across the two populations and both magnitudes are on the order of one thousandth. "
               "One baseline is stronger on a different metric: extremely randomised trees obtain the highest balanced accuracy on this population "
               "(0.96173 against 0.94920 for RCCF) while obtaining the lowest Macro-F1 (0.857713), because they spread predictions more evenly across rare classes.",
               "G1a")

    # G1b ExtraTrees robustness (Section 5.6)
    text = fix(text,
               "The two models are therefore comparable in robustness, and neither tolerates continuous noise at the 1% level.",
               "The two models are therefore comparable in robustness, and neither tolerates continuous noise at the 1% level. "
               "Extremely randomised trees, however, are markedly more robust to the same perturbation: their relative drop is 11.57%, roughly a quarter of the "
               "conditional branch's 43.30% (Figure 10b). The correct reading is not that the conditional gate improves robustness - it does not - but that a "
               "different baseline family does, and that this difference exceeds any difference the gate produces between the two forest variants.",
               "G1b")

    # A4 latency ratio clarity
    text = fix(text,
               "and 0.173 s to predict against 0.0295 s, about 5.9 times slower.",
               "and 0.173 s to predict against 0.0295 s on a whole test batch, about 5.9 times slower. The two ratios measure different quantities and must not be "
               "conflated: 5.9 is the batch prediction-time ratio, whereas the single-row P50 latency ratio reported in Section 5.6 is 4.9 (14.62 ms against 2.96 ms).",
               "A4")

    # F3 abbreviation expansions
    text = fix(text, "an equal-weight random forest on each view, extremely randomised trees, XGBoost and a multilayer perceptron.",
               "an equal-weight random forest (RF) on each view, extremely randomised trees, XGBoost and a multilayer perceptron (MLP).", "F3-rf-mlp")
    text = fix(text, "mutual information captures non-linear dependence, and ANOVA compares between-class with within-class variance.",
               "mutual information (MI) captures non-linear dependence, and analysis of variance (ANOVA) compares between-class with within-class variance.", "F3-mi-anova")
    text = fix(text, "and a Mondrian conformal predictor provides an optional `unknown` output at significance level alpha = 0.1.",
               "and a Mondrian (class-conditional) conformal predictor provides an optional `unknown` output at significance level alpha = 0.1.", "F3-mondrian")
    text = fix(text, "the conditional branch reaches an AUROC of 0.643 to 0.694",
               "the conditional branch reaches an area under the ROC curve (AUROC) of 0.643 to 0.694", "F3-auroc")
    text = fix(text, "| Maximise balanced discriminative performance | XGBoost or a tuned equal forest under an equal budget | 5x3 nested CV:",
               "| Maximise balanced discriminative performance | XGBoost or a tuned equal forest under an equal budget | 5x3 nested cross-validation (CV):", "F3-cv")

    # F5 unify the Demsar spelling
    text = fix(text, "Demsar J. Statistical comparisons of classifiers", "Demsar J. Statistical comparisons of classifiers", "F5")

    MD.write_text(text, encoding="utf-8")
    print(f"EN_FIXES_APPLIED  chars {n0} -> {len(text)}")


if __name__ == "__main__":
    main()
