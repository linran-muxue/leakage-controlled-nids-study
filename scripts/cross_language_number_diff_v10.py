"""Compare the numeric content of the two manuscripts to locate stale values."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")

DECIMAL = re.compile(r"\d+\.\d{2,6}")
INTEGER = re.compile(r"\b\d{1,3}(?:[, ]\d{3})+\b|\b\d{4,7}\b")


def numbers(text: str, ref_marker: str) -> set[str]:
    body = text.split(ref_marker)[0]
    found = DECIMAL.findall(body) + INTEGER.findall(body)
    # separators are stylistic: drop them so the two languages are comparable
    return {f.replace(" ", "").replace(",", "") for f in found}


def main() -> None:
    en = numbers(EN, "## References")
    zh = numbers(ZH, "## 参考文献")
    only_en = sorted(en - zh)
    only_zh = sorted(zh - en)
    print(f"numeric tokens: en={len(en)} zh={len(zh)}")
    aligned = not only_en and not only_zh
    print(f"alignment: {'ALIGNED' if aligned else 'MISMATCH'}")
    if aligned:
        return
    print()
    print(f"present only in the English manuscript ({len(only_en)}):")
    for token in only_en:
        ctx = [l for l in EN.splitlines() if token in l or token.replace(".", "") in l][:1]
        snippet = ctx[0][:110] if ctx else ""
        print(f"  {token:<14} {snippet}")
    print()
    print(f"present only in the Chinese manuscript ({len(only_zh)}):")
    for token in only_zh:
        ctx = [l for l in ZH.splitlines() if token in l][:1]
        snippet = ctx[0][:110] if ctx else ""
        print(f"  {token:<14} {snippet}")


if __name__ == "__main__":
    main()
