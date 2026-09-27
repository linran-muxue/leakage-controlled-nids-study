"""Report which numbered references are cited in the body text."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def cited(path: Path, split_token: str) -> set[int]:
    text = path.read_text(encoding="utf-8")
    body = text.split(split_token)[0]
    found: set[int] = set()
    for group in re.findall(r"\[(\d[\d,\-\s]*)\]", body):
        for part in group.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-")
                found.update(range(int(a), int(b) + 1))
            elif part.isdigit():
                found.add(int(part))
    return found


def main() -> None:
    for label, name, token in (("en", "English_SCI_Manuscript_v4.md", "## References"),
                               ("zh", "中文SCI论文_v4_重构版.md", "## 参考文献")):
        path = BASE / name
        have = cited(path, token)
        missing = sorted(set(range(1, 46)) - have)
        print(f"{label}: cited {len(have)}/47, uncited = {missing}")


if __name__ == "__main__":
    main()
