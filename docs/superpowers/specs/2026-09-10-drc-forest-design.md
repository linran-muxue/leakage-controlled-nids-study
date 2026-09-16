# DRC-Forest Design

## Objective

Develop and evaluate a dual-layer reliability-cost random forest for network intrusion detection. The method must be runnable on the existing CPU environment, preserve the training-only leakage boundary, and produce paired predictions and probabilities for statistical comparison.

## Scientific positioning

DRC-Forest is a proposed method, not a pre-validated superiority claim. The paper will report whether it improves Macro-F1, Balanced Accuracy, minority-class recall, probability quality, or open-set rejection under the declared protocols. A null or mixed result will be retained as a valid finding.

## Method definition

Let (T) be the number of trees and (C) the class set. Each tree (t) produces (p_{t,c}(x)). On a validation partition, compute per-class tree reliability:

\[
r_{t,c}=\sqrt{F1_{t,c}\,Recall_{t,c}}.
\]

Normalize the reliability for each class:

\[
w_{t,c}=\frac{r_{t,c}+\varepsilon}{\sum_{s=1}^{T}(r_{s,c}+\varepsilon)}.
\]

Fuse tree probabilities class-wise:

\[
q_c(x)=\sum_{t=1}^{T}w_{t,c}p_{t,c}(x).
\]

For imbalanced data, compute a class cost from the training partition only:

\[
g_c=\operatorname{clip}\left[\left(\frac{\bar n}{n_c}\right)^\beta,g_{min},g_{max}\right],
\]

where (n_c) is the training count, \(\bar n\) is the mean training class count, and \(\beta\), \(g_{min}\), and \(g_{max}\) are fixed or selected only inside the training/validation protocol. The final probability is:

\[
p_{DRC}(c\mid x)=\frac{g_cq_c(x)}{\sum_{k\in C}g_kq_k(x)}.
\]

For balanced CIC experiments, the cost layer is retained with \(g_c\approx1\), so the reliability layer can be isolated. For natural-distribution experiments, the cost layer is enabled and its parameters are declared in the protocol file.

## Leakage controls

- Min-Max scaling and feature selection are fitted on training data only.
- Tree reliability is computed on validation data only.
- Class costs use training counts only.
- Open-set thresholds use known-class validation scores only; unknown families never select thresholds.
- Test rows are used once for locked final predictions and metrics.
- Source filename, timestamp, row index, and raw label remain provenance fields and are excluded from model inputs.

## Comparison matrix

1. Equal-probability RF.
2. Scalar validation-weighted RF.
3. Per-class reliability RF without cost correction.
4. Cost-corrected RF without reliability correction.
5. Full DRC-Forest.
6. ExtraTrees, XGBoost, SVM, and decision tree baselines.

All comparisons use identical rows, preprocessing boundaries, seeds, and feature budgets within each protocol.

## Primary protocols

- CIC balanced research subset: 3,365 rows, 673 per class, 70/15/15 split.
- CIC natural-distribution audited subset: `data_processed_imbalanced_v3`, reported as a sensitivity protocol rather than a population estimate.
- CIC file-level forward/leave-one-file-out analysis: report only shared known-label metrics, unseen labels, coverage, and per-file support. Do not call it complete five-class temporal generalization.
- NSL-KDD: native Normal/DoS/Probe/R2L/U2R labels and official train/test boundary.
- UNSW-NB15: native ten-class `attack_cat` labels and official train/test boundary; independent benchmark only.

## Metrics and inference

Hard-label metrics: Accuracy, Balanced Accuracy, Macro-Precision, Macro-Recall, Macro-F1, and per-class Recall/F1. Probability metrics: Log Loss, macro Brier, ECE, and MCE. Robustness: shared perturbation masks and noise matrices. Deployment: single-thread and multi-thread P50/P95/P99 latency at declared batch sizes. Inference: paired bootstrap intervals, exact sign-flip or permutation tests, McNemar where applicable, and Holm correction within predefined comparison families.

## Failure and fallback policy

If DRC-Forest does not improve the primary estimand with a non-negligible paired effect, the method remains an ablation and the paper's claim is methodological. No parameter or narrative change may be made after inspecting the test result to manufacture a positive outcome.

## Deliverables

- Tested DRC-Forest implementation.
- Protocol JSON recording all parameters and data boundaries.
- Per-sample predictions and probabilities for every compared model.
- Metrics, class reports, confusion matrices, calibration, robustness, latency, and paired statistical outputs.
- Updated English and Chinese manuscripts with explicit evidence bounds.
