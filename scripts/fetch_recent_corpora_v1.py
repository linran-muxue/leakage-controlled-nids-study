"""Fetch modern (2020-2023) intrusion-detection corpora from their public mirrors.

  RT-IoT2022              2022  52 MB   one CSV
  ACI-IoT-2023            2023  446 MB  tar.gz of processed tables
  LITNET-2020 (S0.001)    2020  11 MB   train/test CSVs
  IoT-23 preprocessed     2020  11 MB   parquet

Each file is verified against the size the Hub reports, then hashed into a
manifest.  Destination: E:\\论文\\data\\external\\recent.
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
ROOT = Path(r"E:\论文\data\external\recent")
TARGETS = {
    "RT-IoT2022": ("michaelmallari/rt-iot2022", ["rt-iot2022.csv"]),
    "ACI-IoT-2023": ("knhn1004/aci-iot-2023-processed", ["datasets.tar.gz"]),
    "LITNET-2020-S0.001": ("sukengine/LITNET2020-S0.001",
                           ["train_data_0.001.csv", "test_data_0.001.csv"]),
    "IoT-23": ("19kmunz/iot-23-preprocessed",
               ["data/train-00000-of-00001-ad1ef30cd88c8d29.parquet"]),
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
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                timeout=300, context=CTX) as response, \
            target.open("ab" if existing else "wb") as handle:
        while chunk := response.read(1 << 22):
            handle.write(chunk)
    if target.stat().st_size != expected:
        raise SystemExit(f"size mismatch for {target.name}")


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    manifest = []
    for name, (repo, wanted) in TARGETS.items():
        entries = {entry["path"]: entry for entry in api(repo)
                   if entry.get("type") == "file"}
        for relative in wanted:
            entry = entries[relative]
            target = ROOT / name / Path(relative).name
            started = time.time()
            download(f"https://huggingface.co/datasets/{repo}/resolve/main/{relative}",
                     target, entry["size"])
            manifest.append({"dataset": name, "repo": repo, "path": relative,
                             "file": str(target), "bytes": target.stat().st_size,
                             "sha256": digest(target),
                             "seconds": round(time.time() - started, 1)})
            print(f"{name}: {Path(relative).name} "
                  f"({target.stat().st_size / 1e6:.1f} MB)", flush=True)
    out = ROOT / "recent_corpora_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"RECENT_FETCH_DONE files={len(manifest)} manifest={out}")


if __name__ == "__main__":
    main()
