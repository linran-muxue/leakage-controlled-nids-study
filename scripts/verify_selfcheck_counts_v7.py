"""Verify that the self-check table is internally consistent.

The table is the document a supervisor or reviewer reads first, so a stale
total, a duplicated item id or a status that contradicts the summary row is a
real defect. This check now fails loudly instead of only printing counts.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SC = (BASE / "论文自查表.md").read_text("utf-8")

problems: list[str] = []

# item rows live in layers A-G, before the closing action list
head = SC.split("## 自查结论与行动清单")[0]
item_lines = re.findall(r"^\| [A-G]\d+ \|.*$", head, flags=re.M)
ids = re.findall(r"^\| ([A-G]\d+) \|", head, flags=re.M)

passed = partial = missing = unlabelled = 0
for line in item_lines:
    if "**通过**" in line:
        passed += 1
    elif "**部分通过**" in line:
        partial += 1
    elif "**缺失**" in line:
        missing += 1
    else:
        unlabelled += 1
        print("  unlabelled row:", line[:70])

print(f"item rows: {len(ids)}")
print(f"pass={passed} partial={partial} missing={missing} total={passed + partial + missing}")
if unlabelled:
    problems.append(f"{unlabelled} unlabelled item row(s)")

duplicates = sorted({i for i in ids if ids.count(i) > 1})
if duplicates:
    problems.append(f"duplicate ids {duplicates}")
print("duplicate ids:", duplicates or "none")

# layer table must add up
layer_rows = re.findall(
    r"^\| ([A-G]) [^|]*\| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", head, flags=re.M)
layer_total = sum(int(r[1]) for r in layer_rows)
layer_pass = sum(int(r[2]) for r in layer_rows)
layer_partial = sum(int(r[3]) for r in layer_rows)
layer_missing = sum(int(r[4]) for r in layer_rows)
print(f"layer rows: {len(layer_rows)} sum={layer_total}/{layer_pass}/{layer_partial}/{layer_missing}")
if layer_rows and (layer_total, layer_pass, layer_partial, layer_missing) != (len(ids), passed, partial, missing):
    problems.append(
        f"layer table sums {layer_total}/{layer_pass}/{layer_partial}/{layer_missing} "
        f"!= counted {len(ids)}/{passed}/{partial}/{missing}")

summary = re.search(
    r"\| \*\*合计\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", SC)
if not summary:
    problems.append("summary row not found")
    print("summary row: not found")
else:
    got = tuple(int(g) for g in summary.groups())
    print("summary row:", got)
    if got != (len(ids), passed, partial, missing):
        problems.append(f"summary row {got} != counted {(len(ids), passed, partial, missing)}")

# the closing section must agree with the summary: no missing items claim
tail = SC.split("## 自查结论与行动清单")[1] if "## 自查结论与行动清单" in SC else ""
# only the conclusion sentence counts; the rest of the section legitimately
# quotes the stale wording it replaced
claimed = re.search(r"\*\*(\d+) 项检查中 (\d+) 项通过、(\d+) 项部分通过、(\d+) 项缺失。?\*\*", tail)
if not claimed:
    claimed = re.search(r"\*\*(\d+) 项通过、(\d+) 项部分通过、(\d+) 项缺失。?\*\*", tail)
    if not claimed:
        problems.append("closing conclusion carries no parsable counts")
if claimed:
    groups = [int(g) for g in claimed.groups()]
    got = tuple(groups[-3:])
    if got != (passed, partial, missing):
        problems.append(f"closing conclusion {got} != counted {(passed, partial, missing)}")
    elif len(groups) == 4 and groups[0] != len(ids):
        problems.append(f"closing conclusion claims {groups[0]} items, table has {len(ids)}")
    print("closing conclusion:", got)

# supplementary naming format
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
print()
print("manuscript supplementary ids:", re.findall(r"^\| (S\d+) \|", EN, flags=re.M)[:6])
bundle_dir = BASE / "补充材料_S01_S26"
if not bundle_dir.exists():
    problems.append(f"supplementary bundle directory missing: {bundle_dir.name}")
else:
    bundle = sorted(set(re.findall(
        r"^\| (S\d+) \|", (bundle_dir / "README.md").read_text(encoding="utf-8"), flags=re.M)))
    print(f"bundle supplementary ids: {bundle[:6]} ({len(bundle)} entries)")
    en_ids = sorted(set(re.findall(r"^\| (S\d+) \|", EN, flags=re.M)))
    if not set(en_ids) <= set(bundle):
        problems.append(f"bundle misses manuscript ids {sorted(set(en_ids) - set(bundle))}")

print()
if problems:
    for p in problems:
        print(f"ISSUE {p}")
    print("SELFCHECK_MISMATCH")
    raise SystemExit(1)
print("SELFCHECK_OK")
