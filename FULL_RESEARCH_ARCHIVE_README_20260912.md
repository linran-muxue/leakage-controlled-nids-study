# RCCF/CIC-IDS2017 Full Research Archive

This archive contains the complete local research record for the study,
including final and historical processed-data protocols, experiment outputs,
predictions, scripts, tests, manuscripts, figures, protocol contracts,
literature notes, source metadata, statistical analyses, and environment
specifications.

## Canonical publication layer

- Primary CIC data: `data_processed_cic_natural_v3b`
- Balanced CIC control: `data_processed_cic_balanced_v3b`
- Primary results: `results_rccf_cic_natural_v3b`
- Evidence results: `results_rccf_evidence_v3b`
- External native-label results: `results_rccf_nsl_v2_final`, `results_rccf_unsw_v2_final`
- Manuscripts: `results_paper_materials_v3`
- Publication manifest: `results_publication_final/MANIFEST.json`

## Included material categories

1. Final and historical processed-data outputs and provenance sidecars.
2. Final and historical baseline, ablation, calibration, robustness, latency,
   open-set, repeated-split, nested-CV, NSL-KDD, and UNSW-NB15 results.
3. Per-sample predictions and probabilities where generated.
4. All source code, tests, document builders, audit scripts, and experiment
   runners.
5. English and Chinese manuscripts, tables, figures, Highlights, graphical
   abstract, cover-letter templates, protocols, claim matrices, literature
   notes, DOI records, and submission audits.
6. `requirements-direct.txt`, `requirements-lock.txt`, and repository README.

## Deliberately excluded

- Original CIC-IDS2017 CSV files under `data/raw`.
- Original NSL-KDD and UNSW-NB15 files under `data_external`.
- Python virtual environments (`.venv`).
- Git internals (`.git`).
- Python caches and pytest caches.
- Existing compressed release archives and temporary staging directories.

The excluded raw datasets must be obtained from their providers and used under
the applicable terms. Historical protocols are retained for auditability but
must not be substituted for the locked v3b publication protocol.
