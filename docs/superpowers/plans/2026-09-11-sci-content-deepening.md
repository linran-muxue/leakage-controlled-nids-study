# SCI Content Deepening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the manuscript from an experiment report to a defensible SCI evaluation study with explicit estimands, mechanism-level reasoning, systematic related work, auditable evidence tables, and bounded conclusions.

**Architecture:** Keep CFRG-Forest as a bounded methodological mechanism, while making the paper's primary contribution the leakage-controlled evaluation protocol and failure-boundary analysis. Generate the English and Chinese manuscripts from canonical Markdown sources, and place a compact set of evidence tables in the main Word body before supplementary material.

**Tech Stack:** Markdown, Python, python-docx, pandas, pytest, existing CIC/NSL-KDD/UNSW result artifacts.

## Global Constraints

- Do not claim SOTA, universal superiority, statistically significant CFRG improvement, solved open-set detection, transfer success, or end-to-end gateway readiness.
- Do not invent literature metrics, licenses, author metadata, or data-provider terms.
- Preserve the locked CIC protocol: deduplicated balanced research subset, 3,365 rows, top-60 training-only features, 100 trees, `min_samples_leaf=2`, seeds 42/2024/3407.
- Keep NSL-KDD and UNSW-NB15 as independent native-label benchmarks; do not pool scores across datasets.
- Every numerical claim must be traceable to an existing result artifact or an explicitly labeled assumption.

---

### Task 1: Add a formal study model and estimand map

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`

- [ ] Add a compact notation block defining populations, protocols, metrics, and comparison estimands.
- [ ] Add explicit acceptance/refutation rules for H1–H4 and distinguish confirmatory from sensitivity analyses.
- [ ] Add a protocol table with dataset, label space, split, fit boundary, and estimand.

### Task 2: Deepen the algorithmic argument without overstating novelty

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`

- [ ] Add propositions explaining when a risk gate can change the argmax and when it is algebraically inert.
- [ ] Add a gate-identifiability and error-correlation discussion.
- [ ] Add an explicit cost-benefit equation for the extra gate computation.

### Task 3: Expand related work into a systematic comparison

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`

- [ ] Add 2021–2025 literature from `docs/recent_sci_literature_scan_2026-09-11.md` with author-year citations only where metadata is available.
- [ ] Add a dataset/task/protocol/limitation comparison table and state that quantitative values are not copied when full text was not verified.
- [ ] Add a paragraph distinguishing this study from OpenMax/EVT/VAE/BNN/domain-adaptation families.

### Task 4: Rewrite results and discussion around mechanisms and negative evidence

**Files:**
- Modify: `results_paper_materials_v3/english_sci_manuscript_final.md`
- Modify: `results_paper_materials_v3/chinese_sci_manuscript_final.md`

- [ ] Reorganize results into primary, stability, external, and diagnostic evidence.
- [ ] Explicitly answer RQ1–RQ4 after each evidence block.
- [ ] Add relative changes, uncertainty interpretation, and failure-boundary implications using existing values.

### Task 5: Put core evidence tables into the main Word body

**Files:**
- Modify: `scripts/build_final_manuscripts_v1.py`

- [ ] Add a compact protocol table and literature comparison table before the evidence appendix.
- [ ] Keep detailed CSV-derived tables as supplementary evidence.
- [ ] Regenerate bilingual DOCX files.

### Task 6: Validate content and reproducibility

**Files:**
- Create: `tests/test_manuscript_content.py`

- [ ] Test that the manuscript contains bounded claims, all RQ answers, key limitations, and required citation markers.
- [ ] Run pytest, Python compilation, manuscript audit, and DOCX readability checks.

