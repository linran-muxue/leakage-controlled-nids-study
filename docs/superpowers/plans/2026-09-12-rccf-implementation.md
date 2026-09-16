# RCCF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and evaluate Risk-Calibrated Conformal Forest (RCCF) under a locked, leakage-controlled protocol and update the SCI manuscript using only verified results.

**Architecture:** Four feature-selector forest experts produce cross-fitted probabilities and uncertainty descriptors. A regularized risk model estimates per-expert error from training-only out-of-fold predictions; normalized risk reliabilities fuse probabilities. A disjoint calibration partition fits temperature and class-conditional conformal rejection, while the untouched test partition is used once for final metrics. Experiment runners write row-level predictions, probabilities, thresholds, metrics, confidence intervals, and a manifest without pooling incompatible label spaces.

**Tech Stack:** Python 3.11, NumPy, pandas, SciPy, scikit-learn, XGBoost, matplotlib/seaborn, pytest, python-docx.

## Global Constraints

- Use only CIC-IDS2017, NSL-KDD, and UNSW-NB15 public data already present in the repository.
- Preserve native label spaces; never claim cross-dataset transfer.
- CIC results must identify the 3,365-row deduplicated balanced research subset and must not be described as full-dataset performance.
- Feature selection, risk fitting, calibration, conformal alpha, and thresholds must not use final test labels.
- Evaluate at least seeds 42, 2024, and 3407; keep a repeated-split sensitivity run separate from the primary estimate.
- Do not claim algorithmic superiority unless the acceptance criteria in the design specification are satisfied after Holm correction.
- Record dataset hashes, software versions, seeds, split manifests, probabilities, row-level predictions, calibration parameters, thresholds, and commands.

---

### Task 1: Add RCCF core estimator

**Files:**
- Create: `src/rccf_forest.py`
- Modify: `src/__init__.py`
- Test: `tests/test_rccf_forest.py`

**Interfaces:**
- Consumes: numeric feature matrices and native labels; `RandomForestClassifier`-compatible expert configuration.
- Produces: `RCCFForest.fit(X, y, X_cal, y_cal=None)`, `predict_proba(X)`, `predict(X)`, `predict_selective(X)`, `row_risk_`, `expert_weights_`, `temperature_`, `conformal_thresholds_`, and `classes_`.

- [ ] **Step 1: Write failing tests for expert alignment and cross-fitting.**

```python
def test_rccf_returns_normalized_probabilities_and_native_labels():
    X, y = make_classification(n_samples=120, n_features=8, n_classes=3,
                               n_informative=5, random_state=7)
    labels = np.array([f"c{i}" for i in y])
    model = RCCFForest(n_estimators=15, cv=3, random_state=7, n_jobs=1)
    model.fit(X[:90], labels[:90], X[90:105], labels[90:105])
    p = model.predict_proba(X[105:])
    assert p.shape == (15, 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert set(model.predict(X[105:])).issubset(set(labels))

def test_rccf_keeps_test_rows_out_of_risk_fit():
    X, y = make_classification(n_samples=150, n_features=6, n_classes=3,
                               n_informative=4, random_state=11)
    model = RCCFForest(n_estimators=10, cv=3, random_state=11, n_jobs=1)
    model.fit(X[:100], y[:100], X[100:125], y[100:125])
    assert model.risk_training_rows_ == 100
    assert model.final_test_rows_seen_ == 0
```

- [ ] **Step 2: Run the focused tests and verify they fail because the estimator is absent.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_forest.py`

Expected: collection failure or `ImportError` for `RCCFForest`.

- [ ] **Step 3: Implement the minimum estimator.**

Implement four experts (`full`, `chi2`, `mutual_info`, `anova`) using fold-local selectors. For each training fold, fit the selector and forest on the remaining fold, store out-of-fold probabilities and descriptors, then fit a logistic risk model whose target is expert argmax error. Fit final experts on all training rows using training-only selector fits. Convert predicted error to reliability with `exp(-risk)` and normalize across experts. Store `risk_training_rows_` and never expose a method that accepts final-test labels during fitting.

- [ ] **Step 4: Add calibration and selective interfaces.**

Fit temperature by validation-only log loss and class-conditional conformal scores from `X_cal, y_cal`. `predict_selective` must return `(labels, rejected_mask, coverage, selective_risk)` and must use only fitted calibration parameters.

- [ ] **Step 5: Run the focused tests and add edge-case tests.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_forest.py`

Expected: all RCCF tests pass, including missing-class and single-expert validation errors.

- [ ] **Step 6: Commit the core estimator.**

```text
git add src/rccf_forest.py src/__init__.py tests/test_rccf_forest.py
git commit -m "feat: add risk-calibrated conformal forest"
```

### Task 2: Implement leakage-safe metrics and statistical utilities

**Files:**
- Create: `src/rccf_metrics.py`
- Modify: `src/paired_tests.py`, `src/additional_metrics.py`
- Test: `tests/test_rccf_metrics.py`

**Interfaces:**
- Consumes: `y_true`, hard predictions, class probabilities, rejection scores, and paired model predictions.
- Produces: `classification_metrics`, `selective_metrics`, `open_set_metrics`, `bootstrap_metric_ci`, `paired_sign_flip_test`, and `holm_adjust`.

- [ ] **Step 1: Add failing metric tests.**

```python
def test_metrics_include_probability_and_selective_endpoints():
    y = np.array(["a", "b", "a", "b"])
    p = np.array([[.9,.1],[.2,.8],[.6,.4],[.4,.6]])
    out = classification_metrics(y, p, np.array(["a", "b"]))
    assert {"macro_f1", "log_loss", "brier", "ece", "mce"} <= out.keys()
    curve = selective_metrics(y, p, np.array(["a", "b"]))
    assert {"aurc", "risk_at_90", "risk_at_95"} <= curve.keys()
```

- [ ] **Step 2: Run the focused tests and verify failure.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_metrics.py`

Expected: import failure for the new functions.

- [ ] **Step 3: Implement metrics with explicit label order.**

Use `labels=classes` for every classification metric. Compute multiclass Brier as the mean squared error against one-hot labels. Compute ECE and MCE with fixed validation-independent bins `[0,.1,...,1]`. Compute AURC by sorting confidence descending and integrating risk over coverage. Do not tune bins or coverage targets from test labels.

- [ ] **Step 4: Implement paired bootstrap, sign-flip, and Holm correction.**

Bootstrap identical test rows for paired model differences. Sign-flip differences across repeated splits with exact enumeration when there are at most 12 splits. Holm-adjust only the declared comparison family and preserve raw and adjusted p-values.

- [ ] **Step 5: Run tests and commit.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_metrics.py tests/test_selective_prediction.py tests/test_conformal_rejection.py`

Expected: all focused tests pass.

```text
git add src/rccf_metrics.py src/paired_tests.py src/additional_metrics.py tests/test_rccf_metrics.py
git commit -m "feat: add RCCF probability selective and paired metrics"
```

### Task 3: Build the locked split and experiment runner

**Files:**
- Create: `scripts/run_rccf_experiments_v1.py`
- Create: `tests/test_rccf_runner.py`
- Modify: `src/audit_utils.py`

**Interfaces:**
- Consumes: `--dataset {cic,nsl,unsw}`, `--data-dir`, `--output-dir`, `--seeds`, `--n-estimators`, `--cv`, and `--alpha`.
- Produces: `metrics_by_seed.csv`, `metrics_aggregate.csv`, `predictions_seed*.csv`, `probabilities_seed*.csv`, `split_manifest.json`, `calibration_parameters.json`, and `run_manifest.json`.

- [ ] **Step 1: Write runner contract tests.**

```python
def test_runner_writes_probabilities_and_split_manifest(tmp_path):
    out = run_toy_rccf_experiment(tmp_path)
    assert (out / "predictions_seed42.csv").exists()
    assert (out / "probabilities_seed42.csv").exists()
    manifest = json.loads((out / "split_manifest.json").read_text())
    assert manifest["test_labels_used_for_fitting"] is False
```

- [ ] **Step 2: Implement deterministic split manifests.**

Use the existing deduplicated CIC v2 protocol and explicit train/calibration/validation/test indices. For NSL-KDD and UNSW-NB15, preserve the official split when available and create calibration only from the training side. Hash each index file and record class counts before fitting.

- [ ] **Step 3: Implement the runner and row-level artifact writing.**

Fit RCCF and every baseline on the same rows, write one prediction and one probability row per test sample, and include `row_id`, `true_label`, `predicted_label`, `rejected`, `max_probability`, and per-class probabilities. Measure wall-clock fit and prediction latency separately.

- [ ] **Step 4: Run the runner contract tests and commit.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_runner.py`

```text
git add scripts/run_rccf_experiments_v1.py src/audit_utils.py tests/test_rccf_runner.py
git commit -m "feat: add locked RCCF experiment runner"
```

### Task 4: Run CIC primary and sensitivity experiments

**Files:**
- Create: `scripts/run_rccf_cic_v1.py`
- Create: `tests/test_rccf_cic_contract.py`
- Output: `results_rccf_cic_v1/`

- [ ] **Step 1: Add contract tests for the 3,365-row CIC research subset.**

Assert that the manifest reports `balanced_rows=3365`, five native target labels, deduplication before splitting, and no test labels used in selector, risk, calibration, or threshold fitting.

- [ ] **Step 2: Run the contract tests before the full experiment.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_cic_contract.py`

- [ ] **Step 3: Execute primary seeds and all baselines.**

Run:

```text
& 'E:\论文\.venv\Scripts\python.exe' scripts/run_rccf_cic_v1.py --processed-dir 'E:\论文\data\processed_audit_v2' --output-dir results_rccf_cic_v1 --seeds 42 2024 3407 --n-estimators 100 --cv 5 --alpha 0.1
```

Compare RCCF with equal RF, full RF, ExtraTrees, XGBoost, CFRG, calibrated RF, and conformal RF under equal feature and tree budgets. Add 10 repeated splits only after primary artifacts are complete.

- [ ] **Step 4: Audit outputs and commit artifacts metadata.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' scripts/audit_cfrg_results_v1.py --results-dir results_rccf_cic_v1`

Expected: every primary endpoint has seed-level rows, paired prediction IDs match, and no threshold was fitted from test rows.

### Task 5: Run independent NSL-KDD and UNSW-NB15 evaluations

**Files:**
- Create: `scripts/run_rccf_external_v1.py`
- Create: `tests/test_rccf_external_contract.py`
- Output: `results_rccf_nsl_v1/`, `results_rccf_unsw_v1/`

- [ ] **Step 1: Add native-label and official-split contract tests.**

Require NSL-KDD labels `Normal, DoS, Probe, R2L, U2R`; require UNSW native attack labels and official training/testing files. Assert that outputs state `independent_native_label_benchmark=true` and `cross_dataset_transfer=false`.

- [ ] **Step 2: Execute NSL-KDD evaluation.**

Run the external runner with the two official files, reserving calibration rows only from the training file. Report Balanced Accuracy, per-class recall/F1, especially R2L and U2R, plus Log Loss, Brier, ECE, selective risk and open-set endpoints where the native protocol permits.

- [ ] **Step 3: Execute UNSW-NB15 evaluation.**

Use the official training/testing CSVs and preserve the native label taxonomy. Report the same metrics and explicitly separate this independent benchmark from CIC conclusions.

- [ ] **Step 4: Audit and commit runner code.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_external_contract.py`

### Task 6: Shared perturbation, deployment latency, coverage, and statistical analysis

**Files:**
- Create: `scripts/analyze_rccf_evidence_v1.py`
- Create: `tests/test_rccf_evidence_contract.py`
- Output: `results_rccf_evidence_v1/`

- [ ] **Step 1: Write evidence contract tests.**

Require one shared perturbation mask per seed and model, single-thread and multi-thread latency files, P50/P95/P99 fields, file-label coverage matrix, paired bootstrap CIs, Macro-F1 sign-flip tests, effect sizes, and Holm-adjusted p-values.

- [ ] **Step 2: Implement shared perturbation analysis.**

Generate noise and feature masks once per seed from a recorded RNG state, apply the identical rows and masks to every model, and report absolute and relative degradation from each model's unperturbed result.

- [ ] **Step 3: Implement latency and coverage analysis.**

Measure batch size one under `n_jobs=1` and the declared parallel setting. Repeat enough calls after warm-up to estimate P50/P95/P99. Report extracted-feature inference only, not end-to-end gateway latency. Generate the original-file × native-label × row-count matrix.

- [ ] **Step 4: Implement statistical aggregation.**

Join predictions by `row_id`, run paired bootstrap and sign-flip tests for primary endpoints, calculate standardized and absolute effect sizes, and apply Holm correction within the pre-declared families.

- [ ] **Step 5: Run evidence tests and commit.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q tests/test_rccf_evidence_contract.py`

### Task 7: Rebuild figures, tables, and bilingual SCI manuscript

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`
- Modify: `scripts/build_final_manuscripts_v1.py`
- Create: `scripts/build_rccf_figures_v1.py`
- Output: `results_paper_materials_v3/english_sci_manuscript_final.docx`, `chinese_sci_manuscript_final.docx`, and `results_publication_final/`

- [ ] **Step 1: Add manuscript contract tests before editing claims.**

Require the title, abstract, methods, results, limitations, and conclusion to distinguish RCCF from CFRG; require all primary values to be loaded from canonical CSV outputs; reject phrases such as `significantly superior`, `state of the art`, `full CIC dataset`, and `cross-dataset transfer` unless the evidence gate explicitly permits them.

- [ ] **Step 2: Generate figures from CSV artifacts only.**

Create risk-coverage curves, open-set ROC/PR curves, calibration diagrams, normalized confusion matrices, perturbation degradation plots, latency quantiles, and feature/expert weight stability plots. Every figure records source file hashes in its metadata.

- [ ] **Step 3: Rewrite the English and Chinese sections.**

Use RCCF as the proposed mechanism only if acceptance criteria pass; otherwise state the negative result and applicability boundary. Add the algorithm pseudocode, split diagram, leakage-control diagram, native-label dataset table, endpoint definitions, effect sizes, failure analysis, and reproducibility statement.

- [ ] **Step 4: Rebuild Word files and publication manifest.**

Run:

```text
& 'E:\论文\.venv\Scripts\python.exe' scripts/build_final_manuscripts_v1.py
& 'E:\论文\.venv\Scripts\python.exe' scripts/build_publication_manifest.py
```

Expected: both DOCX files open, table/figure numbering is consistent, and the manifest points to the exact RCCF result directories and source hashes.

### Task 8: Full verification and release gate

**Files:**
- Modify: `docs/final_submission_gate_v2_2026-09-11.md`
- Modify: `results_publication_final/MANIFEST.json`

- [ ] **Step 1: Run all unit and contract tests.**

Run: `& 'E:\论文\.venv\Scripts\python.exe' -m pytest -q`

Expected: zero failures.

- [ ] **Step 2: Compile every Python source file.**

Run:

```text
$files = Get-ChildItem -LiteralPath src,scripts,tests -Filter *.py -Recurse | ForEach-Object { $_.FullName }
& 'E:\论文\.venv\Scripts\python.exe' -m py_compile $files
```

Expected: no compiler output and exit code zero.

- [ ] **Step 3: Run manuscript, data, and submission audits.**

Run:

```text
& 'E:\论文\.venv\Scripts\python.exe' scripts/audit_manuscript_claims_v1.py
& 'E:\论文\.venv\Scripts\python.exe' scripts/audit_jisa_submission_v1.py
```

Expected: all canonical results, declarations, references, figures, supplementary files, hashes, and release identifiers agree.

- [ ] **Step 4: Apply the scientific decision gate.**

If RCCF meets the pre-specified endpoint, stability, significance, and guardrail criteria, retain the algorithmic-method positioning. Otherwise update title, abstract, and conclusion to the methods-and-evaluation positioning and preserve the negative result.

- [ ] **Step 5: Commit the verified release.**

```text
git add src scripts tests docs results_paper_materials_v3 results_publication_final
git commit -m "feat: complete RCCF evaluation and manuscript release"
```

