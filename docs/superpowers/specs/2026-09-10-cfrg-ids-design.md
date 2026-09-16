# CFRG-IDS Algorithm Design Specification

**Date:** 2026-09-10  
**Status:** Awaiting author review before implementation  
**Target task:** Leakage-controlled network intrusion detection with sample-conditional forest gating and open-set rejection

## 1. Research objective

The current reliability-weighted random forest assigns fixed tree weights and produces the same hard predictions as equal voting on the locked CIC protocol. CFRG-IDS replaces fixed post-hoc weights with a cross-fitted, sample-conditional gating mechanism and a separately calibrated rejection rule. The objective is not to guarantee an improvement in advance, but to test whether adaptive gating can improve the joint operating point of class-balanced classification, probability quality, and unknown-attack rejection under strict leakage control.

The primary estimands are defined before running the final experiments:

1. The paired difference in test Macro-F1 and Balanced Accuracy between CFRG-IDS and the strongest tuned non-CFRG baseline.
2. The paired difference in Log Loss, macro-Brier score, and ECE.
3. The difference in unknown-attack recall and false-positive rate at a fixed known-class coverage target.
4. The change in risk--coverage area under the curve for selective prediction.

No superiority claim will be made unless the direction, uncertainty interval, and pre-specified comparison family support it. A null or adverse result will be reported as a valid outcome.

## 2. Algorithm definition

### 2.1 Base forest

For a training partition, fit a random forest with (T) trees using the locked feature pipeline. Each tree (t) produces a class-probability vector (p_t(x)). The base forest retains the ordinary equal-voting probability

\[
p_{\mathrm{eq}}(c\mid x)=\frac{1}{T}\sum_{t=1}^{T}p_t(c\mid x).
\]

### 2.2 Cross-fitted tree descriptors

For each training row (x_i), obtain the prediction of every tree that did not use row (i) in its bootstrap sample. These OOB predictions are used only to construct training descriptors. For tree (t), define:

- confidence (m_t(x)=\max_c p_t(c\mid x));
- predictive entropy (H_t(x)=-\sum_c p_t(c\mid x)\log(p_t(c\mid x)+\epsilon));
- margin (d_t(x)=p_{t,(1)}(x)-p_{t,(2)}(x)), where the two terms are the largest class probabilities;
- disagreement (D_t(x)=1-\frac{1}{T-1}\sum_{s\ne t}\mathbf 1[\arg\max p_t(x)\ne\arg\max p_s(x)]).

The descriptor (z_t(x)=[m_t(x),H_t(x),d_t(x),D_t(x)]) is normalized using training-fold parameters only. No validation or test row is used to fit descriptor scaling.

### 2.3 Sample-conditional gating network

A small multinomial logistic gate is fitted on OOB descriptors and the corresponding training labels. Its score is

\[
u_t(x)=h_\phi(z_t(x)),\qquad
\alpha_t(x)=\frac{\exp(u_t(x)/\tau)}{\sum_{s=1}^{T}\exp(u_s(x)/\tau)},
\]

where τ is selected in the inner validation protocol from the fixed grid {0.5, 1.0, 2.0}. The gate is regularized with L2 penalty selected from {10⁻⁴, 10⁻³, 10⁻²}. The final gated probability is

\[
p_{\mathrm{gate}}(c\mid x)=\sum_{t=1}^{T}\alpha_t(x)p_t(c\mid x).
\]

This is materially different from a fixed validation weight: the vector α(x) changes for each sample, while the gate parameters are fitted from cross-fitted OOB evidence.

### 2.4 Class-risk adjustment

Class-risk adjustment is optional and evaluated as a separate component, never silently combined with the gate. The training-only class factor is

\[
g_c=\operatorname{clip}\left[\left(\frac{\bar n}{n_c}\right)^\beta,g_{\min},g_{\max}\right],
\]

with β ∈ {0, 0.25, 0.5}, (g_{\min}=0.5), and (g_{\max}=2.0). The adjusted probability is normalized after multiplication by (g_c). β=0 is the no-cost gate and is the primary algorithmic comparison; nonzero β values are operating-point analyses.

### 2.5 Open-set rejection

The known-class classifier is trained without unknown attack rows. A rejection score is computed from the gated output:

\[
s(x)=1-\max_c p_{\mathrm{gate}}(c\mid x).
\]

The threshold is selected only on known-class validation rows to achieve a pre-specified coverage target of 95% when possible. If the target is infeasible, the nearest feasible threshold is recorded. Unknown rows are never used for threshold fitting. Outputs are either a known class or `unknown`.

The primary open-set metrics are AUROC, AUPR, unknown recall, FPR@95TPR, and risk--coverage AUC. Results are reported separately for each held-out attack-family combination and are not described as complete open-world detection.

## 3. Leakage-control boundaries

The following rules are mandatory for every dataset and split:

1. Global duplicate and conflict auditing is a dataset-level curation step and is disclosed as such.
2. Imputation, invalid-value filtering decisions, scaling, encoding, feature scoring, gate descriptor scaling, gate fitting, cost factors, temperature, regularization, and rejection thresholds are fitted inside the training partition or inner training fold only.
3. Validation data may be used for hyperparameter selection, calibration, and rejection-threshold selection; it is never used to fit the base forest.
4. The test partition is used once for final evaluation and is never used to select features, hyperparameters, costs, calibration, or thresholds.
5. Source filename, timestamp, row index, raw label, duplicate fingerprint, and provenance fields are excluded from model features.
6. NSL-KDD and UNSW-NB15 preserve their native labels and official train/test boundaries. Their results are independent benchmarks, not pooled transfer scores.

## 4. Baseline and ablation matrix

All models receive the same rows, feature budget, preprocessing boundary, seeds, and tuning budget.

### Baselines

1. Full-feature random forest.
2. Chi-square Top-60 random forest.
3. ExtraTrees with the same feature budget.
4. XGBoost with a documented fixed search budget.
5. Class-weighted random forest.
6. Balanced random forest or an explicitly documented class-weighted substitute if the dependency is unavailable.
7. Static scalar-weighted forest.
8. Probability-calibrated equal forest.

### CFRG ablations

1. Equal voting without a gate.
2. Fixed validation weighting only.
3. OOB gate without class-risk adjustment.
4. OOB gate with class-risk adjustment.
5. Gate without entropy descriptor.
6. Gate without disagreement descriptor.
7. Gate trained from in-sample predictions instead of OOB predictions, included only as a leakage-risk negative control and never as a valid final method.
8. Gate plus open-set rejection versus equal forest plus the same rejection rule.

The primary method is OOB gate with β=0. Nonzero cost settings and descriptor removals are ablations, not additional undisclosed model variants.

## 5. Datasets and protocols

### CIC-IDS2017

- Balanced research subset: 3,365 rows, five classes, 70/15/15 stratified split, seeds 42, 2024, and 3407.
- Natural-distribution sensitivity set: same locked configuration, class priors retained.
- Open-set protocol: known five classes; PortScan, Infiltration, and Heartbleed held out as unknown combinations.
- File-level protocol: report only shared-label metrics and label coverage; missing classes are N/A.

### NSL-KDD

Use native Normal, DoS, Probe, R2L, and U2R labels and the official KDDTrain+/KDDTest+ boundary. Report accuracy, balanced accuracy, macro-F1, Log Loss, Brier, ECE, confusion matrices, per-class support, and R2L/U2R predicted-count analysis.

### UNSW-NB15

Use native ten-class `attack_cat` labels and the official training/testing files. Report the same metrics and the documented feature-key overlap sensitivity. No cross-dataset pooled score is computed.

## 6. Statistical analysis

For each comparison family:

1. Run three fixed seeds and at least ten repeated stratified splits for CIC when computationally feasible.
2. Save per-row predictions and probabilities for every model.
3. Use paired bootstrap resampling of test rows for 95% intervals.
4. Use paired sign-flip or permutation tests for repeated-split metric differences.
5. Use McNemar only for paired hard-label disagreements on the same test rows.
6. Report effect size, confidence interval, raw p-value, and Holm-adjusted p-value.
7. Treat five-fold nested results as sensitivity evidence because the attainable permutation p-value resolution is discrete.

## 7. Complexity and deployment accounting

The base forest remains (O(T\,d\,\log n)) for training up to implementation-dependent constants. Gating adds (O(Tq)) per sample, where (q=4) descriptor dimensions before optional ablations. Memory overhead is (O(Tq)) for per-sample descriptors plus the gate parameters. Report model file size, peak resident memory where measurable, single-thread and multi-thread P50/P95/P99 latency, and throughput for batch sizes 1, 32, and 512. These are offline CPU measurements on the documented machine and are not end-to-end gateway guarantees.

## 8. Pre-registered success and failure criteria

The method is considered to have evidence of algorithmic value only if all of the following are examined and reported:

1. The gate changes predictions or probabilities on a non-trivial fraction of test rows.
2. Any positive Macro-F1 or Balanced Accuracy difference is reproduced across seeds or repeated splits.
3. The 95% interval excludes a practically negligible margin defined before evaluation (0.2 percentage points for Macro-F1 on CIC).
4. The improvement is not obtained solely by changing class priors or using test-derived thresholds.
5. Probability or open-set gains are reported even if hard-label gains are absent.

If these criteria are not met, the manuscript must present CFRG-IDS as a tested mechanism with bounded applicability and revert to the evaluation-protocol contribution rather than claiming a breakthrough classifier.

## 9. Reproducibility artifacts

The implementation must emit:

- a protocol JSON containing dataset paths, hashes, split seeds, model parameters, and software versions;
- per-model metrics, class reports, confusion matrices, normalized confusion matrices;
- per-row predictions and probabilities;
- gate descriptor and weight summaries;
- threshold and calibration records;
- bootstrap and paired-test outputs;
- a figure/table crosswalk pointing only to canonical result artifacts.

No original dataset is redistributed in the repository.

