"""Make the headline numbers in the front matter match the body exactly.
Three mismatches: the abstract and cover letter rounded the headline difference
to -0.00046 where the body says -0.000456, they rounded the class-prior effect
to +0.072 against +0.0725, and they called the 4.6 throughput ratio "per row"
although the body's per-row latency ratio is 4.9.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EDITS = {
    "English_SCI_Manuscript_v4.md": [
        ("differ by -0.00046 Macro-F1", "differ by -0.000456 Macro-F1"),
        ("move Macro-F1 by +0.072 and up to +0.0060", "move Macro-F1 by +0.0725 and up to +0.0060"),
        ("4.6 times slower per row than one forest", "4.6 times lower in throughput than one forest"),
    ],
    "中文SCI论文_v4_重构版.md": [
        ("平均差为 −0.00046，逐种子方向五正五负", "平均差为 −0.000456，逐种子方向五正五负"),
        ("分别带来 +0.072 与至多 +0.0060 的变化", "分别带来 +0.0725 与至多 +0.0060 的变化"),
        ("该机制体积是单个等权森林的 4.1 倍、单行慢 4.6 倍", "该机制体积是单个等权森林的 4.1 倍、吞吐低 4.6 倍"),
    ],
    "Cover_Letter_JISA_v4.md": [
        ("differ by -0.00046 Macro-F1", "differ by -0.000456 Macro-F1"),
        ("4.1 times larger and 4.6 times slower per row than a single forest",
         "4.1 times larger and 4.6 times lower in throughput than a single forest"),
    ],
}
def main() -> None:
    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        applied = 0
        for old, new in edits:
            if old in text:
                text = text.replace(old, new, 1)
                applied += 1
            else:
                print(f"  [{name}] anchor absent: {old[:52]}...")
        path.write_text(text, encoding="utf-8")
        print(f"{name}: {applied}/{len(edits)} applied")
if __name__ == "__main__":
    main()
