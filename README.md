# Leakage-Controlled Network Intrusion Detection Study

Public repository: https://github.com/linran-muxue/leakage-controlled-nids-study
Submission release: `v1.0.2` (tag present in the local checkout; verify the remote tag before submission)

The locked CIC-IDS2017 publication protocol is **v3b**.  `data_processed_cic_natural_v3b`
is the primary capped natural-prior research population, while
`data_processed_cic_balanced_v3b` is a secondary balanced control subset.  The
older `audit_v1`--`audit_v6`, `data_processed_cic_natural_v1`--`v3`, and
`results_*_v1`/`v2` directories are historical artifacts and must not be used
to reproduce the manuscript tables.

Reproducibility materials for the manuscript *Provenance-Aware and Uncertainty-Aware Evaluation of Network Intrusion Detection Models: A Cross-Fitted Risk-Gated Forest Study*.

## Scope

This repository contains source code, configuration files, audit summaries, derived metrics, prediction outputs, figures, and manuscript-supporting tables. It does **not** redistribute the original CIC-IDS2017, NSL-KDD, or UNSW-NB15 files. Users must obtain those datasets from their respective providers and comply with the providers' terms.

## Reproduction environment

The tested environment is recorded in `requirements-lock.txt`. The project was validated with Python 3.11, scikit-learn, pandas, NumPy, SciPy, matplotlib, seaborn, joblib, openpyxl, python-docx, xgboost, and pytest.

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
- `results_paper_materials_v3/`: manuscript, figures, Highlights, Graphical Abstract, and supplementary index.
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

The repository is the public code and derived-artifact archive for this study. It excludes the original datasets and other restricted or large raw files. The exact release commit used for submission should be recorded in the manuscript and Manifest after the release is pushed.

## Citation

If you use the code or derived artifacts, cite the associated manuscript and the original dataset papers listed in the manuscript's `References` and `Data references` sections.
