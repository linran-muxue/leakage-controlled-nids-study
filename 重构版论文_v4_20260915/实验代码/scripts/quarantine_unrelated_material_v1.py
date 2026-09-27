"""Untrack the scratch and third-party material that is not part of the paper.

The public repository declares what it contains (source code, configuration,
audit summaries, derived metrics, predictions, figures and supporting tables)
and states that it does not redistribute third-party material.  In fact it
still tracked 46 unrelated files: twenty-two saved journal, article and search
pages, the full text of three unrelated papers (Reflexion, ReAct, Toolformer)
plus their previews, seven scratch scripts or outputs, and eleven run logs.

This script moves them to ``.quarantine/unrelated_material/`` (gitignored,
nothing is deleted), removes them from the index, and records a manifest so the
action stays auditable.  ``check_release_hygiene_v1.py`` fails if any of them is
tracked again.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / ".quarantine" / "unrelated_material"
MANIFEST = ROOT / "superseded" / "unrelated_material_manifest_v1.json"

# name -> (reason, marker that must appear in the file, proving we handle the
# file we think we are handling)
ITEMS: dict[str, tuple[str, str]] = {
    "paper1_en.txt": ("full text of an unrelated third-party paper", "Reflexion"),
    "paper2_en.txt": ("full text of an unrelated third-party paper", "REACT"),
    "paper3_en.txt": ("full text of an unrelated third-party paper", "Toolformer"),
    "paper1_preview.txt": ("excerpt of an unrelated third-party paper", "Reflexion"),
    "paper2_preview.txt": ("excerpt of an unrelated third-party paper", "REACT"),
    "paper3_preview.txt": ("excerpt of an unrelated third-party paper", "Toolformer"),
    "article_8661.html": ("scraped article page", "html"),
    "article_10162.html": ("scraped article page", "html"),
    "article_20031125.html": ("scraped article page", "html"),
    "article9821.html": ("scraped article page", "html"),
    "csa_9702.html": ("scraped search page", "html"),
    "csa_10278.html": ("scraped search page", "html"),
    "csa_10310.html": ("scraped search page", "html"),
    "csa_20170605.html": ("scraped search page", "html"),
    "csa_intro_utf8.html": ("scraped search page", "html"),
    "j_applied-soft-computing.html": ("saved journal landing page", "html"),
    "j_computers-and-security.html": ("saved journal landing page", "html"),
    "j_expert-systems-with-applications.html": ("saved journal landing page", "html"),
    "j_journal-of-information-security-and-applications.html": ("saved journal landing page", "html"),
    "search_ids.html": ("scraped search page", "html"),
    "src_applied-soft-computing.html": ("saved journal landing page", "html"),
    "src_computers-and-security.html": ("saved journal landing page", "html"),
    "tmp_csa.html": ("scraped search page", "html"),
    "tmp_page_3844686675673330626.html": ("scraped journal page", "html"),
    "tmp_page_3860765524720389898.html": ("scraped journal page", "html"),
    "web_3647369443213981488.html": ("scraped journal page", "html"),
    "web_4861238045800853825.html": ("scraped journal page", "html"),
    "web_4893981334794878482.html": ("scraped journal page", "html"),
    "extract_papers.py": ("scratch scraping helper", "import"),
    "fetch_csa.py": ("scratch scraping helper", "import"),
    "parse_csa.py": ("scratch scraping helper", "import"),
    "post_search.py": ("scratch scraping helper", "import"),
    "make_word_scaffold.py": ("scratch document helper", "import"),
    "print_rows.py": ("scratch helper", "import"),
    "parse_output.txt": ("scratch output", ""),
}
for _seed in ("diversity_v5", "equivalence_10seeds_v5", "gate_tuning_v5", "mlp_final_v5",
              "mlp_long_v5", "mlp_v5", "resources_v5", "robustness_extended_v5",
              "robustness_extended_v5_seeds", "seeds10_v5", "tuned_gate_test_v5"):
    ITEMS[f"results_{_seed}.log"] = ("run log, not a released artifact", "")

IGNORE_BLOCK = """
# Scratch material and third-party documents that are unrelated to the paper.
# They are kept locally under .quarantine/ but must never be shipped in the
# public repository: the README states that it does not redistribute
# third-party material.
.quarantine/
article*.html
csa_*.html
j_*.html
paper[0-9]_*.txt
tmp_*.html
web_*.html
src_*.html
search_ids.html
parse_output.txt
print_rows.py
extract_papers.py
fetch_csa.py
parse_csa.py
post_search.py
make_word_scaffold.py
results_*.log
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    return set(out.splitlines())


def main() -> int:
    in_index = tracked()
    # Idempotent: a second pass only handles what is still in the tree, and the
    # manifest accumulates rather than replacing earlier entries.
    previous: dict[str, dict] = {}
    if MANIFEST.exists():
        previous = {row["file"]: row for row in
                    json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]}
    pending = {name: spec for name, spec in ITEMS.items() if (ROOT / name).exists()}
    unexpected = [name for name in ITEMS if not (ROOT / name).exists() and name not in previous]
    if unexpected:
        raise SystemExit(f"expected files are missing: {unexpected}")
    for name, (_, marker) in pending.items():
        if marker and marker.lower() not in (ROOT / name).read_text(
                encoding="utf-8", errors="replace").lower():
            raise SystemExit(f"{name} does not contain the expected marker {marker!r}")

    DEST.mkdir(parents=True, exist_ok=True)
    rows = [previous[name] for name in sorted(previous)]
    for name, (reason, _) in sorted(pending.items()):
        source = ROOT / name
        digest = sha256(source)
        target = DEST / name
        target.write_bytes(source.read_bytes())
        if sha256(target) != digest:
            raise SystemExit(f"copy verification failed for {name}")
        if name in in_index:
            subprocess.run(["git", "rm", "--cached", "--quiet", name], cwd=ROOT, check=True)
        source.unlink()
        rows.append({"file": name, "bytes": target.stat().st_size, "sha256": digest,
                     "reason": reason, "quarantined_to": str(target.relative_to(ROOT))})
        print(f"  quarantined {name:<62}{reason}")

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(
        {"note": "Files moved out of the release tree; kept locally under .quarantine/.",
         "count": len(rows), "files": rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".quarantine/" not in ignore:
        (ROOT / ".gitignore").write_text(ignore.rstrip() + "\n" + IGNORE_BLOCK,
                                        encoding="utf-8")

    # Point the provenance folder at the new manifest so the removal stays
    # discoverable from the place a reader would look for superseded material.
    note = ROOT / "superseded" / "README.md"
    text = note.read_text(encoding="utf-8")
    marker = "## Unrelated material removed from the release"
    reasons = [row["reason"] for row in rows]
    counts = {
        "pages": sum("page" in r for r in reasons),
        "papers": sum("third-party paper" in r for r in reasons),
        "scratch": sum(r.startswith("scratch") for r in reasons),
        "logs": sum("run log" in r for r in reasons),
    }
    if len(rows) != sum(counts.values()):
        raise SystemExit(f"manifest categories do not add up: {counts} vs {len(rows)}")
    paragraph = (
        f"The public repository also tracked {len(rows)} scratch files that are unrelated to\n"
        f"this study: {counts['pages']} saved journal, article and search pages, the full text of\n"
        f"three unrelated papers together with their previews ({counts['papers']} files),\n"
        f"{counts['scratch']} scratch scripts or outputs, and {counts['logs']} run logs. They no\n"
        "longer belong to the release, because the README states that the archive does not\n"
        "redistribute third-party material. The files were moved to the gitignored\n"
        "`.quarantine/unrelated_material/` folder and are listed, with sizes and SHA-256\n"
        "digests, in `unrelated_material_manifest_v1.json`.\n"
        "`scripts/check_release_hygiene_v1.py` fails if any of them is tracked again.\n")
    head = text.split(marker)[0].rstrip() if marker in text else text.rstrip()
    note.write_text(head + "\n\n" + marker + "\n\n" + paragraph, encoding="utf-8")
    print(f"documented the removal in {note.name}: {counts}")
    total = sum(row["bytes"] for row in rows)
    print()
    print(f"QUARANTINED {len(rows)} file(s), {total / 1048576:.1f} MB, manifest {MANIFEST.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
