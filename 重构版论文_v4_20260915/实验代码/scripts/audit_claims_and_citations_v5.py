"""Second-pass audit: in-text citations, claim-evidence mapping, wording precision."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

DOCS = {"zh": BASE / "中文SCI论文_v4_重构版.md",
        "en": BASE / "English_SCI_Manuscript_v4.md"}


def main() -> None:
    for label, path in DOCS.items():
        text = path.read_text(encoding="utf-8")
        body = text.split("## 参考文献")[0] if "参考文献" in text else text.split("## References")[0]

        print(f"=== {label}: {path.name} ===")
        numeric = re.findall(r"\[(\d{1,2})\]", body)
        print("  numeric citation markers [n] in body:", len(numeric))
        author_year = re.findall(r"([A-Z][a-z]+(?: et al\.| and [A-Z][a-z]+)?)\s*\((\d{4})\)", body)
        named = re.findall(r"\b([A-Z][a-z]+ (?:et al\.|and [A-Z][a-z]+))", body)
        print("  author-year style mentions:", len(author_year))
        print("  sample named mentions:", sorted(set(named))[:10])

        # Validation vs test wording around the gate-tuning claim
        for key in ["108", "862", "gate hyper-parameter", "门控的全部超参数"]:
            for m in re.finditer(re.escape(key), body):
                s = max(0, m.start() - 160)
                snippet = body[s:m.end() + 160].replace("\n", " ")
                print(f"  [{key}] ...{snippet}...")
                break
        print()


if __name__ == "__main__":
    main()
