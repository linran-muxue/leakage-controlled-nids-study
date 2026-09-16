from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_manuscripts_use_bounded_claims_and_answer_research_questions():
    for name in ("english_sci_manuscript_final.md", "chinese_sci_manuscript_final.md"):
        text = (ROOT / "results_paper_materials_v3" / name).read_text(encoding="utf-8")
        assert "RQ1" in text and "RQ2" in text and "RQ3" in text and "RQ4" in text
        assert "McNemar" in text
        assert "repeated" in text or "重复" in text
        assert "not support" in text or "不能据此" in text or "普遍" in text
        assert "balanced research subset" in text or "平衡研究子集" in text


def test_english_manuscript_contains_method_mechanism_and_protocol_boundaries():
    text = (ROOT / "results_paper_materials_v3" / "english_sci_manuscript_final.md").read_text(encoding="utf-8")
    for marker in (
        "Estimands and decision rules",
        "When can the gate change a prediction?",
        "Confirmatory versus diagnostic analyses",
        "Practical decision matrix",
        "Study family",
        "Gate identifiability, limiting propositions, and cost–benefit criterion",
        "Reviewer-facing synthesis: claim, evidence, and boundary",
        "normalized weight entropy",
        "Table 1a compares representative recent studies",
    ):
        assert marker in text
