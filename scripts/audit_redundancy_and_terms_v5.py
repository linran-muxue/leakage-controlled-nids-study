"""Third-pass audit: duplicated sentences, terminology consistency, heading parity."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DOCS = {"zh": BASE / "中文SCI论文_v4_重构版.md",
        "en": BASE / "English_SCI_Manuscript_v4.md"}


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？])|(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def main() -> None:
    for label, path in DOCS.items():
        text = path.read_text(encoding="utf-8")
        body = text.split("## 参考文献")[0] if "参考文献" in text else text.split("## References")[0]
        sents = sentences(body)
        counts = Counter(sents)
        dups = [(s, c) for s, c in counts.items() if c > 1]
        print(f"=== {label} ===")
        print(f"  sentences: {len(sents)}, duplicated: {len(dups)}")
        for s, c in dups[:5]:
            print(f"    x{c}: {s[:90]}")
        # near-duplicate detection: identical 12-word shingles
        words = re.findall(r"\w+", body.lower())
        shingles = Counter(tuple(words[i:i + 12]) for i in range(max(0, len(words) - 12)))
        heavy = [(c, " ".join(s)) for s, c in shingles.items() if c >= 3]
        print(f"  12-gram shingles repeated >=3 times: {len(heavy)}")
        for c, s in heavy[:4]:
            print(f"    x{c}: {s[:90]}")
        print()

    print("=== heading alignment (first 12 pairs) ===")
    zh = re.findall(r"^#{2,3}\s+(.*)$", DOCS["zh"].read_text(encoding="utf-8"), flags=re.M)
    en = re.findall(r"^#{2,3}\s+(.*)$", DOCS["en"].read_text(encoding="utf-8"), flags=re.M)
    for a, b in list(zip(zh, en))[:12]:
        print(f"  zh: {a[:46]:<48} en: {b[:46]}")


if __name__ == "__main__":
    main()
