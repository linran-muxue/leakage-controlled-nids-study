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
