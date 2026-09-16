"""Place Figure 1 at the head of Section 3 (both languages) and add Figure 3 to the
English Section 4.2, so that figures appear in numeric order."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def fix(path: Path, heading: str, fig1_line: str, section_anchor: str | None = None,
        fig3_line: str | None = None, fig3_anchor: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if fig1_line in text:
        text = text.replace(fig1_line + "\n\n", "", 1)
        text = text.replace(fig1_line, "", 1)
        if heading not in text:
            raise SystemExit(f"heading not found in {path.name}")
        text = text.replace(heading, heading + "\n\n" + fig1_line, 1)
    if fig3_line and fig3_anchor and fig3_line not in text:
        if fig3_anchor not in text:
            raise SystemExit(f"figure 3 anchor not found in {path.name}")
        text = text.replace(fig3_anchor, fig3_line + "\n\n" + fig3_anchor, 1)
    path.write_text(text, encoding="utf-8")
    print(f"FIXED={path.name}")


def main() -> None:
    fix(BASE / "中文SCI论文_v4_重构版.md",
        heading="## 3 数据、来源与协议",
        fig1_line="![图 1 泄漏受控研究框架与信息边界](figures/fig1_protocol_pipeline.png)")
    fix(BASE / "English_SCI_Manuscript_v4.md",
        heading="## 3. Data, Provenance and Protocol",
        fig1_line="![Figure 1. Leakage-controlled research framework and information boundary](figures_en/fig1_protocol_pipeline.png)",
        fig3_line="![Figure 3. Mechanism of conditional weighting and the three identifiability conditions](figures_en/fig3_rccf_mechanism.png)",
        fig3_anchor="Algorithm 1 states the full procedure with the information boundary made explicit.")


if __name__ == "__main__":
    main()
