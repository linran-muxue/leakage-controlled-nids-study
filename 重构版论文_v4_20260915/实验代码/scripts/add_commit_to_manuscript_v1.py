from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'results_paper_materials_v3' / 'english_sci_manuscript_v1.md'
text = path.read_text(encoding='utf-8')
url = 'https://github.com/linran-muxue/leakage-controlled-nids-study'
commit = 'd66f7dfd54e20387067fa46dd09020616648946f'
needle = url + '. The repository excludes'
replacement = url + f' (release commit: {commit}). The repository excludes'
if needle in text:
    text = text.replace(needle, replacement)
path.write_text(text, encoding='utf-8')
print(f'UPDATED={path}')
