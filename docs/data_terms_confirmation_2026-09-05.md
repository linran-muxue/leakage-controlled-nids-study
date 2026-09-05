# Data-source terms confirmation

## CIC-IDS2017

- Source: Canadian Institute for Cybersecurity, University of New Brunswick.
- URL: https://www.unb.ca/cic/datasets/ids-2017.html
- Local evidence: `docs/source_records/cic_ids2017_source_2026-09-05.png`.
- Evidence-supported description: the page identifies the CIC-IDS2017 intrusion-detection evaluation dataset and describes labelled flow CSV files generated with CICFlowMeter.
- License status: the captured page does not show a standard SPDX license identifier or a complete redistribution license. The manuscript therefore states that the dataset is used for offline research according to the provider's terms and is not redistributed.
- File evidence: local archive SHA-256 is recorded in `results_publication_final/external_data_metadata_template.json`.

## NSL-KDD

- Actual download source: `defcom17/NSL_KDD` raw GitHub URLs, as recorded in the PowerShell download transcript.
- URL: https://github.com/defcom17/NSL_KDD
- Local evidence: `docs/source_records/nsl_kdd_mirror_2026-09-05.png` and `docs/source_records/nsl_kdd_provenance_confirmation.md`.
- Important discrepancy: the saved screenshot shows `Jehuty4949/NSL_KDD`, while the actual download transcript shows `defcom17/NSL_KDD`. The screenshot is not used as proof of the local file source.
- License status: no explicit standard license is visible in the captured record for `defcom17/NSL_KDD`; no license is inferred from GitHub hosting.
- Snapshot status: the exact commit of the downloaded raw files was not preserved; file SHA-256 values are provided instead.

## UNSW-NB15

- Source: UNSW Canberra Cyber project page.
- URL: https://research.unsw.edu.au/projects/unsw-nb15-dataset
- Local evidence: `docs/source_records/unsw_nb15_source_2026-09-05.png`.
- Evidence-supported description: the page describes the generated packet/flow data, the 49-feature representation, the nine attack types, and the official training/testing CSV split. It explicitly requests citation of the associated dataset paper for academic/public use.
- License status: the captured page does not show a standard SPDX license identifier or a general redistribution license. The manuscript therefore cites the original paper, uses the files for offline research, and does not redistribute the original files.

## Reproducibility rule

The project records URLs, access dates, local file hashes, source screenshots, and conservative terms statements. Public availability is not treated as proof of an open-source license. Any later change to the terms text must be supported by a new dated page capture.
