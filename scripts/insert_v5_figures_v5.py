"""Insert the two new figures into Section 5.3 of the restructured manuscript."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    fig11 = "![图 11 决策边距与权重扰动上界的分布，以及命题 2 的可证明不变比例](figures/fig11_margin_bound.png)"
    if "fig11_margin_bound.png" not in text:
        anchor = "**测量五：结论不是调参不足造成的。**"
        if anchor not in text:
            raise SystemExit("figure 11 anchor not found")
        text = text.replace(anchor, fig11 + "\n\n" + anchor, 1)

    fig10 = "![图 10 专家多样性与门控增益的剂量—反应关系](figures/fig10_diversity_dose_response.png)"
    if "fig10_diversity_dose_response.png" not in text:
        anchor = "### 5.4 RQ3"
        if anchor not in text:
            raise SystemExit("figure 10 anchor not found")
        text = text.replace(anchor, fig10 + "\n\n" + anchor, 1)

    MD.write_text(text, encoding="utf-8")
    print("FIGURES_INSERTED")


if __name__ == "__main__":
    main()
