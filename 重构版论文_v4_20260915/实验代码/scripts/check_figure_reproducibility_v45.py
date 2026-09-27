"""Verify that the committed figures are exactly what the builders produce.
Regenerates into place, compares bytes, and restores the originals if anything
differs, so the check never leaves the worktree modified.
"""
from __future__ import annotations
import hashlib
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
BUILDERS = [
    ("scripts/build_figures_en_v5.py", BASE / "figures_en"),
    ("scripts/build_restructured_figures_v4.py", BASE / "figures"),
    ("scripts/build_graphical_abstract_v5.py", BASE),
]
def snapshot(folder: Path, pattern: str = "*.png") -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(folder.glob(pattern))}
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]
def declared_outputs(script: Path) -> set[str]:
    """File names a builder writes, so a frozen figure cannot hide.

    figures/fig6_margin_bound.png and figures/fig7_diversity_dose_response.png
    were 2026-09-15 copies that no builder produced; the byte comparison above
    cannot see that, because it only compares files that already exist.
    """
    return set(re.findall(r'"([^"\n]+\.(?:png|pdf))"', script.read_text(encoding="utf-8")))
def main() -> int:
    problems: list[str] = []
    for script, folder in BUILDERS:
        patterns = ("*.png", "*.pdf")
        before = {pattern: snapshot(folder, pattern) for pattern in patterns}
        proc = subprocess.run([PY, script], capture_output=True, text=True, cwd=ROOT, timeout=900,
                              encoding="utf-8", errors="replace")
        after = {pattern: snapshot(folder, pattern) for pattern in patterns}
        declared = declared_outputs(ROOT / script)
        orphans = sorted(name for name in set(before["*.png"]) | set(before["*.pdf"])
                         if name not in declared)
        restored = False
        changed, missing, new = [], [], []
        for pattern in patterns:
            for name, data in before[pattern].items():
                if name not in after[pattern]:
                    missing.append(name)
                elif after[pattern][name] != data:
                    # PDFs embed a creation timestamp, so only PNGs are compared
                    if pattern == "*.png":
                        changed.append(name)
                    (folder / name).write_bytes(data)
                    restored = True
            new.extend(n for n in after[pattern] if n not in before[pattern])
        status = "identical" if not (changed or missing or new) else "DIFFERS"
        total = sum(len(files) for files in before.values())
        print(f"  {script}: {total} output(s) {status}"
              + (f" (changed {changed}, missing {missing}, new {new})" if status == "DIFFERS" else ""))
        if restored:
            print("     originals restored; worktree unchanged")
        print(f"     builder declares {len(declared)} output(s)"
              + (f"; not produced by it: {orphans}" if orphans else ""))
        if proc.returncode != 0:
            problems.append(f"{script} exited {proc.returncode}: {proc.stderr.strip()[:120]}")
        if changed or missing or new:
            problems.append(f"{script} output is not what is committed: {changed + missing + new}")
        if orphans:
            problems.append(f"{script} does not write {orphans}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("FIGURE_REPRODUCIBILITY_FAILED")
        return 1
    print("FIGURES_REPRODUCIBLE")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
