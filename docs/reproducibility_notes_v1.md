# Reproducibility notes

## Why the three-seed and ten-seed baselines disagree for the same seed

Two released directories contain an arm named "equal RF (chi-square, k = 60)" on
the same split:

| Directory | Protocol | Seed 42 Macro-F1 | Shipped as |
|---|---|---:|---|
| `results_cic_natural_baselines_v3b/` | three seeds (42, 2024, 3407) | 0.890773 | S04, S05, S06, S07 |
| `results_seeds10_v5/` | ten seeds | 0.891714 | S20, Table 4(a) |

They disagree on 11 of the 7,986 test rows, and the same nominal configuration
should not do that. The cause is **the column order of the design matrix**, not
the chi-square score:

* `run_cfrg_cic_v1.py` builds `X[:, np.argsort(-scores)]`, i.e. columns sorted by
  descending chi-square score;
* `run_seeds10_v5.py` uses `SelectKBest(...).transform(X)`, which keeps the
  original feature order.

A random forest draws `max_features` columns per split **by index**, so
permuting the selected columns fits different trees. That is the whole effect.
Refitting seed 42 on the processed split establishes it exactly
(`results_review_v5/baseline_reproduction_v1.json`):

| Selection | Column order | Macro-F1 | Agreement with the released files |
|---|---|---:|---|
| three-seed set | score order | 0.890773 | v3b 7,986/7,986 |
| three-seed set | feature order | 0.891945 | neither |
| ten-seed set | score order | 0.890773 | v3b 7,986/7,986 |
| ten-seed set | feature order | 0.891714 | v5 7,986/7,986 |

The two selections differ by one feature, `RST Flag Count` versus
`ECE Flag Count`, because their chi-square scores tie exactly at rank 60 - and
the two columns are **element-wise identical** on this corpus (they fire on the
same flows), so the tie changes a column's name but not a single prediction.
The column order is the only cause.

### What this does and does not affect

* No reported number changes. Table 4(a) and Table 5 are computed entirely from
  `results_seeds10_v5`; the three-seed RCCF values quoted for the neural-baseline
  comparison come from `results_rccf_cic_natural_v3b`, and the **RCCF arm is
  identical between the two runs** (same per-seed Macro-F1 and accuracy to six
  decimals). The manuscript never mixes the two baseline runs for one quantity.
* What a reader must not do is compare the three-seed baseline file with the
  ten-seed baseline file and read the difference as an effect. They are two
  different forests under one name.

### What has been changed

`src/feature_selection.py` now defines one canonical selection: top-k by
chi-square, returned in ascending feature order (what `SelectKBest.transform`
produces, hence what the current ten-seed protocol already used), with any tie
at the k-th boundary reported rather than silently resolved.
`run_seeds10_v5.py` uses it, and a unit test asserts the canonical selection is
bit-identical to `SelectKBest.transform`. `run_cfrg_cic_v1.py` is left as
published so that `results_cic_natural_baselines_v3b/` stays reproducible as
released. `scripts/check_selection_reproducibility_v1.py` is part of the gate: it
recomputes the tie, re-checks that each released column order reproduces its own
file exactly, and fails if this note's evidence disappears.
