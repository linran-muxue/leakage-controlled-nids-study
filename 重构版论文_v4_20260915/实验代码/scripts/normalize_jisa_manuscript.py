from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'results_paper_materials_v3' / 'english_sci_manuscript_v1.md'
text = path.read_text(encoding='utf-8')
replacements = {
    'description [1].': 'description (Sharafaldin et al., 2018).',
    'ExtraTrees [15], full-feature random forest [4], chi-square random forest [5]':
        'ExtraTrees (Geurts et al., 2006), full-feature random forest (Breiman, 2001), chi-square random forest (Liu and Setiono, 1995)',
    'percentile 95% intervals [10]': 'percentile 95% intervals (Efron and Tibshirani, 1997)',
    "paired prediction disagreements [9]": "paired prediction disagreements (McNemar, 1947)",
    'pre-defined comparison family [13]': 'pre-defined comparison family (Demšar, 2006)',
    'On UNSW-NB15 [3]': 'On UNSW-NB15 (Moustafa and Slay, 2015)',
    'XGBoost [14]': 'XGBoost (Chen and Guestrin, 2016)',
    'Demšar [13]': 'Demšar (2006)',
}
for old, new in replacements.items():
    text = text.replace(old, new)

marker = '## Data and code availability\n'
insert = '''## Declarations\n\n### CRediT authorship contribution statement\n\nTo be completed by the authors before submission. Contributions should be assigned using the CRediT roles required by JISA.\n\n### Funding\n\nThis research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.\n\n### Declaration of competing interest\n\nThe authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.\n\n### Acknowledgements\n\nTo be completed if applicable.\n\n'''
if '## Declarations\n' not in text:
    text = text.replace(marker, insert + marker)

old_data = 'The final release should add a persistent code repository URL, software environment lock file, and the exact source-record archive.'
new_data = ('The reproducibility package includes the processing scripts, configuration files, audit summaries, '
            'prediction outputs, source-record screenshots, and a locked software environment. The original datasets '
            'are not redistributed because their providers control access and reuse. A persistent public repository '
            'or DOI-backed archive should be inserted here before submission; until then, the archived project package '
            'is the available research record.')
text = text.replace(old_data, new_data)

ai = '''\n## Declaration of Generative AI and AI-assisted technologies in the manuscript preparation process\n\nDuring the preparation of this manuscript, the authors used ChatGPT to assist with language editing, document organization, code documentation, and the presentation of reproducibility materials. The authors reviewed and edited all assisted content, verified the reported data and references, and take full responsibility for the final published version.\n'''
if '## Declaration of Generative AI and AI-assisted technologies' not in text:
    ref_marker = '## References\n'
    text = text.replace(ref_marker, ai + '\n' + ref_marker)

path.write_text(text, encoding='utf-8')
print(f'UPDATED={path}')
