"""Second half of the ten-seed update for the English manuscript."""
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

    # second reading
    text = fix(text,
               "**Second, the paired statistics give a definite equivalence boundary.** The three seed-level differences "
               "are -0.00149, +0.00314 and +0.00160. A paired bootstrap that resamples test rows gives a pooled 90% "
               "interval of [-0.00290, +0.00550], which lies entirely inside a pre-specified equivalence margin of "
               "SESOI = 0.01 Macro-F1; equivalence can therefore be asserted at alpha = 0.05. The same interval does "
               "**not** fit inside SESOI = 0.005, because its upper bound of 0.0055 exceeds that margin. Per-seed exact "
               "McNemar tests give p = 0.508, 0.092 and 0.344, and pooling all 23,958 test rows gives p = 0.215. None "
               "is significant. Under the pre-declared decision rule - the difference must be stable, consistent in "
               "sign and bounded away from zero - **H2 is not supported**.",
               "**Second, the paired statistics establish equivalence at a strict margin.** With ten seeds the mean "
               "paired difference is -0.000456 with a standard deviation of 0.001152. Two interval estimates are "
               "reported because they answer different questions: the seed-level 90% interval [-0.001124, +0.000212] "
               "reflects model-to-model variability, while the test-row paired bootstrap interval [-0.004251, "
               "+0.003382] reflects resampling uncertainty over the locked test set. Both lie inside equivalence "
               "margins of 0.005 and 0.01 Macro-F1, so equivalence can be asserted at alpha = 0.05 against either "
               "margin. This strengthens the three-seed analysis, for which the 0.005 margin was not attainable. The "
               "sign of the difference is split five to five across seeds, and exact McNemar tests on the test rows are "
               "non-significant. Under the pre-declared decision rule - stable, consistent in sign, and bounded away "
               "from zero - **H2 is not supported**.",
               "second-reading")

    # table 5
    old_table = "\n".join([
        "**Table 5. Paired tests on the natural-prior population (RCCF minus equal-weight chi-square forest)**",
        "",
        "| Seed | Macro-F1 difference | Paired bootstrap 90% interval | Inside +/- 0.01? | Exact McNemar p |",
        "|---|---:|---|---:|---:|",
        "| 42 | -0.001490 | [-0.003823, +0.000580] | Yes | 0.508 |",
        "| 2024 | +0.003142 | [-0.000366, +0.006950] | Yes | 0.092 |",
        "| 3407 | +0.001602 | [-0.000142, +0.003605] | Yes | 0.344 |",
        "| Pooled (23,958 rows) | +0.001085 | [-0.002898, +0.005501] | Yes at 0.01 / No at 0.005 | 0.215 |",
        "| Control: versus equal RF (all features) | +0.001995 | - | - | **0.00061 (RCCF better)** |",
    ])
    new_table = "\n".join([
        "**Table 5. Paired statistics on the natural-prior population (ten seeds)**",
        "",
        "| Comparison | Mean difference | SD | Seed-level 95% interval | Seed-level 90% interval | TOST at 0.005 | TOST at 0.01 | Minimum detectable effect (80% power) | Cohen's d_z | Seeds favouring RCCF / baseline |",
        "|---|---:|---:|---|---|---|---|---:|---:|---:|",
        "| RCCF - equal RF (chi-square) | -0.000456 | 0.001152 | [-0.001280, +0.000368] | [-0.001124, +0.000212] | equivalent | equivalent | 0.001146 | -0.40 | 5 / 5 |",
        "| RCCF - equal RF (all features) | +0.001613 | 0.001376 | [+0.000628, +0.002597] | [+0.000815, +0.002410] | equivalent | equivalent | 0.001369 | +1.17 | 9 / 1 |",
        "| RCCF - ExtraTrees (chi-square) | +0.031788 | 0.001616 | [+0.030632, +0.032944] | [+0.030851, +0.032724] | not equivalent | not equivalent | 0.001607 | +19.68 | 10 / 0 |",
        "",
        "The test-row paired bootstrap against the equal-weight chi-square forest gives a pooled 90% interval of "
        "[-0.004251, +0.003382] over the same ten seeds, which is also inside both margins.",
        "",
        "Three entries deserve comment. **Power.** With ten seeds and the observed standard deviation, the smallest "
        "difference detectable at 80% power is 0.00115 to 0.00161 Macro-F1; anything smaller would be missed, which is "
        "precisely why the equivalence margins are stated explicitly rather than inferred from a non-significant test. "
        "**Versus the full-feature forest.** The difference is positive and statistically detectable - the interval "
        "excludes zero and nine of ten seeds favour RCCF - yet its magnitude of 0.0016 lies inside the 0.005 "
        "equivalence margin: it is real but practically negligible, and Section 5.4 shows it is the same size as a "
        "feature-view choice. **Versus extremely randomised trees.** The difference is large and unambiguous "
        "(d_z = 19.7, all ten seeds), and is the only substantial model-to-model gap in this study.",
    ])
    text = fix(text, old_table, new_table, "table5")

    # third reading: full-feature comparison and cost
    text = fix(text,
               "**Third, against the full-feature forest the difference is significant, but no larger than a "
               "feature-view choice.** Compared with an equal-weight full-feature forest, RCCF gains 0.001995 "
               "Macro-F1; pooling 23,958 test rows gives an exact McNemar p = 0.00061, with RCCF winning 33 rows and "
               "losing 10. The gate therefore does produce a small, directionally consistent advantage, but its "
               "magnitude is in the same band as simply swapping the feature view from chi-square to full features "
               "(+0.0009 to +0.0022). Combined with a 5.9-fold inference cost, that advantage has no engineering "
               "exchange value.",
               "**Third, against the full-feature forest the difference is detectable, but no larger than a "
               "feature-view choice.** Compared with an equal-weight full-feature forest, RCCF gains 0.001613 "
               "Macro-F1 over ten seeds, with the seed-level interval excluding zero and nine of ten seeds favouring "
               "RCCF. The gate therefore does produce a small, directionally consistent advantage, but its magnitude "
               "is in the same band as simply swapping the feature view from chi-square to full features (+0.0021). "
               "Combined with a roughly fivefold inference cost, that advantage has no engineering exchange value.",
               "third-reading")

    # fourth reading: batch ratio
    text = fix(text,
               "and 0.173 s to predict against 0.0295 s on a whole test batch, about 5.9 times slower.",
               "and 0.244 s to predict against 0.046 s on a whole test batch, about 5.3 times slower.",
               "fourth-reading")

    # class prior magnitude
    text = fix(text,
               "The same RCCF mechanism reaches 0.961807 Macro-F1 on the balanced control population and 0.889955 on "
               "the natural-prior population, a difference of **+0.0719**.",
               "The same RCCF mechanism reaches 0.961807 Macro-F1 on the balanced control population and 0.889278 on "
               "the natural-prior population, a difference of **+0.0725**.",
               "class-prior")

    # magnitude list
    text = fix(text,
               "aggregation +0.0011, feature view +0.0009, deduplication order +0.0014 (maximum 0.0060), tuning "
               "budget +0.0078 and class prior +0.0719",
               "aggregation 0.0005, feature view +0.0021, deduplication order +0.0014 (maximum 0.0060), tuning "
               "budget +0.0078 and class prior +0.0725",
               "magnitude-list")

    # calibration sentence
    text = fix(text,
               "On the natural-prior population RCCF's Log Loss (0.05148) and Brier score (0.006312) are better than "
               "the equal-weight forest's (0.05283 and 0.006334), but its ECE is worse (0.006605 against 0.004442).",
               "On the natural-prior population RCCF's Log Loss (0.05183) is better than the equal-weight forest's "
               "(0.05220), but both its Brier score (0.006365 against 0.006255) and its ECE (0.006849 against "
               "0.004493) are worse.",
               "calibration")

    # conclusion first
    text = fix(text,
               "On the natural-prior population of CIC-IDS2017, the Macro-F1 difference between conditional weighting "
               "and an equal-weight chi-square forest is +0.0011 with a pooled 90% interval of [-0.00290, +0.00550], "
               "which is equivalent within a pre-specified margin of 0.01 Macro-F1 but not within 0.005; per-seed "
               "McNemar tests are non-significant. The four experts disagree on no test row, and the normalised "
               "weight entropy is 0.99998. The cost is a 78-fold increase in training time and a 5.9-fold increase in "
               "inference time. Against a full-feature equal forest the gate is significantly better (p = 0.00061), "
               "but the magnitude matches that of a feature-view change.",
               "Averaged over ten seeds on the natural-prior population of CIC-IDS2017, the Macro-F1 difference "
               "between conditional weighting and an equal-weight chi-square forest is -0.000456 with the per-seed "
               "sign split five to five; both the seed-level 90% interval [-0.00112, +0.00021] and the test-row "
               "paired bootstrap interval [-0.00425, +0.00338] lie inside equivalence margins of 0.005 and 0.01. The "
               "four experts disagree on no test row, and the normalised weight entropy is 0.99998. The cost is about "
               "an 80-fold increase in training time and a fivefold increase in batch inference time. Against a "
               "full-feature equal forest the gate is reliably better over ten seeds, but the magnitude matches that "
               "of a feature-view change.",
               "conclusion-first")

    # conclusion third
    text = fix(text,
               "a change of class prior moves Macro-F1 by +0.0719 and a reversal of deduplication order by up to "
               "+0.0060, whereas the aggregation strategy moves it by +0.0011.",
               "a change of class prior moves Macro-F1 by +0.0725 and a reversal of deduplication order by up to "
               "+0.0060, whereas the aggregation strategy moves it by 0.0005.",
               "conclusion-third")

    MD.write_text(text, encoding="utf-8")
    print("EN_10SEED_PART2_APPLIED")


if __name__ == "__main__":
    main()
