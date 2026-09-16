# Canonical Protocol v3b

This file is the single protocol contract for the submission package.

## Primary estimand

Expected primary test Macro-F1 for five-class CIC-IDS2017 flow classification on the v3b 53,237-row deduplicated, physically screened, capped observed-prior population, using a stratified 70/15/15 split and seeds 42, 2024, and 3407. The 3,365-row balanced subset is a secondary control protocol. Both estimates are conditional on the documented corpus-level curation and sampling rules; neither is a full-corpus prevalence estimate.

## Curation boundary

Label mapping, finite-value removal, strict physical-range screening, duplicate screening, cross-label conflict identification, per-class capping, and balanced sampling are performed before the final split. These steps are dataset-level curation choices and are disclosed as such. They do not establish an untouched test corpus.

## Training boundary

Scaling, feature ranking, model fitting, OOB gate fitting, calibration, rejection thresholds, and hyperparameter selection use only the training partition, OOB predictions, or the designated validation/calibration partition. Final test labels are read once for locked evaluation.

## Locked model

Chi-square Top-60 features, 100 trees, `min_samples_leaf=2`, `class_weight=balanced_subsample`, and fixed seeds 42/2024/3407. Equal-voting RF, full-feature RF, ExtraTrees, and XGBoost are reported as controlled comparisons. CFRG is an applicability mechanism under test, not a pre-certified winner.

## Evidence hierarchy

Natural-prior CIC results are primary; balanced CIC results are a control. Ten repeated splits, paired tests, bootstrap intervals, calibration, robustness, latency, open-set, file-coverage, NSL-KDD, and UNSW-NB15 analyses are secondary or diagnostic. Native-label external benchmarks are not pooled and are not interpreted as direct transfer.

## Claim limits

The package does not support claims of universal superiority, SOTA status, complete temporal generalization, cross-dataset transfer, or end-to-end gateway deployment.

## Source-file boundary

The v3b natural-prior and balanced protocols are stratified flow-level splits.
All eight source CSVs appear in train, validation, and test; the machine-readable
`results_data_audit_cic_natural_v3b/source_file_split_label_counts.csv` records
this explicitly. Therefore zero duplicate/hash overlap is not evidence of
source-file or temporal independence. The leave-one-file-out results are kept as
a separate coverage-aware pressure test.
