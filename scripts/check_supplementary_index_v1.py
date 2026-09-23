"""Verify the supplementary index, the bundle it describes and the mirror.

S27, S28 and S29 each listed two sources with the same file name; the second
copy overwrote the first, so the bundle shipped one file less than the index
promised and checksums.sha256 carried two different hashes for one path. This
check recomputes the expected file names from the assembler's ITEMS table and
fails whenever the index, the bundle, the checksums or the mirror disagree.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from assemble_supplementary_v5 import ITEMS, target_names  # noqa: E402
from supplementary_paths_v1 import supplementary_bundle  # noqa: E402

BUNDLE = supplementary_bundle(ROOT / "重构版论文_v4_20260915")
MIRROR = ROOT / "results_publication_final" / "supplementary"
problems: list[str] = []


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if not BUNDLE.exists():
        print(f"ISSUE bundle missing: {BUNDLE}")
        print("SUPPLEMENTARY_INDEX_FAILED")
        return 1
    readme = (BUNDLE / "README.md").read_text(encoding="utf-8")
    checksums: dict[str, str] = {}
    for line in (BUNDLE / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        if rel in checksums:
            problems.append(f"checksums.sha256 lists {rel} twice")
        checksums[rel] = digest

    expected: set[str] = set()
    for key, (title, sources) in ITEMS.items():
        names = target_names(sources)
        if len(set(names)) != len(names):
            problems.append(f"{key}: the index still collides: {names}")
        for src, name in zip(sources, names):
            rel = f"{key}/{name}"
            expected.add(rel)
            if not (BUNDLE / key / name).is_file():
                problems.append(f"{rel}: missing from the bundle")
            if not (MIRROR / key / name).is_file():
                problems.append(f"{rel}: missing from the mirror")
            if rel not in checksums:
                problems.append(f"{rel}: missing from checksums.sha256")
            elif checksums[rel] != sha256(BUNDLE / key / name):
                problems.append(f"{rel}: checksum does not match the shipped file")
        row = next((line for line in readme.splitlines() if line.startswith(f"| {key} |")), "")
        listed = [piece.strip() for piece in row.split("|")[3].split(";") if piece.strip()]
        if listed != names:
            problems.append(f"{key}: README lists {listed}, expected {names}")

    for path in BUNDLE.rglob("*"):
        if path.is_file() and path.name not in ("README.md", "checksums.sha256"):
            rel = str(path.relative_to(BUNDLE)).replace("\\", "/")
            if rel not in expected:
                problems.append(f"{rel}: shipped but not listed in the index")

    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SUPPLEMENTARY_INDEX_FAILED")
        return 1
    print(f"supplementary index OK: {len(ITEMS)} sections, {len(expected)} files, "
          f"checksums and mirror agree")
    print("SUPPLEMENTARY_INDEX_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
