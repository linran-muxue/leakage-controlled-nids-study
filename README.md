# Leakage-Controlled Network Intrusion Detection Study

Public repository: https://github.com/linran-muxue/leakage-controlled-nids-study
Submission release: `v1.11.0` (pushed to the remote; the archive cited in the manuscript availability statement)

The locked CIC-IDS2017 publication protocol is **v3b**.  `data_processed_cic_natural_v3b`
is the primary capped natural-prior research population, while
`data_processed_cic_balanced_v3b` is a secondary balanced control subset.  The same
audit is then re-run with a 200,000-per-class cap (`data_processed_cic_natural_v4_scale200k`,
413,209 flows) and with the cap removed entirely (`data_processed_cic_natural_v4_full`,
2,429,503 flows); those two populations are reported in Section 5.7 and in supplementary
S27 and S29, and they are where the aggregation-rule difference stops being equivalent.  The
older `audit_v1`--`audit_v6`, `data_processed_cic_natural_v1`--`v3`, and
`results_*_v1`/`v2` directories are historical artifacts and must not be used
to reproduce the manuscript tables.

Reproducibility materials for the manuscript *Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection: A Leakage-Controlled Study of Conditional Ensemble Weighting*.

## Scope

This repository contains source code, configuration files, audit summaries, derived metrics, prediction outputs, figures, and manuscript-supporting tables. It does **not** redistribute the original CIC-IDS2017, NSL-KDD, UNSW-NB15 or N-BaIoT files. Users must obtain those datasets from their respective providers and comply with the providers' terms.

## Reproduction environment

The tested environment is recorded in `requirements-lock.txt`. The project was validated with Python 3.11, scikit-learn, pandas, NumPy, SciPy, matplotlib, seaborn, joblib, openpyxl, python-docx, xgboost, and pytest.

Two released directories contain an arm with the same name but different
numbers: the three-seed baseline (`results_cic_natural_baselines_v3b/`) sorts the
selected columns by descending chi-square score, while the ten-seed baseline
(`results_seeds10_v5/`) keeps the original feature order, and a random forest
subsamples columns by index. Seed 42 therefore reads 0.890773 in one and
0.891714 in the other. Each run is internally consistent and the manuscript
never mixes them, but the two must not be subtracted from one another. The full
evidence is in `docs/reproducibility_notes_v1.md`; `src/feature_selection.py`
defines the canonical selection used by the current runner.

## Main artifacts

- `src/`: reusable data and experiment components.
- `scripts/`: audit, experiment, statistical-analysis, and document-generation scripts.
- `tests/`: automated tests.
- `results_publication_final/`: locked CIC results and uncertainty outputs.
- `results_cfrg_cic_v2_verified/`: canonical locked CIC comparison after the probability-label alignment fix.
- `results_cfrg_nsl_v2_verified/`, `results_cfrg_unsw_v2_verified/`: verified native-label independent benchmarks.
- `results_cfrg_repeated_v3_verified/`, `results_cfrg_strong_baselines_v2_verified/`: verified repeated-split and strong-baseline comparisons.
- `results_cfrg_open_set_v5_verified/`: verified open-set metrics using conformal anomaly scores.
- `results_cfrg_calibration_v2_verified/`: validation-only temperature-scaling diagnostics after the probability-alignment fix.
- Older `v1`/`v2` CFRG directories are historical artifacts and are not the canonical evidence for the final manuscript.
- `重构版论文_v4_20260915/`: **the current manuscript** (English and Chinese), its figures, the `S01-S29` supplementary bundle, the cover letter and the Highlights.
- `results_paper_materials_v3/`: the earlier JISA-layout materials (superseded manuscripts, `Highlights_JISA`, `Graphical_Abstract_JISA` and the provenance tables). The submitted manuscript is the one under `重构版论文_v4_20260915/`; nothing here should be quoted as the final text.
- `data_processed_cic_natural_v4_scale200k/`, `data_processed_cic_natural_v4_full/`: the 413,209-flow and 2,429,503-flow populations behind the scale-sensitivity analyses (supplementary S27 and S29).
- `superseded/`: files kept only for provenance; they are not the source of any number in the manuscript.
- `docs/`: journal requirements, data provenance, and reproducibility notes.

The file-level experiment is a **coverage-aware leave-one-file-out pressure
test**.  Because the eight CIC files do not jointly provide all five target
classes, it is not a category-complete temporal holdout and must not be
reported as proof of full temporal generalization.

## Validation

The current project validation reports the passing-test count printed by the
locked checkout and successful Python byte-compilation. Exact file hashes and
the artifact inventory are recorded in `results_publication_final/MANIFEST.json`.

## Data provenance

See `results_publication_final/external_data_metadata_template.json` and `docs/source_records/`. The metadata deliberately does not infer a standard SPDX license when the provider or mirror does not state one.

## Reproducibility archive

The repository is the public code and derived-artifact archive for this study. It excludes the original datasets and other restricted or large raw files. The exact release commit used for submission is recorded in the manuscript availability statement and in `results_publication_final/MANIFEST.json` (release `v1.11.0`).

## Citation

If you use the code or derived artifacts, cite the associated manuscript and the original dataset papers listed in the manuscript's `References` and `Data references` sections.
