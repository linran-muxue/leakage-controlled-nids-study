"""Guard the released metadata documents and the shape of the repository.

Two failure modes are checked, both of which had already happened:

* Scratch and third-party material was tracked in the public repository (37
  files: scraped journal pages, the full text of three unrelated papers and run
  logs). ``quarantine_unrelated_material_v1.py`` moved them out; this check
  fails if any of them is tracked again.
* README, MODEL_CARD and DATA_CARD described three datasets, the superseded
  manuscript layout and one population, while the paper had moved to four
  datasets, a new manuscript directory and four populations. ``fix_release_docs_v1.py``
  corrected them; this check fails if the facts disappear again.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "superseded" / "unrelated_material_manifest_v1.json"
FORBIDDEN_SUFFIXES = (".html",)
FORBIDDEN_NAMES = {
    "parse_output.txt", "print_rows.py", "extract_papers.py", "fetch_csa.py",
    "parse_csa.py", "post_search.py", "make_word_scaffold.py",
}
problems: list[str] = []


def track() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    return set(out.splitlines())


def main() -> int:
    tracked = track()
    offenders = []
    for name in sorted(tracked):
        if "/" in name:
            continue
        if name in FORBIDDEN_NAMES or name.endswith(FORBIDDEN_SUFFIXES) \
                or (name.startswith("paper") and name.endswith(".txt")) \
                or (name.startswith("results_") and name.endswith(".log")):
            offenders.append(name)
    if offenders:
        problems.append(f"unrelated material is tracked again: {offenders}")

    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".quarantine/" not in ignore:
        problems.append(".gitignore does not exclude .quarantine/")

    if not MANIFEST.exists():
        problems.append(f"missing {MANIFEST.relative_to(ROOT)}")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        quarantined = [row["file"] for row in manifest["files"]]
        if len(quarantined) != manifest["count"] or len(quarantined) < 30:
            problems.append(f"manifest covers {len(quarantined)} files, expected {manifest['count']}")
        still_tracked = [name for name in quarantined if name in tracked]
        if still_tracked:
            problems.append(f"quarantined files are tracked again: {still_tracked}")
        for row in manifest["files"]:
            target = ROOT / row["quarantined_to"]
            if not target.exists():
                problems.append(f"{row['file']} was moved but is not in the quarantine folder")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    model = (ROOT / "MODEL_CARD.md").read_text(encoding="utf-8")
    data = (ROOT / "DATA_CARD.md").read_text(encoding="utf-8")

    required = [
        ("README names all four datasets in its scope statement", readme,
         "CIC-IDS2017, NSL-KDD, UNSW-NB15 or N-BaIoT files"),
        ("README points at the current manuscript", readme, "重构版论文_v4_20260915"),
        ("README names the 413,209-flow population", readme, "413,209"),
        ("README names the full corpus", readme, "2,429,503"),
        ("README marks the old layout as superseded", readme, "superseded manuscripts"),
        ("MODEL_CARD counts four datasets", model, "four public research datasets"),
        ("MODEL_CARD names N-BaIoT", model, "N-BaIoT"),
        ("MODEL_CARD attributes 4.6 to batch throughput", model,
         "whole-batch throughput is 4.6 times lower"),
        ("DATA_CARD lists the N-BaIoT row", data, "| N-BaIoT |"),
        ("DATA_CARD lists the 200,000-per-class population", data, "413,209"),
        ("DATA_CARD lists the uncapped corpus", data, "2,429,503"),
        ("DATA_CARD records the N-BaIoT benchmark", data, "180,000"),
    ]
    for label, text, needle in required:
        if needle not in text:
            problems.append(f"{label}: {needle!r} not found")
    if "4.6 times slower per row" in model:
        problems.append("MODEL_CARD still conflates batch throughput with per-row latency")
    if "three public research datasets" in model or "three public research datasets" in data:
        problems.append("a card still says three public research datasets")

    print(f"tracked files: {len(tracked)} | quarantined: "
          f"{json.loads(MANIFEST.read_text(encoding='utf-8'))['count'] if MANIFEST.exists() else 0}")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("RELEASE_HYGIENE_FAILED")
        return 1
    print("RELEASE_HYGIENE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
