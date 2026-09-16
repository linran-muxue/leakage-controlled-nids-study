# Final Submission Gate v2

## Locally completed

- Canonical protocol is fixed: CIC-IDS2017 curated balanced subset, 70/15/15 stratified split, RCCF Top-60 experts, 100 trees, `min_samples_leaf=2`, seeds 42/2024/3407.
- Manuscript claims are bounded: no universal superiority, SOTA, complete temporal generalization, direct cross-dataset transfer, or end-to-end gateway deployment claim.
- Primary and diagnostic tables use explicit captions; class-level, probability, open-set, independent-benchmark, and limitation evidence are present.
- Supplementary files S1-S15 are copied under `results_publication_final/supplementary/` and indexed.
- English and Chinese DOCX files were regenerated from the final Markdown sources.
- RCCF contract tests, figure generation, Python compilation and manuscript audits are part of the final gate; rerun them after any author metadata edit.

## Must be cleared by the author

- Confirm the public release tag. The manuscript currently cites local tag `v1.0.2`; remote verification was unavailable in this run, so confirm that this tag is pushed and publicly readable before submission.
- Replace CRediT, Funding, competing-interest, author affiliation, correspondence, and ORCID placeholders with factual information.
- Manually verify every DOI, author list, volume/issue/pages or article number, and add an in-text citation for each retained reference. The current source contains 24 reference entries; the reference list is not a substitute for this manual check.
- Confirm the current JISA Guide for Authors and apply its official template or formatting requirements.
- Archive the three dataset source pages and their actual usage terms at the submission date. No SPDX license is asserted where the provider does not state one.
- Inspect the final PDF visually for equation rendering, figure resolution, table pagination, and supplementary links.

## Scientific interpretation

The paper is ready for a conservative reproducible-evaluation submission package, not for an algorithmic-superiority claim. The RCCF mechanism has a near-null fixed-split point difference, no significant hard-label advantage, higher computational cost, and mixed probability quality on CIC; external and open-set evidence is mixed or negative.
