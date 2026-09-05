# Public code release plan

The public repository URL supplied by the author is https://github.com/linran-muxue/leakage-controlled-nids-study. The local project is prepared for a selective reproducibility release; the original datasets remain excluded.

## Files safe to publish

- `src/`
- `scripts/`
- `tests/`
- `docs/`
- `results_paper_materials_v3/` (manuscript-supporting text, tables, figures, Highlights, Graphical Abstract)
- `results_publication_final/` (derived results, hashes, configuration, Manifest)
- `results_nsl_kdd_fair_v2/` (derived NSL-KDD results only)
- `results_unsw_nb15_independent_v4/` and related derived result summaries
- `README.md`, `LICENSE`, `requirements-direct.txt`, `requirements-lock.txt`

## Files not to publish

- Original CIC-IDS2017, NSL-KDD, and UNSW-NB15 files.
- PCAP files, ZIP archives, and local virtual environments.
- Any file containing personal author information before the title page is finalized.

## Author actions required

1. Confirm that the supplied repository is owned by the author and is public.
2. Upload the safe files listed above, or allow the local Git push from the project directory.
3. Create a tagged release or archive and record the commit SHA/DOI in `results_publication_final/MANIFEST.json`.

The manuscript cites the supplied public URL and release tag `v1.0.0`. The tag should be created after the final submission-material commit and pushed to GitHub.
