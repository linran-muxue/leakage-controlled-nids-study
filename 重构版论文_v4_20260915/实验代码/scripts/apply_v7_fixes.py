"""Fix the four issues found by the fresh audit."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

NEW_HIGHLIGHTS = """# Highlights

- Conditional ensemble weighting is equivalent to equal voting within 0.005 Macro-F1.
- Across ten seeds the per-seed sign splits five to five, with no advantage.
- 99.91% of test rows are provably immune to the gate; no row changes label.
- Feature-value corruption costs far more accuracy than corrupted labels.
- Protocol choices move Macro-F1 by 0.073, against 0.0005 for the aggregation rule.

---

# 中文要点（供中文稿使用）

- 条件集成加权与等权投票在 0.005 Macro-F1 边界内等价。
- 十个种子上逐种子方向五正五负，无优势。
- 99.91% 的测试行可被证明不受门控影响，实际改判 0 条。
- 特征值污染造成的精度损失远大于标签污染。
- 类别先验带来的差异为 0.073，而聚合策略仅 0.0005。
"""


def two_digit_ids(text: str) -> str:
    """S1..S9 -> S01..S09 inside supplementary table rows and S-references."""
    text = re.sub(r"\bSupplementary S(\d)\b", r"Supplementary S0\1", text)
    text = re.sub(r"补充材料 S(\d)\b", r"补充材料 S0\1", text)
    text = re.sub(r"^\| S(\d) \|", r"| S0\1 |", text, flags=re.M)
    return text


def main() -> None:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        path = BASE / name
        path.write_text(two_digit_ids(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"IDS_NORMALISED={name}")

    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    en = en.replace("![Figure 4. Main results and paired bootstrap intervals]",
                    "![Figure 4. Main results on both populations (ten seeds for the natural-prior panel) "
                    "and paired bootstrap intervals]", 1)
    en_path.write_text(en, encoding="utf-8")

    (BASE / "Highlights_v4.md").write_text(NEW_HIGHLIGHTS, encoding="utf-8")
    print("HIGHLIGHTS_UPDATED")

    lengths = [(l, len(l) - 2) for l in NEW_HIGHLIGHTS.splitlines() if l.startswith("- ")]
    over = [t for t, n in lengths if n > 85]
    print("highlights over 85 chars:", over or "none")


if __name__ == "__main__":
    main()
