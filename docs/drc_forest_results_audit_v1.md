# DRC-Forest results audit (2026-09-10)

## Locked CIC-IDS2017 balanced protocol

- Data: `data_processed_audit_v2`; 3,365 rows, five classes, 2,355/505/505 train/validation/test.
- Preprocessing: Min-Max and χ² Top-60 fitted on training rows only.
- Model configuration: 100 trees, `min_samples_leaf=2`, `class_weight=balanced_subsample`, seeds 42, 2024, 3407.
- DRC reliability: per-tree per-class `sqrt(F1*Recall)` measured on validation rows.
- DRC cost: training-count-only class cost with beta=0.5 and clipping [0.5, 2.0]. Costs are effectively one on the balanced protocol.

| Model | Accuracy mean | Balanced accuracy mean | Macro-F1 mean | Log loss mean | Brier mean | ECE mean |
|---|---:|---:|---:|---:|---:|---:|
| Equal RF χ² | 0.959736 | 0.959736 | 0.959842 | 0.133281 | 0.013817 | 0.026244 |
| Reliability-only RF χ² | 0.959736 | 0.959736 | 0.959842 | 0.133001 | 0.013783 | 0.026142 |
| Cost-only RF χ² | 0.959736 | 0.959736 | 0.959842 | 0.133281 | 0.013817 | 0.026244 |
| Full DRC-Forest χ² | 0.959736 | 0.959736 | 0.959842 | 0.133001 | 0.013783 | 0.026142 |

Hard predictions are identical between DRC-Forest and equal RF for all three seeds. The paired Macro-F1 delta is exactly 0 and McNemar's exact p-value is 1.0 (0 discordant pairs). The method therefore does not demonstrate a hard-label accuracy breakthrough on this balanced protocol. The small probability-quality difference is retained as a secondary finding, not a superiority claim.

## Natural-distribution CIC sensitivity protocol

Using `data_processed_imbalanced_v3`, equal RF χ² has mean Macro-F1 0.893624 and balanced accuracy 0.951580. Full DRC-Forest has mean Macro-F1 0.876068 and balanced accuracy 0.960349. Paired bootstrap Macro-F1 differences (DRC minus equal) are negative for all three seeds: -0.01897, -0.01986, and -0.01185, with percentile intervals excluding zero in the 500-resample audit. McNemar p-values are below 1e-8 for all seeds. The cost layer improves class-balanced recall at the expense of overall Macro-F1 under the declared natural-prior protocol.

## Independent benchmarks

NSL-KDD is evaluated with its native Normal/DoS/Probe/R2L/U2R labels and official train/test boundary. With a training-only internal validation split, DRC-Forest χ² obtains accuracy 0.749911, balanced accuracy 0.507170, and Macro-F1 0.538121. R2L and U2R remain minority-class failure modes; the independent benchmark is not a transfer experiment.

UNSW-NB15 is evaluated with native ten-class `attack_cat` labels and the official train/test boundary. In the seed-42 DRC audit, accuracy is 0.725113, balanced accuracy 0.565792, and Macro-F1 0.499362. The official files have 1,302 normalized feature-key overlaps covering 8,541 test rows (10.37%); this is reported as a split-construction limitation.

## Claim policy

The evidence supports a dual-layer reliability/cost mechanism as a transparent, reproducible applicability analysis. It does not support claims of universal superiority, statistically significant hard-label improvement, complete temporal generalization, cross-dataset transfer, or real-gateway deployment readiness.

