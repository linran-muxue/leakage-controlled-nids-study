"""Download the two additional corpora from their public Hugging Face mirrors.

  * CIC-IDS2018 official CSVs (12 files, 6.4 GB) from c01dsnap/CIC-IDS2018
  * CIC-IoT-2023 ML tables (parquet, 2.0 GB) from lacg030175/CIC-IoT-2023-full

Every file is verified against the size the Hub reports, resumed with HTTP Range
if a partial file exists, and recorded in a manifest with its SHA-256.  The
destination is E:\\论文\\data\\external so the repository stays untouched.
"""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"E:\论文\data\external")
TARGETS = {
    "CIC-IDS2018": ("c01dsnap/CIC-IDS2018", ["main"]),
    "CIC-IoT-2023": ("lacg030175/CIC-IoT-2023-full",
                     ["random", "random_3way"]),
}
CTX = ssl.create_default_context()


def api(repo: str) -> list[dict]:
    url = f"https://huggingface.co/api/datasets/{repo}/tree/main?recursive=true"
    with urllib.request.urlopen(url, timeout=60) as handle:
        return json.loads(handle.read().decode("utf-8"))


def download(url: str, target: Path, expected: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.stat().st_size if target.exists() else 0
    if existing == expected:
        return
    headers = {"User-Agent": "rccf-repro/1.0"}
    if existing:
        headers["Range"] = f"bytes={existing}-"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=300, context=CTX) as response, \
            target.open("ab" if existing else "wb") as handle:
        while True:
            chunk = response.read(1 << 22)
            if not chunk:
                break
            handle.write(chunk)
    if target.stat().st_size != expected:
        raise SystemExit(f"size mismatch for {target.name}: "
                         f"{target.stat().st_size} != {expected}")


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    manifest: list[dict] = []
    for name, (repo, prefixes) in TARGETS.items():
        destination = ROOT / name / "hf"
        entries = [entry for entry in api(repo)
                   if entry.get("type") == "file"
                   and any(entry["path"].startswith(prefix + "/") or "/" not in entry["path"]
                           for prefix in prefixes)
                   and entry["path"].endswith((".csv", ".parquet"))]
        total = sum(entry.get("size", 0) for entry in entries)
        print(f"== {name}: {len(entries)} files, {total / 1e9:.2f} GB -> {destination}",
              flush=True)
        for index, entry in enumerate(sorted(entries, key=lambda e: e["path"]), 1):
            # keep the Hub's sub-directory so identically named splits from
            # different folders cannot overwrite one another
            relative = entry["path"]
            target = destination / relative
            url = (f"https://huggingface.co/datasets/{repo}/resolve/main/"
                   f"{entry['path']}")
            started = time.time()
            download(url, target, entry["size"])
            manifest.append({
                "dataset": name, "repo": repo, "path": entry["path"],
                "file": relative, "bytes": target.stat().st_size,
                "sha256": digest(target),
                "seconds": round(time.time() - started, 1),
            })
            print(f"  [{index}/{len(entries)}] {relative} "
                  f"({target.stat().st_size / 1e6:.1f} MB)", flush=True)
    out = ROOT / "new_corpora_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FETCH_DONE files={len(manifest)} manifest={out}")


if __name__ == "__main__":
    main()
