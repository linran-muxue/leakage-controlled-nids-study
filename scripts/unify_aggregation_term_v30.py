"""Use one term for the object being compared: "aggregation rule".
The title and Section 4.3 define the comparison as an aggregation rule
(conditional weighting versus equal voting). The English body slipped into
"aggregation strategy" three times and the Chinese body used 聚合策略 seventeen
times against three uses of the title's term 聚合规则, which reads as a
different object to a Chinese reader.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    en_count = en.count("aggregation strategy")
    body, _, refs = en.partition("## References")
    body = body.replace("aggregation strategy", "aggregation rule")
    en_path.write_text(body + "## References" + refs, encoding="utf-8")
    print(f"EN: {en_count} occurrence(s) of 'aggregation strategy' -> 'aggregation rule'")
    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zh_count = zh.count("聚合策略")
    zh_path.write_text(zh.replace("聚合策略", "聚合规则"), encoding="utf-8")
    print(f"ZH: {zh_count} occurrence(s) of 聚合策略 -> 聚合规则")
if __name__ == "__main__":
    main()
