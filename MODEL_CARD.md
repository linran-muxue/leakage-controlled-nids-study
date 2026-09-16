# Model card

## Overview

The archive evaluates two aggregation strategies for flow-based intrusion detection under
one leakage-controlled protocol:

1. **Equal-weight random forest** - the control. One forest per feature view, uniform averaging.
2. **RCCF (Risk-Calibrated Conformal Forest)** - the mechanism under test. Four forests over
   four feature views, fused with sample-conditional weights learned from cross-fitted
   out-of-fold probabilities, followed by temperature scaling and Mondrian conformal rejection.

In the released code the conditional mechanism is implemented in `src/rccf_forest.py`; the
identifier `cfrg_forest` used by some result files refers to the same object.

## Intended use

Research on evaluation methodology for network intrusion detection: how much of a reported
model difference survives control of duplicates, feature-selection leakage, class priors and
tuning budgets. The archive is intended for reproduction and re-analysis of the accompanying
manuscript.

## Out-of-scope use

- **Not** a production intrusion-detection system. Latency measurements exclude packet capture,
  flow construction and feature extraction.
- **Not** validated on live traffic. All experiments use three public research datasets.
- **Not** an adversarial-robustness claim. Only random perturbations and feature masking were
  evaluated.

## Training data

See `DATA_CARD.md`. The primary protocol uses a deduplicated, capped natural-prior population
of 53,237 CIC-IDS2017 flows split 70/15/15, with a 3,365-flow balanced control.

## Evaluation

- Primary metric: macro-averaged F1 on the natural-prior population over ten seeds.
- Secondary: balanced accuracy, log loss, Brier score, expected calibration error, selective
  risk, open-set AUROC, perturbation degradation and latency percentiles.
- Equivalence is assessed with TOST against pre-specified margins of 0.005 and 0.01 Macro-F1.

## Reported summary

Across ten seeds the conditional mechanism and the equal-weight chi-square forest differ by
-0.00046 Macro-F1 with the per-seed sign split five to five, which is equivalent within both
margins. The mechanism is 4.1 times larger and 4.6 times slower per row than a single forest,
and shows no cost-sensitive advantage across false-negative to false-positive cost ratios from
1 to 100. The gain it can deliver is bounded by expert diversity: expert sets with 0.20-0.36%
pairwise disagreement gain exactly zero, while deliberately decorrelated sets gain positively.

## Ethical considerations

All experiments use public datasets. No scanning, probing or live attack traffic was generated.
Raw datasets are not redistributed.
