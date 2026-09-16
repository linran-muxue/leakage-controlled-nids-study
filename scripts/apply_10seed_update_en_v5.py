"""Update the English manuscript with the ten-seed primary results."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
MD = BASE / "English_SCI_Manuscript_v4.md"
RUN = ROOT / "results_seeds10_v5"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    table_rows = (RUN / "table4a_10seeds.md").read_text(encoding="utf-8").strip().splitlines()

    # 1. abstract
    text = fix(text,
               "On the natural-prior protocol RCCF and an equal-weight chi-square forest differ by +0.0011 Macro-F1; "
               "a paired bootstrap gives a pooled 90% interval of [-0.00290, +0.00550], which is contained within a "
               "pre-specified equivalence margin of 0.01 Macro-F1 but not within 0.005, and per-seed exact McNemar "
               "tests are non-significant (p = 0.508 / 0.092 / 0.344).",
               "Across ten seeds on the natural-prior protocol the two models differ by -0.00046 Macro-F1 with the "
               "per-seed sign split five to five; both the seed-level 90% interval [-0.00112, +0.00021] and the "
               "test-row paired bootstrap interval [-0.00425, +0.00338] lie inside equivalence margins of 0.005 and "
               "0.01 Macro-F1.",
               "abstract")

    # 2. contribution 3 magnitude list
    text = fix(text, "aggregation (+0.0011), feature view (-0.0009), deduplication order (up to +0.0060)",
               "aggregation (0.0005), feature view (+0.0021), deduplication order (up to +0.0060)", "contrib")

    # 3. estimand seeds
    text = fix(text, "averaged over a pre-specified set of random seeds (42, 2024, 3407).",
               "averaged over a pre-specified set of ten random seeds (42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505).",
               "seeds")

    # 4. feature-selection comparison row
    text = fix(text, "| Natural-prior population (three seeds) | 0.887960 | 0.888870 | **+0.00091** |",
               "| Natural-prior population (ten seeds) | 0.887666 | 0.889734 | **+0.00207** |", "feature-row")

    # 5. table 4 lead-in and caption
    text = fix(text, "Table 4 gives the main results on both populations, averaged over the three fixed seeds.",
               "Table 4 gives the main results on both populations. Panel (a) is averaged over the ten seeds of the "
               "primary protocol; panel (b) remains the three-seed balanced control.", "table4-lead")
    text = fix(text, "**Table 4. Main results on the two populations (mean of three seeds)**",
               "**Table 4. Main results on the two populations**", "table4-caption")
    text = fix(text, "(a) Natural-prior population P_nat, 7,986 test rows",
               "(a) Natural-prior population P_nat, 7,986 test rows, mean of ten seeds", "table4a-head")

    # 6. replace panel (a) rows
    old_rows = [
        "| RCCF | 0.97792 | 0.94920 | **0.889955** | **0.05148** | **0.006312** | 0.006605 | 61.00 | 0.173 |",
        "| Equal RF (chi-square, k = 60) | 0.97759 | 0.94948 | 0.888870 | 0.05283 | 0.006334 | **0.004442** | 0.784 | 0.0295 |",
        "| Equal RF (full features) | 0.97696 | 0.95085 | 0.887960 | 0.05424 | 0.006624 | 0.005126 | 0.816 | 0.0367 |",
        "| ExtraTrees (chi-square) | 0.96369 | **0.96173** | 0.857713 | 0.08903 | 0.010849 | 0.015791 | 0.442 | 0.0368 |",
    ]
    joined = "\n".join(old_rows)
    if joined not in text:
        raise SystemExit("panel (a) rows not found as a block")
    text = text.replace(joined, "\n".join(table_rows), 1)

    # 7. first reading
    text = fix(text,
               "**First, the headline result is a near-zero difference.** On the natural-prior population RCCF reaches "
               "0.889955 Macro-F1 against 0.888870 for the equal-weight chi-square forest, a mean difference of "
               "**+0.001085**. On the balanced control RCCF reaches 0.961807 against 0.963215, i.e. it trails by "
               "**-0.001408**. The signs are opposite across the two populations and both magnitudes are on the order "
               "of one thousandth. One baseline is stronger on a different metric: extremely randomised trees obtain "
               "the highest balanced accuracy on this population (0.96173 against 0.94920 for RCCF) while obtaining "
               "the lowest Macro-F1 (0.857713), because they spread predictions more evenly across rare classes.",
               "**First, the headline result is a near-zero difference.** Averaged over ten seeds on the natural-prior "
               "population, RCCF reaches 0.889278 Macro-F1 against 0.889734 for the equal-weight chi-square forest, a "
               "mean difference of **-0.000456**, with five seeds favouring RCCF and five favouring the equal forest. "
               "On the three-seed balanced control RCCF reaches 0.961807 against 0.963215, trailing by -0.001408. Both "
               "magnitudes are below one thousandth and the sign is not stable across settings. One baseline is "
               "stronger on a different metric: extremely randomised trees obtain the highest balanced accuracy "
               "(0.96215 against 0.94820 for RCCF) while obtaining the lowest Macro-F1 (0.857490), because they "
               "spread predictions more evenly across rare classes.",
               "first-reading")

    MD.write_text(text, encoding="utf-8")
    print("EN_10SEED_PART1_APPLIED")


if __name__ == "__main__":
    main()
