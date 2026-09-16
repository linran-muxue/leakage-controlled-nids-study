# CFRG-IDS Scientific Decision Report (2026-09-11)

## Scope

This report records the pre-specified decision criteria for the cross-fitted
risk-gated forest (CFRG-Forest). It is based only on versioned result
artifacts under `results_cfrg_cic_v2_verified`, `results_cfrg_unsw_v2_verified`,
`results_cfrg_nsl_v2_verified`, and the corrected `results_cfrg_open_set_v5_verified` protocol.

## Decision summary

**Algorithmic breakthrough claim: NOT SUPPORTED.** CFRG changes the hard
prediction for only one paired test row per CIC seed relative to equal-voting
RF. The Macro-F1 difference is approximately +0.00198 on each seed, but the
paired bootstrap intervals include zero, McNemar's exact p-value is 1.0, and
the corrected paired Macro-F1 permutation test is not significant.

**Probability-quality claim: NOT SUPPORTED.** On CIC, CFRG has slightly worse
mean Log Loss (0.14478 versus 0.13328 for equal RF-χ²) and slightly worse macro
Brier (0.01422 versus 0.01382). ECE is lower on average, but MCE and Log Loss
are not consistently improved. On NSL-KDD and UNSW-NB15, CFRG Log Loss and
Brier are also worse than equal RF-χ².

**Open-set claim: REJECTED FOR THE CURRENT VERSION.** Under the corrected
known-validation protocol, raw CFRG has mean AUROC 0.6675 and unknown recall
0.0145, whereas equal RF has 0.9357 and 0.1860. Conformal scoring improves
CFRG to AUROC 0.7878 and unknown recall 0.0648, but remains below equal-RF
conformal rejection (0.8969 and 0.2172). The gate should not be presented as
an open-set detector.

**Cross-dataset robustness claim: NOT SUPPORTED.** On NSL-KDD and UNSW-NB15,
CFRG does not dominate the native-label baselines. Results remain independent
benchmarks; no pooled or transfer score is valid.

### Calibration follow-up

Temperature scaling was fitted on a known-class calibration split only and
evaluated on a separate known evaluation split plus held-out unknown families.
For CFRG, calibration reduced CIC Log Loss from
0.14337/0.14288/0.14810 to 0.13693/0.13610/0.14013 for seeds 42/2024/3407 and
reduced ECE to 0.0119--0.0177, but it did not change Macro-F1.
In the leakage-safe open-set protocol, calibrated CFRG AUROC was 0.765--0.817
and unknown recall was 0.003--0.0078, still far below equal RF. Calibration
improves probability sharpness but does not repair the gate's inability to
separate unknown attacks.

### Repeated splits and stronger baselines

Ten independent stratified CIC splits further weaken the algorithmic claim.
CFRG mean Macro-F1 is 0.95710 (SD 0.00780), compared with 0.95722 (SD
0.00739) for equal-voting RF; CFRG wins 4 splits, ties 1, and loses 5. Under
the same locked feature budget and three fixed seeds, XGBoost obtains mean
Macro-F1 0.96324, CFRG 0.96182, equal RF 0.95984, and ExtraTrees 0.94898.
Thus CFRG is not the strongest tuned model and its apparent fixed-seed gain
does not survive repeated resampling.

## Evidence table

| Estimand | Evidence | Decision |
|---|---|---|
| CIC Macro-F1 vs equal RF-χ² | +0.00198 per seed; bootstrap lower bound 0; McNemar p=1.0; paired permutation p=1.0 | Null / practically negligible |
| CIC probability quality | Log Loss 0.14478 vs 0.13328; Brier 0.01422 vs 0.01382 | Adverse |
| NSL-KDD native benchmark | CFRG Macro-F1 0.5200 vs ExtraTrees 0.5829; Log Loss 2.448 vs equal RF 1.567 | Adverse relative to strongest baseline |
| UNSW-NB15 native benchmark | CFRG Balanced Accuracy 0.5783; Macro-F1 0.4852; Log Loss 0.788 | Mixed, no dominance |
| CIC open-set rejection | CFRG AUROC 0.657–0.784; unknown recall 0.0005–0.145 | Rejected |
| Calibrated open-set rejection | CFRG AUROC 0.765–0.817; unknown recall 0.003–0.0078 | Rejected |
| Ten repeated CIC splits | CFRG 0.95710 vs equal RF 0.95722; 4 wins/1 tie/5 losses | Rejected |
| Strong baseline comparison | XGBoost Macro-F1 0.96324 > CFRG 0.96182 | Rejected |

## Required manuscript wording

The method must not be described as state of the art, universally superior,
significantly better than random forest, or as a solved open-set detector.
The defensible wording is:

> CFRG-Forest is a pre-specified sample-conditional gating mechanism. In the
> present protocols it produces a small, non-significant hard-label change on
> balanced CIC data and degrades probability quality and open-set rejection.
> These results identify a calibration and uncertainty failure mode rather
> than establish a superior classifier.

## Next technical work before any algorithm-paper submission

1. Add a separately fitted temperature/isotonic calibration layer using known
   validation data only.
2. Recompute open-set scores from calibrated probabilities and compare with
   equal RF under identical thresholds.
3. Add class-weight RF, Balanced RF, XGBoost, ExtraTrees, and a calibrated
   stacking baseline under one locked tuning budget.
4. Repeat the CIC comparison over at least ten predeclared stratified splits;
   retain the current three-seed artifacts as a fixed-seed audit.
5. If no practical positive effect remains after calibration, change the paper
   positioning to reproducible evaluation and publish CFRG as a bounded
   negative result rather than an algorithmic breakthrough.
