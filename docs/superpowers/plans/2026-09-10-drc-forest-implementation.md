# DRC-Forest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and evaluate DRC-Forest under locked, natural-distribution, file-level, and independent-benchmark protocols without weakening leakage controls.

**Architecture:** Add a focused estimator module for class-conditional reliability and class-cost fusion. Add a runner that reuses existing split loaders and emits machine-readable metrics, probabilities, reports, and protocol metadata. Update manuscript material generators only after the experimental artifacts pass tests and consistency checks.

**Tech Stack:** Python 3.11, NumPy, pandas, scikit-learn, XGBoost, pytest, python-docx.

## Global Constraints

- Never use test labels for feature selection, reliability, cost, calibration, threshold selection, or hyperparameter choice.
- Keep CIC balanced and natural-distribution protocols separate.
- Keep file-level results as coverage/generalization-risk analysis, not complete temporal generalization.
- Keep NSL-KDD and UNSW-NB15 as native-label independent benchmarks.
- Do not claim DRC-Forest superiority unless paired effect and predeclared significance criteria support it.

### Task 1: Estimator contract and tests

**Files:**
- Create: `src/drc_forest.py`
- Create: `tests/test_drc_forest.py`

- [ ] Write tests for class-conditional reliability shape, column normalization, finite probabilities, deterministic output, and balanced-data cost neutrality.
- [ ] Run the focused tests and confirm they fail because `DRCForest` does not yet exist.
- [ ] Implement `DRCForest.fit(X, y, X_valid, y_valid)`, `predict_proba(X)`, and `predict(X)` using a fitted `RandomForestClassifier` and validation-derived per-class reliability.
- [ ] Add `cost_beta`, `cost_min`, `cost_max`, and `epsilon` parameters with validation and training-count-only cost computation.
- [ ] Run focused tests, then the complete test suite.

### Task 2: Locked CIC runner

**Files:**
- Create: `scripts/run_drc_forest_cic_v1.py`
- Create: `tests/test_drc_runner_contract.py`

- [ ] Write tests for required CLI arguments, protocol metadata, output filenames, and same-row paired prediction alignment.
- [ ] Run focused tests and confirm failure before implementation.
- [ ] Implement a runner for `train.csv`, `validation.csv`, and `test.csv` with training-only Min-Max and χ² Top-k selection.
- [ ] Emit DRC-Forest, scalar weighted RF, equal RF, reliability-only, cost-only, and declared baselines using the same rows and seeds.
- [ ] Emit `metrics_3seeds.csv`, flattened aggregate metrics, class reports, confusion matrices, normalized matrices, probabilities, and `protocol.json`.
- [ ] Run the runner on the balanced CIC subset and inspect row counts and class order.

### Task 3: Natural-distribution and file-level protocols

**Files:**
- Create: `scripts/run_drc_forest_protocols_v1.py`
- Modify: `scripts/run_file_external_generalization_v1.py` only if needed to expose DRC-Forest metrics.
- Create: `tests/test_drc_protocols.py`

- [ ] Write tests proving natural-distribution outputs preserve native support and file-level outputs include unseen labels and coverage.
- [ ] Implement natural-distribution evaluation using `data_processed_imbalanced_v3` as a sensitivity protocol.
- [ ] Implement file-level evaluation using shared known labels, unseen-label reporting, and per-file support; never aggregate missing classes as zero without marking N/A.
- [ ] Emit protocol-specific JSON and CSV artifacts.
- [ ] Run focused tests and inspect coverage matrices.

### Task 4: Independent benchmark integration

**Files:**
- Create: `scripts/run_drc_forest_external_v1.py`
- Create: `tests/test_drc_external_contract.py`

- [ ] Write tests for native label preservation, train-derived encoding, and no CIC-label mixing.
- [ ] Implement NSL-KDD and UNSW-NB15 runners using their existing preprocessing boundaries and DRC-Forest where feature geometry permits.
- [ ] Emit native-label class metrics, minority-class analysis, prediction counts, and protocol metadata.
- [ ] Mark all outputs as independent benchmarks, not transfer experiments.

### Task 5: Statistical and manuscript integration

**Files:**
- Create: `docs/drc_forest_results_audit_v1.md`
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`
- Modify: manuscript-generation scripts only after artifact audit.

- [ ] Compare DRC-Forest with every ablation using paired Macro-F1, Balanced Accuracy, class-level recall, probability metrics, and latency.
- [ ] Apply paired bootstrap, exact sign-flip/permutation tests, McNemar for paired hard predictions, and Holm correction within each comparison family.
- [ ] Write results audit with explicit positive, null, and adverse findings.
- [ ] Update abstract, title, methods, results, limitations, and conclusion without overclaiming.
- [ ] Regenerate bilingual DOCX files from final Markdown sources.

### Task 6: Final verification

**Files:**
- Modify: `docs/final_submission_gate_2026-09-10.md`
- Modify: `results_publication_final/MANIFEST.json`

- [ ] Run all tests and Python compilation.
- [ ] Verify all DRC artifacts exist and are listed in the manifest.
- [ ] Run numeric, figure/table, and bilingual consistency checks.
- [ ] Record unresolved human gates: author data, funding, journal template, DOI pages, terms, and final PDF visual review.
