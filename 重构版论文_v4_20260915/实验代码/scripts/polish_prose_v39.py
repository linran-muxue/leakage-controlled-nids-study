"""Sentence-level polish: drop filler lead-ins and vary an echoed sentence.
Each edit removes words rather than adding them, keeps every number unchanged,
and has a mirrored Chinese counterpart where the sentence exists in both.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_EDITS = [
    ("but by very little.", "but only slightly."),
    ("[30-33] Note that the mechanism changes probabilities first",
     "[30-33] The mechanism changes probabilities first"),
    ("Note that the left panel of Figure 4 starts at 0.75",
     "The left panel of Figure 4 starts at 0.75"),
    ("offers no cost-sensitive advantage either. Note that the operating point was selected",
     "offers no cost-sensitive advantage either. The operating point was selected"),
    ("The split-to-split standard deviation over ten repetitions is about 0.011. That is larger "
     "than every aggregation-rule and tuning-budget difference observed here (at most 0.0078), "
     "though not larger than the model-family gaps of 0.0318 and 0.0916.",
     "Repeating the split ten times moves Macro-F1 by about 0.011. That exceeds the "
     "aggregation-rule and tuning-budget differences measured here (at most 0.0078); only the "
     "model-family gaps (0.0318 and 0.0916) are larger."),
]
ZH_EDITS = [
    ("值得注意的是，两者在总体正确率上的配对 McNemar 检验并不显著",
     "两者在总体正确率上的配对 McNemar 检验并不显著"),
    ("1. **划分噪声**：十次重复划分的标准差约为 0.011，大于本文观察到的全部聚合规则差异与"
     "调参预算差异（最大 0.0078），但小于模型族差距 0.0318 与 0.0916。",
     "1. **划分噪声**：十次重复划分会让 Macro-F1 波动约 0.011，超过本文测得的聚合规则差异与"
     "调参预算差异（最大 0.0078）；只有模型族差距（0.0318 与 0.0916）更大。"),
]
def apply(name: str, edits: list[tuple[str, str]]) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            print(f"  [{name}] anchor absent: {old[:56]}...")
    path.write_text(text, encoding="utf-8")
    print(f"{name}: {applied}/{len(edits)} polish edits applied")
def main() -> None:
    apply("English_SCI_Manuscript_v4.md", EN_EDITS)
    apply("中文SCI论文_v4_重构版.md", ZH_EDITS)
if __name__ == "__main__":
    main()
