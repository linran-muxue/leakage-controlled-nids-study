"""Check that every 'N items follow' claim matches the number of items actually listed."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}


def audit(name: str, text: str, ordinal_pattern: str, unit_pattern: str,
          count_patterns: list[tuple[str, str]]) -> None:
    print(f"=== {name} ===")
    headings = re.findall(unit_pattern, text, flags=re.M)
    print(f"  item blocks found: {len(headings)} -> {headings[:8]}")
    for phrase, kind in count_patterns:
        for m in re.finditer(phrase, text, re.I):
            snippet = text[max(0, m.start() - 90):m.end() + 40].replace("\n", " ")
            print(f"  claim [{kind}]: ...{snippet.strip()[:150]}...")


def main() -> None:
    en = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
    zh = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")

    audit("EN readings / measurements", en, r"\*\*(First|Second|Third|Fourth|Fifth|Sixth)",
          r"\*\*(First|Second|Third|Fourth|Fifth|Sixth)[^*]*\*\*",
          [(r"(Two|Three|Four|Five|Six|Seven|Eight) readings follow", "readings"),
           (r"tests them with (\w+) independent measurements", "measurements"),
           (r"has (five|six) components", "statistical components")])

    print()
    audit("ZH 读数 / 测量", zh, r"\*\*(第一|第二|第三|第四|第五|第六)",
          r"\*\*(第[一二三四五六])[^*]*\*\*",
          [(r"本节用(三|四|五|六)组独立测量", "measurements"),
           (r"统计流程包含(四|五|六)项", "statistical components")])

    print()
    print("=== EN contribution / recommendation / control counts ===")
    for phrase in [r"The study contributes \(([ivx]+)\)", r"report at least the following (\w+) items",
                   r"(\w+) control groups are used", r"Three conclusions follow",
                   r"five readings", r"Five readings"]:
        for m in re.finditer(phrase, en, re.I):
            print(f"  ...{en[max(0, m.start() - 60):m.end() + 30].strip()[:140]}...")
    contrib = len(re.findall(r"^\d+\.\s+\*\*", en.split("### 1.4 Contributions")[-1].split("### 1.5")[0], flags=re.M))
    recs = len(re.findall(r"^\d+\.\s+\*\*", en.split("### 6.4")[-1].split("### 6.5")[0], flags=re.M))
    controls = len(re.findall(r"^\d+\.\s+\*\*", en.split("### 4.5")[-1].split("---")[0], flags=re.M))
    print(f"  counted: contributions={contrib}, recommendations={recs}, controls={controls}")


if __name__ == "__main__":
    main()
