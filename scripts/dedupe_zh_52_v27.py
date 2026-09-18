"""Remove the duplicated balanced-control sentence left in the Chinese 5.2.
An earlier alignment edit replaced the head of the paragraph and left the old
tail in place, so the same training pair and the same +/-0.01 summary were
stated twice.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"
OLD = ("差距在平衡控制协议上更大：训练 9.13 秒对 0.45 秒。这些代价换来的最好说法是 Macro-F1 变化在 ±0.01 以内。"
       "平衡控制下的差距更明显：9.13 秒对 0.45 秒。若把支付这些代价换来的收益写成一句话，只能是「Macro-F1 变化在 ±0.01 以内」。")
NEW = "差距在平衡控制协议上更大：训练 9.13 秒对 0.45 秒。这些代价换来的最好说法是 Macro-F1 变化在 ±0.01 以内。"
def main() -> None:
    text = ZH.read_text(encoding="utf-8")
    if OLD not in text:
        print("anchor absent (already deduplicated?)")
        return
    ZH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("ZH 5.2 duplicate sentence removed")
if __name__ == "__main__":
    main()
