"""Round 10b: close the last three cross-language gaps found by the number diff."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_EDITS = [
    # 1. Condition B: replace the loose 3,500 ratio with the traceable Measurement 4 range
    (
        "The measured mean L1 probability change is 0.000299 with a maximum of 0.003473, "
        "while the median decision margin is 1.0 - a ratio of roughly 3,500. "
        "Measurement 4 formalises this: 99.91% of rows are provably immune under the a priori bound.",
        "The measured mean L1 probability change is 0.000299 with a maximum of 0.003473, "
        "while the median decision margin is 1.0, three orders of magnitude above the largest "
        "observed movement. Measurement 4 formalises this: under the a priori bound 99.91% of "
        "rows are provably immune, with a median margin-to-bound ratio of 3,469 to 5,038.",
    ),
    # 2. Section 6.2 item 1: use the same precision as the Chinese manuscript
    (
        "though not larger than the model-family gaps of 0.032 and 0.092.",
        "though not larger than the model-family gaps of 0.0318 and 0.0916.",
    ),
]

ZH_EDITS = [
    (
        "本文测得的平均概率 L1 变化为 0.000299，最大为 0.003473，而多数样本的类别边距远大于此。",
        "本文测得的平均概率 L1 变化为 0.000299，最大为 0.003473，而中位类别边距为 1.0，"
        "比最大的概率移动还大约三个数量级。测量四给出了形式化判据：在事前上界下，99.91% 的样本"
        "可证明不受权重影响，边距与扰动上界的比值中位数为 3469 至 5038 倍。",
    ),
]


def apply(path: Path, edits: list[tuple[str, str]], tag: str) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            print(f"  [{tag}] anchor absent (already applied?): {old[:56]}...")
    path.write_text(text, encoding="utf-8")
    print(f"{tag}_APPLIED={applied}/{len(edits)}")
    return applied


def main() -> None:
    apply(BASE / "English_SCI_Manuscript_v4.md", EN_EDITS, "EN")
    apply(BASE / "中文SCI论文_v4_重构版.md", ZH_EDITS, "ZH")


if __name__ == "__main__":
    main()
