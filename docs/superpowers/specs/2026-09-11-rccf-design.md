# RCCF Design Specification

## 1. Objective

Develop and evaluate Risk-Calibrated Conformal Forest (RCCF), a selective and open-set network intrusion detector. The primary contribution is risk-controlled automatic decision making, not a claim of universal closed-set accuracy superiority.

## 2. Scope and scientific position

RCCF is evaluated independently on CIC-IDS2017, NSL-KDD, and UNSW-NB15. Native label spaces remain separate. The method must not be described as cross-dataset transfer. CIC's balanced 3,365-row corpus remains a research subset, not the full population. File-wise analyses are reported as coverage or stress tests unless all target classes are represented.

If RCCF does not improve the pre-specified selective/open-set endpoints after paired tests and multiplicity correction, the manuscript will use a methods-and-evaluation position rather than claim an algorithmic breakthrough.

## 3. Method

### 3.1 Expert layer

Train four forest experts under identical train/calibration/test boundaries, differing only in feature selector: full feature set, chi-square, mutual information, and ANOVA. Each expert returns class probabilities and uncertainty descriptors: maximum probability, entropy, top-two margin, tree probability variance, and disagreement.

### 3.2 Cross-fitted risk layer

Use stratified K-fold cross-fitting inside the training partition. For every training row, obtain out-of-fold expert probabilities and descriptors. The risk target is the 0/1 error of the expert argmax. Fit a regularized risk model using only cross-fitted training predictions. No validation or final-test labels enter this fit.

### 3.3 Dynamic fusion

Convert predicted error risk to non-negative expert reliability with a fixed monotone transform. Fuse expert probabilities using normalized reliability weights. The risk model and transform are locked before calibration evaluation.

### 3.4 Calibration and conformal rejection

Use a disjoint calibration partition for temperature scaling and class-conditional conformal scores. Fit the rejection threshold only from known-class calibration rows. The final test partition is never used to select temperature, conformal alpha, coverage target, or thresholds.

### 3.5 Outputs

The estimator exposes `predict_proba`, `predict`, `predict_selective`, per-row risk, coverage, and rejection decisions. It also stores expert weights and calibration metadata for auditability.

## 4. Experimental protocol

Use the locked train/validation/calibration/test protocol already defined in the repository. Hyperparameters are selected within training data or a declared validation split. The final test set is evaluated once for each locked seed. Use at least three locked seeds and a repeated-split sensitivity analysis.

### 4.1 Primary endpoints

1. AURC.
2. Selective risk at 90% and 95% coverage.
3. Open-set AUROC, AUPR, OSCR, and unknown recall at fixed known false-rejection rates.

### 4.2 Guardrail endpoints

Macro-F1, balanced accuracy, macro precision/recall, log loss, multiclass Brier score, ECE, MCE, P50/P95/P99 prediction latency, and peak memory where available.

### 4.3 Statistical comparisons

Use paired bootstrap intervals, exact McNemar tests for hard-label paired correctness, paired permutation or sign-flip tests for Macro-F1 and selective-risk differences, and Holm correction within pre-declared comparison families. Report absolute difference, relative difference, confidence interval, adjusted p-value, and effect size.

## 5. Baselines and ablations

Baselines: equal-voting RF with each feature budget, full-feature RF, ExtraTrees, XGBoost, calibrated RF, conformal RF, and the existing CFRG-Forest. Ablations: remove expert diversity, remove risk layer, remove calibration, remove conformal rejection, fixed equal weights, and full RCCF.

## 6. Acceptance and failure criteria

RCCF is considered to have evidence of algorithmic value only if it improves the primary selective/open-set endpoint on at least two datasets or pre-declared CIC unknown-family scenarios, the direction is stable over seeds, and the paired test remains significant after Holm correction. Closed-set Macro-F1 must not decrease by more than 0.5 percentage points, and calibration or latency regressions must be reported rather than hidden.

If these criteria fail, the final paper must explicitly report the negative result and position RCCF as a tested mechanism with documented applicability boundaries.

## 7. Reproducibility requirements

Record dataset hashes, source URLs, label mappings, split manifests, feature-selection rankings, model hyperparameters, random seeds, software versions, prediction probabilities, row-level predictions, calibration parameters, rejection thresholds, and all test commands in the publication manifest.
