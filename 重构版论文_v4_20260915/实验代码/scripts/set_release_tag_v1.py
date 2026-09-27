from pathlib import Path

root = Path(__file__).resolve().parents[1]
replacements = {
    root / 'results_paper_materials_v3' / 'english_sci_manuscript_v1.md': (
        '(release commit: d66f7dfd54e20387067fa46dd09020616648946f)',
        '(release `v1.0.0`)'
    ),
    root / 'README.md': (
        'Public release commit: `d66f7dfd54e20387067fa46dd09020616648946f`',
        'Submission release: `v1.0.0`'
    ),
    root / 'docs' / 'public_code_release_plan.md': (
        'The manuscript cites the supplied public URL. The current public release commit is `d66f7dfd54e20387067fa46dd09020616648946f`.',
        'The manuscript cites the supplied public URL and release tag `v1.0.0`. The tag should be created after the final submission-material commit and pushed to GitHub.'
    ),
}
for path, (old, new) in replacements.items():
    text = path.read_text(encoding='utf-8')
    path.write_text(text.replace(old, new), encoding='utf-8')
    print(f'UPDATED={path}')
