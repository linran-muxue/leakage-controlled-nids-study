"""Move every current-state release citation from one tag to the next.

The gate ``verify_all_v8.py`` requires the manuscripts, the auxiliary front
matter, ``README.md``, ``CITATION.cff`` and ``MANIFEST.json`` to cite exactly the
latest git tag.  The last two rounds bumped the tag by hand and missed files,
which is why this script exists: it lists the locations that describe the
*current* release and rewrites only those.

Historical records are deliberately excluded.  Rows such as
``发布标签已推进到 v1.10.0`` inside the self-check table and the review report
describe past rounds and must keep their original wording; the script skips any
line containing a marker from ``SKIP_MARKERS``.

Default is a dry run; pass ``--apply`` to write.  The script is idempotent: once
the files carry the new tag the replacement counts drop to zero.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

# Lines carrying any of these markers record history and are never rewritten.
SKIP_MARKERS = ("已推进到", "标签已推进", "本轮为", "历史快照")


def rules(old: str, new: str) -> list[tuple[str, list[tuple[str, str]]]]:
    return [
        ("重构版论文_v4_20260915/English_SCI_Manuscript_v4.md",
         [(f"release {old}, tag {old}", f"release {new}, tag {new}")]),
        ("重构版论文_v4_20260915/中文SCI论文_v4_重构版.md",
         [(f"发布版本 {old}，标签 {old}", f"发布版本 {new}，标签 {new}")]),
        ("重构版论文_v4_20260915/Cover_Letter_JISA_v4.md",
         [(f"release {old}, tag {old}", f"release {new}, tag {new}")]),
        ("重构版论文_v4_20260915/论文自查表.md",
         [(f"`{old}`", f"`{new}`")]),
        ("重构版论文_v4_20260915/论文结构诊断与重构方案.md",
         [(f"正式稿件，{old}。", f"正式稿件，{new}。")]),
        ("重构版论文_v4_20260915/P0_P1执行手册.md",
         [(f"正式稿件，{old}。", f"正式稿件，{new}。")]),
        ("重构版论文_v4_20260915/研究缺口审计与优先级清单.md",
         [(f"正式稿件，{old}。", f"正式稿件，{new}。")]),
        ("README.md",
         [(f"Submission release: `{old}`", f"Submission release: `{new}`"),
          (f"(release `{old}`)", f"(release `{new}`)")]),
        ("scripts/check_docx_freshness_v17.py",
         [(f'"{old}"', f'"{new}"')]),
        ("scripts/package_submission_bundle_v18.py",
         [(f'TAG = "{old}"', f'TAG = "{new}"')]),
        ("scripts/update_public_metadata_v15.py",
         [(f'TAG = "{old}"', f'TAG = "{new}"')]),
        ("scripts/update_availability_statement_v5.py",
         [(f'TARGET = "{old}"', f'TARGET = "{new}"')]),
        ("scripts/align_aux_documents_v13.py",
         [(f'TAG = "{old}"', f'TAG = "{new}"')]),
        ("scripts/refresh_selfcheck_facts_v11.py",
         [(f'TAG = "{old}"', f'TAG = "{new}"')]),
        ("scripts/stamp_aux_status_v14.py",
         [(f"正式稿件，{old}。", f"正式稿件，{new}。")]),
    ]


def rewrite(path: Path, pairs: list[tuple[str, str]], apply: bool) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = 0
    for index, line in enumerate(lines):
        if any(marker in line for marker in SKIP_MARKERS):
            continue
        updated = line
        for old, new in pairs:
            if old in updated:
                changed += updated.count(old)
                updated = updated.replace(old, new)
        lines[index] = updated
    if changed and apply:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="old", default="v1.10.0")
    parser.add_argument("--to", dest="new", default="v1.11.0")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.old == args.new:
        raise SystemExit("--from and --to are identical")
    total = 0
    missing = []
    for relative, pairs in rules(args.old, args.new):
        path = ROOT / relative
        if not path.exists():
            missing.append(relative)
            continue
        count = rewrite(path, pairs, args.apply)
        total += count
        print(f"  {relative}: {count} replacement(s)")
    if missing:
        print("missing files:", missing)
    mode = "APPLIED" if args.apply else "DRY_RUN"
    print(f"RELEASE_TAG_BUMP={mode} total={total} {args.old} -> {args.new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
