"""Guards against the classes of defect found during the read-through."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

ISSUES: list[str] = []


def check(label: str, count: int, detail: str = "") -> None:
    if count:
        ISSUES.append(f"{label}: {count} {detail}")
    print(f"{'OK  ' if not count else 'ISSUE'}{label:<44}{count} {detail}")


def main() -> None:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        header = "## References" if "References" in text else "## 参考文献"
        start = text.index(header)
        body, refs = text[:start], text[start:]

        check(f"{name}: reference annotations in body",
              len(re.findall(r"\[no DOI|\[无 DOI", body)), "leaked annotations")
        check(f"{name}: citation after sentence end",
              len(re.findall(r"[a-z\)\u4e00-\u9fff）)]\. ?\[\d", body)), "must precede the full stop")
        check(f"{name}: duplicated table header row",
              len(re.findall(r"^\| Model \|\n\|[-: |]+\|\n\| Model \|", body, flags=re.M)) +
              len(re.findall(r"^\| 模型 \|\n\|[-: |]+\|\n\| 模型 \|", body, flags=re.M)), "duplicate header")
        check(f"{name}: doubled punctuation",
              body.count("。.。") + body.count(".. "), "editing artefact")
        check(f"{name}: dangling 'earlier formulation' phrases",
              body.count("An earlier, purely definitional") + body.count("此前的纯定义式"), "editing artefact")
        check(f"{name}: stale overclaim wording",
              body.count("protocol effects from model effects") + body.count("协议效应与模型效应") +
              body.count("order of magnitude larger than any model"), "overclaim remnant")
        check(f"{name}: duplicated ISBN",
              len(re.findall(r"ISBN 978-0-412-04231-7。\. ISBN", refs)), "duplicated field")

    print()
    if ISSUES:
        print("BODY_HYGIENE_FAILED")
        for item in ISSUES:
            print("  -", item)
        sys.exit(1)
    print("BODY_HYGIENE_OK")


if __name__ == "__main__":
    main()
