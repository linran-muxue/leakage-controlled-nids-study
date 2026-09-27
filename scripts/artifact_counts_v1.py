"""Counts the deliverables quote about the repository itself.

Four numbers are stated in more than one document and every one of them drifts
the moment the artefact it describes changes: the gate grows a check, the
archive gains a file, a figure or a main table is added.  Each was hand-typed in
several places and had already diverged (the gate ran 48 checks while the work
log said 45, the data-source table said 47 and the briefing script said 46), so
they are measured here instead and the documents that quote them are generated
from this module.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def gate_checks() -> int:
    """How many checks the verification gate runs.

    Same definition the deliverable-count checker uses, so a document that
    quotes this number cannot disagree with the gate it names.
    """
    text = (ROOT / "scripts" / "verify_all_v8.py").read_text(encoding="utf-8")
    return len(re.findall(r'^\s{4}\("', text, flags=re.M))


def bundle_files() -> int:
    """The files the next archive build stages, excluding its README and checksum list."""
    path = ROOT / "scripts" / "package_submission_bundle_v18.py"
    spec = importlib.util.spec_from_file_location("package_submission_bundle_v18", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [p for _, _, files in module.LAYOUT for p in files if not p.exists()]
    if missing:
        raise SystemExit("the bundle layout refers to missing artefacts: "
                         + ", ".join(str(p) for p in missing))
    return sum(len(files) for _, _, files in module.LAYOUT)


def figures() -> int:
    return len(list((BASE / "figures_en").glob("*.png")))


def tables() -> int:
    english = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    return len(re.findall(r"^\*\*Table \d+", english, flags=re.M))


def latest_tag() -> str:
    import subprocess
    tags = subprocess.run(["git", "tag"], capture_output=True, text=True,
                          cwd=ROOT).stdout.split()
    if not tags:
        raise SystemExit("the repository carries no release tag")
    return sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1]


if __name__ == "__main__":
    print(f"gate_checks={gate_checks()} bundle_files={bundle_files()} "
          f"figures={figures()} tables={tables()} tag={latest_tag()}")
