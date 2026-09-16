# Data card

This archive does **not** redistribute any raw dataset. It records provenance, retrieval
metadata and checksums, and releases the scripts that derive every processed population.

| Dataset | Source | Version / snapshot | Retrieved | Licence status |
|---|---|---|---|---|
| CIC-IDS2017 | Canadian Institute for Cybersecurity (official page) | MachineLearningCSV archive, 8 CSV files | 2026-09-02 | No SPDX identifier displayed; used under the page terms with citation to the original paper |
| NSL-KDD | Public GitHub mirror, KDDTrain+ / KDDTest+ | Mirror snapshot, commit not recorded | 2026-09-03 | No standard licence identifier verified; none inferred |
| UNSW-NB15 | UNSW Canberra Cyber (official project page) | Official training and testing CSV | 2026-09-04 | Page requires citation of the original paper; no SPDX identifier displayed |

SHA-256 checksums for every file are recorded in `results_paper_materials_v3/tables/table_data_source_provenance_v1.csv`
and in the supplementary bundle (S01).

## Derived populations

| Population | Rows | Construction |
|---|---:|---|
| CIC-IDS2017 raw archive | 2,830,743 | eight CSV files, 78 flow features |
| mapped to five closed-set classes | 2,671,766 | PortScan, Infiltration and Heartbleed reserved for open-set diagnostics |
| finite and physically valid | 2,668,729 | 2,741 non-finite rows and 296 physical-range violations removed |
| deduplicated, capped at 20,000 per class | 53,237 | 239,093 duplicate occurrences and 133 conflicting vectors handled before capping |
| balanced control | 3,365 | 673 rows per class |

Both populations are research subsets. Neither equals the full corpus nor represents
production traffic priors.

## Known limitations

- The primary protocol uses 53,237 of 2,668,729 physically valid records (2.0%).
- Only exact duplicates are removed; near-duplicates are quantified (0.36% of the study
  population at four significant digits) but retained.
- No temporal holdout is possible with a category-complete label set on this dataset.
