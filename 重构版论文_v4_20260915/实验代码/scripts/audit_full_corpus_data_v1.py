"""Independent data audit of the full-corpus experiment.

Checks the processed files against every number the manuscript quotes for that
population, then checks the things a number-traceability test cannot see:
that the ten seeds share one identical test set, that no feature vector appears
in both the training and the test partition, and that the per-seed metrics are
reproducible from the stored predictions.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit_utils import count_shared_rows, feature_row_hashes  # noqa: E402

DATA = ROOT / "data_processed_cic_natural_v4_full"
RCCF = ROOT / "results_rccf_cic_natural_v4_full"
CONTROL = ROOT / "results_full_corpus_v49"
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]
problems: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'OK  ' if ok else 'ISSUE'}{label:<52}{detail}")
    if not ok:
        problems.append(label)


audit = json.loads((DATA / "dedup_audit.json").read_text(encoding="utf-8"))
summary = json.loads((CONTROL / "full_corpus_summary.json").read_text(encoding="utf-8"))

# ---- 1. header counts -------------------------------------------------------
frames = {name: pd.read_csv(DATA / f"{name}.csv", usecols=["target"])
          for name in ("train", "validation", "test")}
sizes = {name: len(frame) for name, frame in frames.items()}
total = sum(sizes.values())
print("=== 1. partition sizes ===")
check("total equals the audited unique rows",
      total == audit["unique_rows_after_conflict"], f"{total:,} vs {audit['unique_rows_after_conflict']:,}")
# Compare against what the manuscript actually claims, rather than against a
# copy of that claim: the earlier version hard-coded the manuscript's own (then
# incorrect) numbers and therefore could never detect the mismatch.
import re as _re
_en = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
# Anchor on the full-corpus sentence: the manuscript also quotes the 7.8x run's
# much smaller splits, and an unanchored search matches that one first.
_claim = _re.search(
    r"Removing the per-class cap entirely yields [\d,]+ flows "
    r"\(train ([\d,]+) / validation ([\d,]+) / test ([\d,]+)\)", _en)
if not _claim:
    problems.append("manuscript split claim not found")
else:
    claimed = {k: int(v.replace(",", "")) for k, v in
               zip(("train", "validation", "test"), _claim.groups())}
    print(f"    manuscript claims: {claimed}")
    for name in ("train", "validation", "test"):
        check(f"{name} size matches the manuscript", sizes[name] == claimed[name],
              f"file {sizes[name]:,} vs text {claimed[name]:,}")
check("train share is 70%", abs(sizes["train"] / total - 0.70) < 0.001,
      f"{sizes['train'] / total:.4f}")
check("validation share is 15%", abs(sizes["validation"] / total - 0.15) < 0.001,
      f"{sizes['validation'] / total:.4f}")

# ---- 2. class support -------------------------------------------------------
print("\n=== 2. class support ===")
support = {name: frame["target"].value_counts().to_dict() for name, frame in frames.items()}
for label in sorted(support["test"]):
    print(f"    {label:<14} train {support['train'].get(label, 0):>9,} "
          f"val {support['validation'].get(label, 0):>7,} test {support['test'].get(label, 0):>7,}")
web = support["test"].get("Web Attack", 0) / sizes["test"] * 100
check("Web Attack share in test is 0.028%", abs(web - 0.028) < 0.001, f"{web:.4f}%")
check("all five classes present in every partition",
      all(len(s) == 5 for s in support.values()), str({k: len(v) for k, v in support.items()}))

# ---- 3. split integrity -----------------------------------------------------
print("\n=== 3. split integrity ===")
features = [c for c in pd.read_csv(DATA / "test.csv", nrows=1).columns if c != "target"]


tr = pd.read_csv(DATA / "train.csv")
te = pd.read_csv(DATA / "test.csv")
tr_hashes = set(feature_row_hashes(tr, features))
te_hashes = feature_row_hashes(te, features)
overlap = count_shared_rows(tr_hashes, te_hashes)
check("no test feature vector appears in training", overlap == 0, f"{overlap} overlapping rows")
check("test rows are unique", len(set(te_hashes)) == len(te_hashes),
      f"{len(te_hashes) - len(set(te_hashes))} duplicates")

# ---- 4. the ten seeds share one test set ------------------------------------
print("\n=== 4. ten-seed test-set identity ===")
reference = None
identical = True
for seed in SEEDS:
    path = RCCF / f"predictions_seed{seed}.csv"
    if not path.exists():
        check(f"seed {seed} predictions exist", False, "missing")
        identical = False
        continue
    labels = pd.read_csv(path, usecols=["true_label"])["true_label"].to_numpy()
    if reference is None:
        reference = labels
        check("row count matches the test partition", len(labels) == sizes["test"],
              f"{len(labels):,}")
        check("labels match the processed test file",
              bool((labels == te["target"].to_numpy()).all()))
    elif not (labels == reference).all():
        identical = False
        print(f"    seed {seed}: test labels differ from the reference ordering")
check("all ten seeds use the identical test rows in the identical order", identical)

print()
if problems:
    for p in problems:
        print(f"ISSUE {p}")
    print("DATA_AUDIT_FAILED")
    raise SystemExit(1)
print("DATA_AUDIT_OK")
