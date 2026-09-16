# Model-wise nested cross-validation (5x3)

This experiment uses the development pool formed by `data_processed_audit_v4/train.csv` and `validation.csv`. The original `data_processed_audit_v4/test.csv` is untouched and is not used for preprocessing, feature selection, tuning, or outer-fold evaluation.

For each of the three model families (random forest, ExtraTrees, XGBoost), the inner 3-fold loop selects the feature mode and χ² budget (`k` in {20, 40, 60}); the selected configuration is then refit and evaluated on the outer 5-fold test partition. Every fold fits its own Min-Max scaler and χ² selector.

Summary:

| Model | Outer Macro-F1 mean ± SD | Log Loss mean ± SD | ECE mean ± SD |
|---|---:|---:|---:|
| Random forest | 0.9544 ± 0.0059 | 0.1506 ± 0.0170 | 0.0287 ± 0.0046 |
| ExtraTrees | 0.9480 ± 0.0067 | 0.1700 ± 0.0204 | 0.0385 ± 0.0081 |
| XGBoost | 0.9622 ± 0.0059 | 0.1176 ± 0.0181 | 0.0139 ± 0.0037 |

The paired outer-fold Macro-F1 difference is 0.0078 for XGBoost minus random forest, with a bootstrap interval of [0.0044, 0.0105] and an exact sign-permutation p-value of 0.0625. Because only five outer folds are available, the result should be described as an observed advantage under this protocol, not as a universal or statistically significant superiority claim.
