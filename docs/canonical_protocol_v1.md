# Canonical protocol v1

## Scope

This protocol defines the only result layer that may be called the primary CIC experiment in the manuscript.

## CIC primary data

- Source: CIC-IDS2017 `MachineLearningCSV` archive.
- Curation: label mapping, finite-value filtering, global feature-vector duplicate audit, cross-label conflict removal, per-class cap, and equal sampling.
- Main labels: `Normal`, `DoS/DDoS`, `Brute Force`, `Web Attack`, `Bot`.
- Excluded closed-set labels: `PortScan`, `Infiltration`, `Heartbleed`; they may appear only in the explicitly labelled open-set experiment.
- Research subset: 3,365 rows, 673 per class.
- Split: stratified 70/15/15, giving 2,355/505/505 rows per split.
- Important boundary: this is a balanced research subset and is not a population estimate for the full CIC archive.

## Canonical model configuration

- Feature selector: training-fitted Min-Max transform followed by χ² ranking and Top-60 selection.
- Random forest: 100 trees, `min_samples_leaf=2`, `class_weight=balanced_subsample`.
- Seeds: 42, 2024, 3407.
- Validation: used for model selection and tree-weight estimation only.
- Test: used once for locked final estimates and paired prediction comparisons.

## Comparison layers

1. **Locked ablation:** full-feature RF, χ² RF, weighted RF, and declared baselines on identical rows.
2. **Feature-selection fairness:** χ², mutual information, ANOVA, and full-feature controls under the same Top-60 budget where applicable.
3. **Nested selection control:** model-specific tuning inside outer folds; never mixed with locked estimates.
4. **Independent benchmarks:** NSL-KDD and UNSW-NB15 retain their native label systems and public train/test boundaries.
5. **Protocol sensitivity:** natural class prior, overlap removal, file coverage, open-set unknown families, probability, robustness, and latency analyses.

## Data leakage wording

Global duplicate/conflict handling is a dataset-level curation step performed before the final split. It is disclosed and audited, but it is not described as a pristine untouched-test protocol. Min-Max parameters, categorical encoders, feature scores, thresholds, calibration parameters, and hyperparameters are fitted only on the training partition or training fold.

## Claim policy

- Report point estimates, dispersion, confidence intervals, and paired effects.
- Do not claim universal superiority, SOTA, complete temporal generalization, real gateway deployment, or cross-dataset transfer.
- Treat weighted voting as an applicability/ablation result because current paired predictions are identical.
- Treat external datasets as independent benchmarks, not pooled evidence.
