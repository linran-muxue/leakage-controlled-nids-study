# SCI Upgrade and Audit Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with verification after each boundary.

**Goal:** Upgrade the intrusion-detection manuscript and experiment package toward a defensible SCI submission by resolving data-independence, statistical, reproducibility, and claim-scope problems.

**Architecture:** Keep CIC-IDS2017 as the primary controlled five-class benchmark, treat NSL-KDD and UNSW-NB15 as independent-label benchmarks, and add a separate sensitivity protocol for UNSW cross-split overlap. Reframe the contribution as leakage-controlled and coverage-aware evaluation unless a new mechanism demonstrates a non-zero, reproducible effect.

**Tech Stack:** Python 3.11/3.9-compatible scripts, pandas, NumPy, scikit-learn, XGBoost, python-docx, pytest.

## Global Constraints

- Never use test data to fit preprocessing, feature selection, calibration, thresholds, or hyperparameters.
- Never report balanced CIC results as full-dataset performance.
- Never claim weighted RF is significantly better when paired tests show zero effect.
- Never call file-external known-only metrics complete five-class temporal generalization.
- Preserve raw datasets and existing canonical artifacts; add new result directories rather than overwriting raw files.

### Task 1: UNSW cross-split sensitivity audit and benchmark

**Files:**
- Create: `scripts/run_unsw_cross_split_sensitivity_v1.py`
- Create: `tests/test_unsw_cross_split_sensitivity_v1.py`
- Produce: `results_unsw_nb15_cross_split_sensitivity_v1/`

- [ ] Add a protocol that evaluates official split, test-overlap removal, and duplicate-group exclusion using the same RF configuration and seed list.
- [ ] Save row counts, overlap fractions, class counts, metrics, and per-sample predictions for every protocol.
- [ ] Add tests for deterministic exclusion and preservation of label columns.
- [ ] Run the focused tests, then run the benchmark.

### Task 2: Canonical manifest and data-source metadata

**Files:**
- Modify: `results_publication_final/MANIFEST.json`
- Create: `results_publication_final/external_data_metadata_template.json`
- Modify: `results_paper_materials_v3/full_paper_body_v6_data_processing.md`

- [ ] Add external audit and sensitivity artifacts to the manifest.
- [ ] Add explicit fields for URL, retrieval date, version/commit, license, and checksum status without inventing values.
- [ ] State unresolved metadata fields as author-supplied items.

### Task 3: Claim-scope and statistical protocol correction

**Files:**
- Modify: `results_paper_materials_v3/full_paper_body_v6_data_processing.md`
- Create: `results_paper_materials_v3/sci_claims_matrix_v1.md`

- [ ] Replace algorithm-improvement language with effect-estimation language where evidence is null.
- [ ] Distinguish Accuracy tests from Macro-F1 bootstrap/paired tests.
- [ ] State single-seed NSL-KDD evidence level and known-only file-external denominator.
- [ ] Document minimum effect thresholds as future preregistration items rather than retrofitted hypotheses.

### Task 4: SCI innovation package

**Files:**
- Create: `results_paper_materials_v3/innovation_positioning_v1.md`
- Modify: `results_paper_materials_v3/full_paper_body_v6_data_processing.md`

- [ ] Position the contribution as an auditable benchmark protocol with open-set, coverage, calibration, and deployment dimensions.
- [ ] Define open-set evaluation as a separate future/extension protocol unless completed with evidence.
- [ ] Add limitations preventing unsupported claims of novelty, migration, deployment, or universal optimality.

### Task 5: Manuscript regeneration and verification

**Files:**
- Modify: `scripts/build_complete_paper_v6.py`
- Produce: `论文完整正文_v6_数据处理完善稿.docx`
- Produce: `results_paper_materials_v3/sci_strict_audit_v1.md`

- [ ] Regenerate Word from the canonical v6 source.
- [ ] Run all tests and Python compilation.
- [ ] Verify stale numbers, duplicate headings, broken table references, and manifest hashes.
- [ ] Report remaining human blockers separately.
