from pathlib import Path

root = Path(__file__).resolve().parents[1]
url = 'https://github.com/linran-muxue/leakage-controlled-nids-study'
md = root / 'results_paper_materials_v3' / 'english_sci_manuscript_v1.md'
text = md.read_text(encoding='utf-8')
old = 'The scripts and derived artifacts can be provided by the corresponding author on reasonable request; a persistent public repository or DOI-backed archive should be added before submission when available.'
if old in text:
    text = text.replace(old, f'The scripts and derived artifacts are publicly archived at {url}. The repository excludes the original datasets and records the processing scripts, derived artifacts, source evidence, and locked software environment.')
elif url not in text:
    text = text.replace('## Data and code availability\n', f'## Data and code availability\n\nPublic code repository: {url}\n')
md.write_text(text, encoding='utf-8')
print(f'UPDATED={md}')
