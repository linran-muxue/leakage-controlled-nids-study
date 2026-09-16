# SCI Manuscript Structural Remediation Plan

**Goal:** Rebuild the manuscript around a defensible leakage-controlled evaluation study, with one canonical protocol, auditable evidence, and no claims stronger than the experiments support.

**Architecture:** First freeze the canonical data/model protocol and validate every reported number against machine-readable artifacts. Then repair the manuscript structure, tables, figure references, provenance statements, and statistical interpretation. Finally regenerate the bilingual Word files and run tests, compilation, manifest, and cross-language consistency checks.

**Tech Stack:** Python 3.11, pandas, scikit-learn, python-docx, pytest, PowerShell, Markdown, Git.

## Global Constraints

- The CIC primary result is a 3,365-row balanced research subset, not a full-dataset population estimate.
- The canonical CIC model is chi-square Top-60, 100 trees, `min_samples_leaf=2`, `class_weight=balanced_subsample`, seeds 42/2024/3407.
- Weighted and equal-voting forests must be reported as an applicability/ablation comparison unless a pre-defined test demonstrates a non-zero benefit.
- NSL-KDD and UNSW-NB15 are independent dataset-specific benchmarks, not direct transfer experiments.
- No dataset license, funding statement, author identity, DOI, or temporal-generalization claim may be invented.

### Task 1: Canonical evidence audit

**Files:**
- Create: `docs/sci_strict_submission_audit_2026-09-10.md`
- Inspect: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Inspect: `results_paper_materials_v3/chinese_sci_manuscript_final.md`
- Inspect: `results_publication_final/MANIFEST.json`
- Inspect: `docs/final_manuscript_consistency_audit_2026-09-05.md`

- [ ] Extract every numeric claim, model name, configuration, figure/table citation, dataset provenance statement, and limitation statement from both manuscripts.
- [ ] Compare each claim with the canonical result files and mark PASS, WARN, or BLOCKER.
- [ ] Record discrepancies with exact file paths and remediation text.
- [ ] Explicitly audit unsupported claims: full-dataset performance, complete temporal generalization, real-gateway deployment, cross-dataset transfer, algorithmic superiority, and unverified licenses.

### Task 2: Protocol and contribution rewrite

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`
- Create: `docs/canonical_protocol_v1.md`

- [ ] State the primary estimand, data curation boundary, split protocol, and model-selection boundary in one canonical protocol block.
- [ ] Recast the contribution as leakage-controlled, provenance-aware evaluation with open-set, imbalance, probability, and protocol-sensitivity evidence.
- [ ] Remove “significant improvement”, “universal superiority”, “real deployment”, and “complete temporal generalization” language unless directly supported.
- [ ] Separate locked ablation results from nested tuned model-selection results and independent benchmarks.

### Task 3: Table and figure integrity

**Files:**
- Create: `docs/figure_table_crosswalk_v1.csv`
- Modify: manuscript sources and generation scripts as needed.

- [ ] Build a crosswalk containing every Table/Figure/Supplement reference, source artifact, caption, and existence status.
- [ ] Ensure all table/figure numbers are sequential, cited in the text, and sourced from the canonical result directory.
- [ ] Remove or relabel stale artifacts from older result directories.
- [ ] Ensure supplementary materials are individually named and cited.

### Task 4: Reference and provenance hardening

**Files:**
- Modify: `docs/reference_doi_verification_2026-09-05.md`
- Modify: manuscript references and data references.
- Create: `docs/reference_verification_matrix_v1.csv`

- [ ] Distinguish DOI-verified scholarly references, stable non-DOI links, and dataset webpages.
- [ ] Add recent literature only when it directly supports a stated gap or protocol decision.
- [ ] Preserve conservative wording for dataset terms when no SPDX license is visible.
- [ ] Record the remaining manual DOI and source-terms checks.

### Task 5: Final document regeneration and gates

**Files:**
- Modify/create the manuscript generation script and final Word outputs.
- Create: `docs/final_submission_gate_2026-09-10.md`

- [ ] Regenerate English and Chinese Markdown/Word documents from the same canonical content.
- [ ] Run pytest, Python compilation, manifest validation, numeric consistency, cross-language section/number checks, and DOCX existence checks.
- [ ] Report unresolved author/funding/template/PDF-preview items separately.
