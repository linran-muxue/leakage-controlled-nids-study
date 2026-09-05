from scripts.audit_manuscript_claims_v1 import MANUSCRIPT


def test_canonical_manuscript_has_no_stale_table_or_metric_claims():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert "表A36" not in text
    assert "表A43" not in text
    assert "95.97%" not in text
    assert "96.05%" not in text
