"""Compare the two reference lists and flag unverified DOI markers."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def refs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    block = text.split("## 参考文献")[-1] if "参考文献" in text else text.split("## References")[-1]
    out = []
    for line in block.splitlines():
        m = re.match(r"^\d+\.\s+(.{0,70})", line.strip())
        if m:
            out.append(m.group(1))
    return out


def main() -> None:
    zh = refs(BASE / "中文SCI论文_v4_重构版.md")
    en = refs(BASE / "English_SCI_Manuscript_v4.md")
    print(f"zh entries: {len(zh)} | en entries: {len(en)}")
    za = {r.split(".")[0].strip() for r in zh}
    ea = {r.split(".")[0].strip() for r in en}
    print("first authors only in zh:", sorted(za - ea))
    print("first authors only in en:", sorted(ea - za))
    for label, path in (("zh", BASE / "中文SCI论文_v4_重构版.md"),
                        ("en", BASE / "English_SCI_Manuscript_v4.md")):
        text = path.read_text(encoding="utf-8")
        pattern = r"\[DOI (?:to verify|待核验)\]"
        count = len(re.findall(pattern, text))
        print(f"{label}: DOI-pending entries = {count}")


if __name__ == "__main__":
    main()
