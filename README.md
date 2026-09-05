# Leakage-Controlled Network Intrusion Detection Study

Public repository: https://github.com/linran-muxue/leakage-controlled-nids-study
Submission release: `v1.0.0`

Reproducibility materials for the manuscript *Leakage-Controlled Feature Selection and Random-Forest Ensembles for Network Intrusion Detection: A Reproducible Multi-Dataset Study*.

## Scope

This repository contains source code, configuration files, audit summaries, derived metrics, prediction outputs, figures, and manuscript-supporting tables. It does **not** redistribute the original CIC-IDS2017, NSL-KDD, or UNSW-NB15 files. Users must obtain those datasets from their respective providers and comply with the providers' terms.

## Reproduction environment

The tested environment is recorded in `requirements-lock.txt`. The project was validated with Python 3.11, scikit-learn, pandas, NumPy, SciPy, matplotlib, seaborn, joblib, openpyxl, python-docx, xgboost, and pytest.

## Main artifacts

- `src/`: reusable data and experiment components.
- `scripts/`: audit, experiment, statistical-analysis, and document-generation scripts.
- `tests/`: automated tests.
- `results_publication_final/`: locked CIC results and uncertainty outputs.
- `results_unsw_nb15_independent_v4/`: UNSW-NB15 independent benchmark outputs.
- `results_nsl_kdd_fair_v2/`: NSL-KDD independent benchmark outputs.
- `results_paper_materials_v3/`: manuscript, figures, Highlights, Graphical Abstract, and supplementary index.
- `docs/`: journal requirements, data provenance, and reproducibility notes.

## Validation

The current project validation reports 66 passing tests and successful Python byte-compilation. Exact file hashes and the artifact inventory are recorded in `results_publication_final/MANIFEST.json`.

## Data provenance

See `results_publication_final/external_data_metadata_template.json` and `docs/source_records/`. The metadata deliberately does not infer a standard SPDX license when the provider or mirror does not state one.

## Reproducibility archive

The repository is the public code and derived-artifact archive for this study. It excludes the original datasets and other restricted or large raw files. The exact release commit used for submission should be recorded in the manuscript and Manifest after the release is pushed.

## Citation

If you use the code or derived artifacts, cite the associated manuscript and the original dataset papers listed in the manuscript's `References` and `Data references` sections.
