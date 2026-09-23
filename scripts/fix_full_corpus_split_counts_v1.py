"""Correct the split counts of the full-corpus population.

The manuscript, the review report and the two generators that produced them all
state train 1,700,651 / validation 364,426, but the processed files and the run
manifest say 1,700,652 / 364,425.  The test split (364,426) is correct; the
other two are each off by one, so the sum still reconciles and no check caught
it.  Corrected here, with the generators fixed so a rebuild cannot reintroduce
the error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

manifest = json.loads((ROOT / "results_rccf_cic_natural_v4_full" /
                       "run_manifest.json").read_text(encoding="utf-8"))
train, val, test = manifest["train_rows"], manifest["validation_rows"], manifest["test_rows"]
expected = (1700652, 364425, 364426)
if (train, val, test) != expected:
    raise SystemExit(f"unexpected split sizes in the manifest: {train}/{val}/{test}")
print(f"manifest split: train {train:,} / validation {val:,} / test {test:,}")

EN_OLD = "(train 1,700,651 / validation 364,426 / test 364,426)"
EN_NEW = f"(train {train:,} / validation {val:,} / test {test:,})"
ZH_OLD = "（训练 1 700 651 / 验证 364 426 / 测试 364 426）"
ZH_NEW = (f"（训练 {train:,}".replace(",", " ") + f" / 验证 {val:,}".replace(",", " ") +
          f" / 测试 {test:,}".replace(",", " ") + "）")

TARGETS: list[tuple[Path, str, str, str]] = [
    (BASE / "English_SCI_Manuscript_v4.md", EN_OLD, EN_NEW, "English manuscript"),
    (BASE / "中文SCI论文_v4_重构版.md", ZH_OLD, ZH_NEW, "Chinese manuscript"),
    (BASE / "遗漏问题审查报告.md", ZH_OLD, ZH_NEW, "review report"),
    (ROOT / "scripts" / "finalize_full_corpus_v56.py", EN_OLD, EN_NEW, "finaliser (EN)"),
    (ROOT / "scripts" / "finalize_full_corpus_v56.py", ZH_OLD, ZH_NEW, "finaliser (ZH)"),
    (ROOT / "scripts" / "append_review_round_v19.py", ZH_OLD, ZH_NEW, "review-round generator"),
    # These two carry the counts inside a longer sentence that ends with a
    # semicolon rather than a closing parenthesis, so they need a separate
    # anchor.
    (BASE / "遗漏问题审查报告.md", "训练 1 700 651 / 验证 364 426 / 测试 364 426；",
     "训练 1 700 652 / 验证 364 425 / 测试 364 426；", "review report (semicolon form)"),
    (ROOT / "scripts" / "append_review_round_v19.py", "训练 1 700 651 / 验证 364 426 / 测试 364 426；",
     "训练 1 700 652 / 验证 364 425 / 测试 364 426；", "review-round generator (semicolon form)"),
]

problems = []
for path, old, new, label in TARGETS:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        # already corrected, or never present
        print(f"  [{label}] anchor absent (already correct)")
        continue
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  [{label}] {old} -> {new}")

# The audit that found this must not re-report rounding artefacts as leakage.
audit = ROOT / "scripts" / "audit_full_corpus_data_v1.py"
text = audit.read_text(encoding="utf-8")
old_fp = ('def fingerprint(frame: pd.DataFrame) -> pd.Series:\n'
          '    return pd.util.hash_pandas_object(frame[features].round(6), index=False)')
new_fp = ('def fingerprint(frame: pd.DataFrame) -> pd.Series:\n'
          '    # Hash the exact float64 bits: rounding first merges rows that differ\n'
          '    # beyond the rounding step and reported 735 phantom train/test overlaps.\n'
          '    return pd.util.hash_pandas_object(frame[features], index=False)')
if old_fp in text:
    audit.write_text(text.replace(old_fp, new_fp, 1), encoding="utf-8")
    print("  [audit] fingerprint switched to exact hashing")

print("SPLIT_COUNTS_CORRECTED")
