# Content-quality audit for SCI submission (2026-09-11)

## Improvements completed in the current manuscript

- Added an explicit problem definition, four research questions, and four pre-specified hypotheses.
- Added a related-work section covering learning-based IDS, feature selection, ensemble reliability, open-set recognition, and probability calibration.
- Added a threat model separating information leakage from protocol-induced optimism.
- Added a formal CFRG-Forest definition, OOB-only gate training rule, descriptor definition, and sample-conditional weight equation.
- Added Algorithm 1 pseudocode and asymptotic/constant-factor complexity discussion.
- Added a separate experimental-design section and an evidence hierarchy.
- Added mechanism-level interpretation of why the gate changes few hard predictions.
- Added a hard-label versus probability-quality analysis, external-benchmark interpretation, and a dedicated validity-threat section.
- Replaced unsupported superiority language with evidence-bounded conclusions.
- Added a twelve-study recent-literature comparison matrix with dataset/task scope, fitting boundary, and limitation fields.
- Added three limiting propositions for the gate, a cost–benefit criterion, complete algorithm input/output pseudocode, and mechanism diagnostics (weight entropy, weight CV, probability-vector L1 change, and changed-argmax count).
- Added a compact primary-results table with Macro-F1, balanced accuracy, log loss, Brier, ECE, and timing, plus relative-change calculations and a reviewer-facing claim/evidence/boundary table.
- Normalized supplementary artifacts and figure/table crosswalk paths to the final publication directory.

## Remaining content-level gaps that cannot be solved by wording alone

1. The current CFRG mechanism is not a demonstrated algorithmic breakthrough. The manuscript must remain an evaluation/negative-result study unless a genuinely stronger method is designed and validated.
2. The literature review now contains a 12-study comparison matrix, but a stronger SCI submission may still expand it to approximately 20–30 studies after full-text verification of metadata and protocols.
3. The manuscript now contains 24 reference entries, including recent primary studies; DOI, volume/issue/page and author-order verification remains a manual pre-submission task.
4. Figures are still appended after the narrative in the generated Word file. The final journal version should place each figure/table near its first citation and add panel descriptions, units, sample sizes, and uncertainty definitions.
5. NSL-KDD and UNSW-NB15 results remain independent native-label checks. They cannot be used to claim domain adaptation, transfer learning, or cross-dataset generalization.
6. The CIC result is based on 3,365 balanced flows. The manuscript must keep this limitation in the title/abstract interpretation and should add a prevalence-weighted supplementary analysis if the target journal requires operational relevance.
7. The current temporal/file-level evidence is coverage auditing, not a category-complete temporal holdout. A stronger temporal claim requires a new protocol and new experiments.
8. Data-provider terms, Funding, conflict of interest, author identity, ORCID, and the official target-journal template still require author confirmation.

## Current defensible positioning

The strongest defensible positioning is a reproducible, leakage-controlled and uncertainty-aware evaluation study with a bounded CFRG-Forest mechanism and documented failure boundaries. It should not be presented as SOTA, universally superior, or a solved open-set detector.
