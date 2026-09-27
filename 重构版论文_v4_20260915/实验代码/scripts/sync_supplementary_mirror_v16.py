"""Keep results_publication_final/supplementary a mirror of the canonical bundle.
That directory still held the superseded S1-S15 set (old numbering, old file
names) while the manuscripts list S01-S26. Anyone who downloaded the results
directory therefore saw a different supplementary package from the one the
paper describes. Default mode syncs the mirror; --check only verifies it.
"""
from __future__ import annotations
import argparse
import hashlib
import shutil
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from supplementary_paths_v1 import supplementary_bundle
ROOT = Path(__file__).resolve().parents[1]
SOURCE = supplementary_bundle(ROOT / "重构版论文_v4_20260915")
TARGET = ROOT / "results_publication_final" / "supplementary"
def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def inventory(base: Path) -> dict[str, str]:
    return {str(p.relative_to(base)).replace("\\", "/"): digest(p)
            for p in base.rglob("*") if p.is_file()}
def guard() -> None:
    resolved = TARGET.resolve()
    if not str(resolved).startswith(str(ROOT.resolve())):
        raise SystemExit(f"refusing to touch {resolved}: outside the repository")
    if TARGET.name != "supplementary" or TARGET.parent.name != "results_publication_final":
        raise SystemExit(f"refusing to touch {resolved}: unexpected target")
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify only")
    args = parser.parse_args()
    guard()
    source = inventory(SOURCE)
    if args.check:
        if not TARGET.exists():
            print("ISSUE supplementary mirror is missing")
            print("SUPPLEMENTARY_MIRROR_MISMATCH")
            return 1
        target = inventory(TARGET)
        stale = sorted(set(target) - set(source))
        missing = sorted(set(source) - set(target))
        changed = sorted(k for k in source if k in target and source[k] != target[k])
        print(f"canonical files: {len(source)} | mirror files: {len(target)}")
        for label, items in (("stale", stale), ("missing", missing), ("changed", changed)):
            if items:
                print(f"  {label}: {items[:6]}{' ...' if len(items) > 6 else ''}")
        if stale or missing or changed:
            print("SUPPLEMENTARY_MIRROR_MISMATCH")
            return 1
        print("SUPPLEMENTARY_MIRROR_OK")
        return 0
    for path in sorted(TARGET.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    for path in sorted(SOURCE.rglob("*")):
        rel = path.relative_to(SOURCE)
        if path.is_dir():
            (TARGET / rel).mkdir(parents=True, exist_ok=True)
        else:
            destination = TARGET / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    print(f"SUPPLEMENTARY_MIRROR_SYNCED files={len(inventory(TARGET))}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
