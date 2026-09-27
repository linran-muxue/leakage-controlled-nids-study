"""Require every number in an abstract to also appear in the body.

The Highlights and the cover letter are already checked this way by
``check_aux_documents_v13.py``, but the abstract was not: it is the most-quoted
part of the paper, and a number that appears only there cannot be checked
against any source file by a reader.  This closes that gap.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DECIMAL = re.compile(r"\d+\.\d{2,6}")
INTEGER = re.compile(r"\b\d{1,3}(?:[, ]\d{3})+\b|\b\d{4,7}\b")
problems: list[str] = []


def tokens(text: str) -> set[str]:
    return {f.replace(" ", "").replace(",", "")
            for f in DECIMAL.findall(text) + INTEGER.findall(text)}


def check(name: str, abstract: str, body: str, label: str) -> None:
    only_abstract = sorted(tokens(abstract) - tokens(body))
    print(f"  {label}: {len(tokens(abstract))} numeric token(s) in the abstract, "
          f"{len(only_abstract)} not found in the body")
    if only_abstract:
        problems.append(f"{name}: abstract quotes {only_abstract} that the body never states")


en = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
head, _, tail = en.partition("## Abstract")
body_all = head + tail
abstract = body_all[:body_all.find("**Keywords")]
check("English", abstract, body_all[len(abstract):], "English")

zh = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
i = zh.find("## 摘要")
j = zh.find("\n---", i)
if j < 0:
    j = zh.find("## 1", i)
check("Chinese", zh[i:j], zh[:i] + zh[j:], "Chinese")

print()
if problems:
    for problem in problems:
        print(f"ISSUE {problem}")
    print("ABSTRACT_NUMBERS_FAILED")
    raise SystemExit(1)
print("ABSTRACT_NUMBERS_OK")
