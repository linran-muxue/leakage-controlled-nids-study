"""Extra automated checks for the self-check table."""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    i = text.find(start)
    j = text.find(end, i + 1) if i >= 0 else -1
    return text[i:j] if i >= 0 and j > i else ""


def main() -> None:
    # 1. duplicate figure files
    print("=== figure files ===")
    for folder in ("figures", "figures_en"):
        hashes = {}
        for p in (BASE / folder).glob("*.png"):
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            hashes.setdefault(h, []).append(p.name)
        dups = {h: v for h, v in hashes.items() if len(v) > 1}
        print(f"  {folder}: {len(hashes)} unique images, duplicates={dups or 'none'}")

    # 2. abstract vs body number consistency (English)
    print("=== abstract number consistency (en) ===")
    abstract = section(EN, "## Abstract", "## 1.")
    body = EN.split("## Abstract")[-1].split("## 1.")[-1]
    ab_numbers = set(re.findall(r"\d+\.\d{2,6}|\b\d{1,3}(?:,\d{3})+\b", abstract))
    missing = sorted(n for n in ab_numbers if n not in body)
    print(f"  numbers in abstract: {len(ab_numbers)}, not repeated in body: {missing or 'none'}")

    # 3. declarations
    print("=== declarations ===")
    for key in ["Data and code availability", "Funding", "Declaration of competing interest",
                "Declaration of generative AI", "CRediT"]:
        print(f"  en {key}: {'present' if key in EN else 'MISSING'}")
    for key in ["数据与代码可用性", "基金", "利益冲突声明", "生成式人工智能使用声明", "作者贡献声明"]:
        print(f"  zh {key}: {'present' if key in ZH else 'MISSING'}")
    print("  placeholders remaining: en", len(re.findall(r"To be completed", EN)),
          "| zh", len(re.findall(r"待作者", ZH)))

    # 4. ethics / dual use / license
    print("=== compliance statements ===")
    for key, pat in [("no live attack traffic", r"no scanning|not distributed|no scanning, probing"),
                     ("licence conservatism", r"no SPDX|not infer|do not infer"),
                     ("generative AI disclosure", r"Generative AI tools were used")]:
        print(f"  {key}: {'present' if re.search(pat, EN, re.I) else 'MISSING'}")

    # 5. figure resolution
    print("=== figure dimensions ===")
    try:
        from PIL import Image
        for p in sorted((BASE / "figures_en").glob("*.png"))[:4]:
            with Image.open(p) as im:
                print(f"  {p.name}: {im.width}x{im.height}, dpi={im.info.get('dpi')}")
    except Exception as exc:
        print("  PIL unavailable:", exc)

    # 6. word / char counts
    print("=== length ===")
    print(f"  en words: {len(EN.split())}")
    zh_chars = len(re.sub(r"\s", "", ZH))
    print(f"  zh chars: {zh_chars}")

    # 7. claim coverage: does every contribution in 1.4 map to a results section?
    print("=== contribution-to-results mapping ===")
    contrib = section(EN, "### 1.4 Contributions", "### 1.5")
    for marker in ["reusable leakage-controlled protocol", "identifiability analysis",
                   "quantitative map", "cost account"]:
        print(f"  '{marker}': {'declared' if marker in contrib else 'NOT DECLARED'}")


if __name__ == "__main__":
    main()
