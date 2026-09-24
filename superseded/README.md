# Superseded artifacts

The files below were produced under an **earlier robustness protocol** (tree-level
weighted forest, separate perturbation seeds per model) and are **not** the source of
any number in the current manuscript. They are kept only for provenance.

The manuscript reports robustness from `results_rccf_evidence_v3b/robustness_shared.csv`,
which applies an identical perturbation mask to every model. Under the old protocol the
gap between the weighted forest and extremely randomised trees reaches about 0.12
Macro-F1; under the shared-mask protocol used in the paper the corresponding gaps are
43.30% versus 11.57% relative degradation for 1% Gaussian noise. The two protocols must
not be mixed.

| File | Reason |
|---|---|
| results_publication_final/deployment/robustness_metrics.csv | superseded robustness protocol |
| results_unified_final/deployment/robustness_metrics.csv | superseded robustness protocol |
| results_publication_stage2/deployment/robustness_metrics.csv | superseded robustness protocol |
| results_recheck_unified_v4/deployment/robustness_metrics.csv | superseded robustness protocol |
| results_paper_materials_v2/tables/table_v2_robustness.csv | superseded robustness protocol |

## Unrelated material removed from the release

The public repository also tracked 46 scratch files that are unrelated to
this study: 22 saved journal, article and search pages, the full text of
three unrelated papers together with their previews (6 files),
7 scratch scripts or outputs, and 11 run logs. They no
longer belong to the release, because the README states that the archive does not
redistribute third-party material. The files were moved to the gitignored
`.quarantine/unrelated_material/` folder and are listed, with sizes and SHA-256
digests, in `unrelated_material_manifest_v1.json`.
`scripts/check_release_hygiene_v1.py` fails if any of them is tracked again.
