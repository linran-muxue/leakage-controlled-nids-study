from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_final_builder_uses_final_sources_and_canonical_figures():
    script = (ROOT / "scripts" / "build_final_manuscripts_v1.py").read_text(encoding="utf-8")
    assert 'english_sci_manuscript_final.md' in script
    assert 'chinese_sci_manuscript_final.md' in script
    assert 'results_publication_final" / "figures' in script
    assert 'Supplementary Table S10. UNSW-NB15 split-sensitivity protocols' in script
    assert 'english_sci_manuscript_v3.md' not in script
