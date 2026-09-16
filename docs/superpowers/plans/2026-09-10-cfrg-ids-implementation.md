# CFRG-IDS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and rigorously evaluate an OOB cross-fitted, sample-conditional gated random forest with optional class-risk adjustment and validation-only open-set rejection.

**Architecture:** A new `CFRGForest` estimator owns a scikit-learn random forest, reconstructs per-tree OOB availability from each tree seed, creates tree-level uncertainty descriptors, and fits a low-capacity logistic gate without using validation or test labels. Separate modules implement selective/open-set scoring and paired statistics. Dataset runners reuse the established training-only scaling and feature-selection boundaries and emit canonical, per-row artifacts.

**Tech Stack:** Python 3.11, NumPy, pandas, scikit-learn, SciPy, XGBoost, pytest, python-docx.

## Global Constraints

- Do not change or overwrite the existing DRC-Forest results; all CFRG outputs use new versioned directories.
- The primary CFRG method uses `cost_beta=0`; nonzero class-risk adjustment is an ablation.
- No validation or test row may be used to fit the base forest, gate, feature transform, or descriptor scaler.
- Rejection thresholds may use known-class validation data only; unknown test attacks are never used for fitting.
- CIC's 3,365-row balanced set remains a research subset, not a full-dataset estimate.
- NSL-KDD and UNSW-NB15 remain native-label independent benchmarks.
- Every final claim must be generated from saved predictions and probabilities.

---

### Task 1: Implement OOB descriptor primitives

**Files:**
- Create: `src/cfrg_forest.py`
- Create: `tests/test_cfrg_forest.py`

**Interfaces:**
- Produces: `tree_probability_tensor(forest, X) -> np.ndarray`, shape `(n_samples, n_trees, n_classes)`.
- Produces: `tree_descriptor_tensor(tree_probabilities, epsilon=1e-12) -> np.ndarray`, shape `(n_samples, n_trees, 4)`.
- Produces: `tree_oob_mask(forest, n_samples) -> np.ndarray`, shape `(n_samples, n_trees)`.

- [ ] **Step 1: Write failing tensor-shape and normalization tests**

```python
def test_tree_probability_and_descriptor_shapes():
    forest = RandomForestClassifier(n_estimators=7, bootstrap=True, random_state=4).fit(X, y)
    probability = tree_probability_tensor(forest, X)
    descriptor = tree_descriptor_tensor(probability)
    assert probability.shape == (len(X), 7, 2)
    assert descriptor.shape == (len(X), 7, 4)
    np.testing.assert_allclose(probability.sum(axis=2), 1.0)
    assert np.isfinite(descriptor).all()
```

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `& "E:\论文\.venv\Scripts\python.exe" -m pytest tests/test_cfrg_forest.py -q`  
Expected: collection/import failure because `src.cfrg_forest` does not exist.

- [ ] **Step 3: Implement aligned per-tree probabilities and descriptors**

Use the forest class order, map each tree's encoded class columns defensively, clip probabilities before logarithms, and compute confidence, normalized entropy, top-two margin, and agreement with the forest modal class.

- [ ] **Step 4: Implement deterministic OOB masks**

Use each fitted tree's `random_state` with scikit-learn's bootstrap sample-count rule. A row is OOB for a tree if it is absent from that tree's generated bootstrap indices. Reject `bootstrap=False` with a clear `ValueError`.

- [ ] **Step 5: Run focused tests**

Run: `& "E:\论文\.venv\Scripts\python.exe" -m pytest tests/test_cfrg_forest.py -q`  
Expected: all Task 1 tests pass.

### Task 2: Implement the cross-fitted gate

**Files:**
- Modify: `src/cfrg_forest.py`
- Modify: `tests/test_cfrg_forest.py`

**Interfaces:**
- Produces class `CFRGForest.fit(X, y)`, `predict_proba(X)`, and `predict(X)`.
- Exposes `classes_`, `model_`, `gate_model_`, `descriptor_scaler_`, `oob_coverage_`, and `gate_diagnostics_`.

- [ ] **Step 1: Write failing fit/predict tests**

Tests must assert deterministic output, finite row-normalized probabilities, sample-varying gate weights, no zero-OOB training row after fallback handling, and cost factors equal to one when `cost_beta=0`.

- [ ] **Step 2: Run the focused tests and confirm failure**

Run the same focused pytest command and verify missing estimator behavior.

- [ ] **Step 3: Build OOB gate-training rows**

For each original training row, retain only OOB trees. Each retained tree descriptor becomes one gate-training row. Its binary target is whether that tree predicted the training label correctly. Add class-aware sample weights so majority classes do not dominate the gate. Rows with fewer than two OOB trees are excluded and counted in diagnostics.

- [ ] **Step 4: Fit the descriptor scaler and logistic gate**

Fit `StandardScaler` and `LogisticRegression` on OOB descriptor rows only. Handle the degenerate one-target-class case with a constant gate. Convert gate correctness probabilities into per-sample tree weights using temperature-softmax.

- [ ] **Step 5: Implement gated prediction and optional class-risk factors**

At inference, compute every tree descriptor, obtain correctness scores, apply temperature-softmax across trees, aggregate probabilities, apply the optional training-count factor, and normalize. Store aggregate diagnostics without retaining test labels.

- [ ] **Step 6: Run focused and existing forest tests**

Run: `& "E:\论文\.venv\Scripts\python.exe" -m pytest tests/test_cfrg_forest.py tests/test_drc_forest.py -q`  
Expected: all tests pass.

### Task 3: Add calibration and selective/open-set utilities

**Files:**
- Create: `src/selective_prediction.py`
- Create: `tests/test_selective_prediction.py`

**Interfaces:**
- Produces `fit_rejection_threshold(probabilities, target_coverage) -> float`.
- Produces `apply_rejection(probabilities, classes, threshold) -> np.ndarray`.
- Produces `risk_coverage_curve(y_true, probabilities, classes) -> pd.DataFrame`.
- Produces `open_set_metrics(known_scores, unknown_scores, threshold) -> dict`.

- [ ] **Step 1: Write failing validation-only threshold tests**

Test monotonic coverage, deterministic threshold selection, correct unknown output, finite risk-coverage AUC, and correct behavior when all probabilities tie.

- [ ] **Step 2: Implement threshold and risk-coverage functions**

Define confidence as maximum class probability and rejection score as one minus confidence. Threshold fitting receives only known validation probabilities. It selects the empirical confidence quantile corresponding to the requested coverage.

- [ ] **Step 3: Implement open-set metrics**

Return AUROC, AUPR, unknown recall at the fitted threshold, known false-rejection rate, and sample counts. Raise on empty known or unknown inputs rather than silently returning invented results.

- [ ] **Step 4: Run focused tests**

Run: `& "E:\论文\.venv\Scripts\python.exe" -m pytest tests/test_selective_prediction.py -q`.

### Task 4: Build the locked CIC CFRG experiment

**Files:**
- Create: `scripts/run_cfrg_cic_v1.py`
- Create: `tests/test_cfrg_cic_contract.py`

**Interfaces:**
- Consumes `data_processed_audit_v2/{train,validation,test}.csv`.
- Produces `results_cfrg_cic_v1/protocol.json`, `metrics_3seeds.csv`, `metrics_aggregate.csv`, class reports, confusion matrices, predictions, probabilities, gate diagnostics, and ablation summaries.

- [ ] **Step 1: Write failing artifact-contract tests**

Use a temporary three-class dataset and assert required columns, class-probability columns, split counts, `feature_selection_fit_on=training_only`, `gate_fit_on=oob_training_predictions_only`, and distinct model identifiers.

- [ ] **Step 2: Implement the runner using existing loading and metric helpers**

Compare equal RF, static weighted RF, DRC, CFRG without costs, CFRG with costs, descriptor ablations, ExtraTrees, class-weight RF, calibrated RF, and XGBoost when installed. Use the same selected features, rows, and seeds.

- [ ] **Step 3: Save gate evidence**

For every seed save the distribution of gate weights, entropy, effective tree count, changed-prediction fraction versus equal RF, probability L1 difference, and OOB coverage.

- [ ] **Step 4: Run the contract test**

Run: `& "E:\论文\.venv\Scripts\python.exe" -m pytest tests/test_cfrg_cic_contract.py -q`.

- [ ] **Step 5: Run the real balanced CIC experiment**

Run:

```powershell
& "E:\论文\.venv\Scripts\python.exe" scripts/run_cfrg_cic_v1.py `
  --processed-dir "C:\Users\27677\Documents\ChatGPT\论文\data_processed_audit_v2" `
  --output-dir "C:\Users\27677\Documents\ChatGPT\论文\results_cfrg_cic_v1" `
  --chi2-k 60 --n-estimators 100 --min-samples-leaf 2 `
  --seeds 42 2024 3407
```

Expected: completed CSV/JSON artifacts and no claims generated in code.

### Task 5: Run natural-distribution and open-set protocols

**Files:**
- Create: `scripts/run_cfrg_sensitivity_v1.py`
- Create: `tests/test_cfrg_sensitivity_contract.py`

**Interfaces:**
- Consumes `data_processed_imbalanced_v3` and existing CIC unknown-family rows/provenance.
- Produces `results_cfrg_sensitivity_v1/natural_distribution/` and `open_set/` artifacts.

- [ ] **Step 1: Write artifact and threshold-boundary tests**

Assert that protocol metadata states `unknown_rows_used_for_threshold=false`, that known validation and unknown test counts are separate, and that all compared methods share the same rejection threshold policy.

- [ ] **Step 2: Implement natural-distribution runner**

Compare `cost_beta` values 0, 0.25, and 0.5 against equal/class-weight RF. Report per-class recall/F1, predicted class counts, balanced accuracy, Macro-F1, probability metrics, and operating-point deltas.

- [ ] **Step 3: Implement open-set runner**

Use the existing unknown-family construction, fit the 95% known-coverage threshold from known validation only, and compare CFRG and equal RF under identical unknown rows for individual and combined held-out families.

- [ ] **Step 4: Run tests and experiments**

Run focused tests, then execute both protocols with seeds 42, 2024, and 3407.

### Task 6: Extend the independent NSL-KDD and UNSW-NB15 runner

**Files:**
- Create: `scripts/run_cfrg_external_v1.py`
- Create: `tests/test_cfrg_external_contract.py`

**Interfaces:**
- Produces separate versioned result directories for each dataset and seed.
- Preserves native labels and official train/test boundaries.

- [ ] **Step 1: Write failing multi-seed and probability-artifact tests**

Assert Log Loss, Brier, ECE/MCE, normalized confusion matrices, per-class predicted counts, file hashes, train/validation/test counts, and `cross_dataset_transfer=false`.

- [ ] **Step 2: Correct preprocessing boundaries while implementing the new runner**

Fit categorical vocabulary, numeric handling, scaler, chi-square selection, base model, and CFRG gate from official training data only. Split validation from the official training file. Never concatenate official train and test data to create dummy-variable columns.

- [ ] **Step 3: Add strong independent baselines**

Run equal RF, class-weight RF, ExtraTrees, XGBoost, probability-calibrated RF, and CFRG with identical per-dataset feature matrices and search budgets.

- [ ] **Step 4: Save minority and overlap diagnostics**

For NSL-KDD, save R2L/U2R recall, F1, support, and prediction counts. For UNSW, preserve the documented feature-key overlap analysis without calling it cross-dataset leakage.

- [ ] **Step 5: Run real external experiments**

Run three seeds on both datasets and aggregate within each dataset only.

### Task 7: Add paired inference and effect-size audit

**Files:**
- Create: `scripts/audit_cfrg_results_v1.py`
- Create: `tests/test_cfrg_statistics_contract.py`

**Interfaces:**
- Consumes per-row prediction artifacts from Tasks 4--6.
- Produces `paired_effects.csv`, `paired_bootstrap_intervals.csv`, `permutation_tests.csv`, `mcnemar_tests.csv`, and `holm_adjusted_tests.csv`.

- [ ] **Step 1: Write tests on synthetic identical and improved predictions**

Identical predictions must produce zero effect and McNemar p=1. Improved synthetic predictions must produce the expected positive direction. Probability tests must preserve pairing.

- [ ] **Step 2: Implement paired row-level bootstrap**

Resample row indices jointly for each model pair and calculate Macro-F1, Balanced Accuracy, Log Loss, and Brier differences. Save percentile intervals and the bootstrap probability of a positive effect.

- [ ] **Step 3: Implement repeated-split permutation and Holm correction**

Apply sign-flip permutation tests to paired split-level effects. Define comparison families before correction and save raw and adjusted values.

- [ ] **Step 4: Run audit tests and the real audit**

Do not average p-values across seeds. Aggregate paired row-level evidence by a declared pooled-strata or hierarchical bootstrap procedure and label it explicitly.

### Task 8: Measure complexity, latency, and memory

**Files:**
- Create: `scripts/benchmark_cfrg_v1.py`
- Create: `tests/test_cfrg_benchmark_contract.py`

**Interfaces:**
- Produces latency percentiles, throughput, serialized model size, peak memory, and descriptor/gate overhead for batch sizes 1, 32, and 512.

- [ ] **Step 1: Write output-schema tests**

Assert batch size, thread count, repeats, warmups, P50/P95/P99, samples per second, file bytes, peak RSS, model name, and hardware/software metadata.

- [ ] **Step 2: Implement fair benchmark harness**

Preload data, warm each model, time only prediction, use identical sample orders, and record single-thread and configured multi-thread runs. State that feature extraction and network I/O are excluded.

- [ ] **Step 3: Run the benchmark on the locked CIC test set**

Save raw timing samples in addition to aggregates.

### Task 9: Generate canonical tables, figures, and scientific decision report

**Files:**
- Create: `scripts/build_cfrg_paper_artifacts_v1.py`
- Create: `docs/cfrg_scientific_decision_2026-09.md`
- Create: `results_cfrg_paper_v1/`
- Create: `tests/test_cfrg_paper_artifacts.py`

**Interfaces:**
- Consumes only versioned CFRG result directories.
- Produces flat publication tables, figures, a claim matrix, and a PASS/NULL/ADVERSE decision for each pre-registered estimand.

- [ ] **Step 1: Write tests preventing unsupported claims**

If an interval includes zero or the practical margin, generated prose must not contain `significantly outperforms`, `state of the art`, `universal`, or `cross-dataset transfer`.

- [ ] **Step 2: Build four to six main tables**

Create a data/protocol table, locked model table, ablation table, external benchmark table, open-set/selective table, and statistical-effect table. Place detailed class reports and timing samples in supplementary outputs.

- [ ] **Step 3: Build figures**

Generate the method diagram, normalized confusion matrix, risk--coverage curve, calibration curve, gate-weight/effective-tree plot, and accuracy/probability/latency Pareto plot.

- [ ] **Step 4: Generate the scientific decision report**

For each success criterion, cite exact source artifacts and decide whether the algorithmic claim passes, remains null, or is adverse.

### Task 10: Rebuild the bilingual manuscript and verification gates

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`
- Modify or create the canonical DOCX builder.
- Modify: `results_publication_final/MANIFEST.json`
- Modify: `README.md`

**Interfaces:**
- Produces regenerated English and Chinese DOCX files from one canonical artifact registry.

- [ ] **Step 1: Rewrite title, abstract, method, results, and conclusion from the decision report**

Promote CFRG-IDS to the title and contribution list only if the pre-registered algorithmic criteria pass. Otherwise retain the evaluation-protocol title and describe CFRG as a negative or bounded mechanism study.

- [ ] **Step 2: Remove duplicated DRC result passages and stale table references**

Every number must point to one canonical artifact. Historical result directories may not be cited as final evidence.

- [ ] **Step 3: Regenerate both Word manuscripts**

Preserve equations as editable equation text where supported, insert high-resolution figures, use sequential captions, and keep author/funding fields explicitly unresolved rather than invented.

- [ ] **Step 4: Run the full verification gate**

Run:

```powershell
& "E:\论文\.venv\Scripts\python.exe" -m pytest -q
$files = Get-ChildItem -LiteralPath src,scripts,tests -Filter *.py -Recurse | ForEach-Object { $_.FullName }
& "E:\论文\.venv\Scripts\python.exe" -m py_compile $files
```

Expected: all tests pass, Python compilation succeeds, manuscript claim audit succeeds, and every manifest path exists.

## Self-review

- All four pre-registered estimands map to Tasks 4--7 and the decision report.
- Every fitted transform has an explicit training boundary.
- The primary model is separated from cost, descriptor, and open-set ablations.
- External datasets are not pooled or described as transfer experiments.
- Failure criteria are explicit, so negative results cannot be hidden by manuscript wording.
- Author identity, funding, source terms, and submission-template confirmation remain human responsibilities and are not invented by this plan.

