"""Fetch the Gotham Dataset 2025 archive over parallel ranged connections.

The archive is 22.2 GiB and Zenodo serves this host roughly 150 kB/s per
connection, so one stream would need about two days.  The file is therefore
pulled over a pool of ranged connections into one pre-allocated file: blocks are
32 MiB, a worker claims the next unfinished block, downloads it with a range
request and writes it at the block offset.  Finished blocks are recorded in a
sidecar state file, so an interrupted run resumes instead of restarting, and the
MD5 published by Zenodo is verified before the manifest is written.

Proxy settings are taken from the environment/registry by urllib, exactly as the
other fetch scripts in this directory do it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def record_metadata(record: str) -> tuple[str, int, str]:
    """Return (download url, byte size, md5) for a Zenodo record."""
    with urllib.request.urlopen(f"https://zenodo.org/api/records/{record}",
                                timeout=120) as handle:
        data = json.loads(handle.read().decode("utf-8"))
    entry = data["files"][0]
    url = entry["links"]["self"] + "?download=1"
    checksum = entry.get("checksum", "")
    md5 = checksum.split(":", 1)[1] if checksum.startswith("md5:") else ""
    return url, int(entry["size"]), md5


def fetch_range(url: str, offset: int, length: int, attempts: int = 6) -> bytes:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url, headers={"Range": f"bytes={offset}-{offset + length - 1}",
                              "User-Agent": "rccf-repro/1.0"})
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
            if len(payload) != length:
                raise IOError(f"short read: {len(payload)} of {length}")
            return payload
        except Exception as exc:  # noqa: BLE001 - retried, then reported
            last = exc
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"block at {offset} failed after {attempts} attempts: {last}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", default="14502760")
    ap.add_argument("--target", type=Path,
                    default=Path(r"E:\论文\data\external\y2025\Gotham2025"
                                 r"\GothamDataset2025.zip"))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--block-mb", type=int, default=32)
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args()

    url, total, expected_md5 = record_metadata(args.record)
    target = args.target
    target.parent.mkdir(parents=True, exist_ok=True)
    state_path = target.with_suffix(target.suffix + ".state.json")
    block = args.block_mb * 1024 * 1024
    count = (total + block - 1) // block
    failed: list[int] = []
    print(f"{target.name}: {total / 1e9:.2f} GB in {count} blocks of "
          f"{args.block_mb} MiB over {args.workers} connections", flush=True)

    if target.exists() and target.stat().st_size != total:
        target.unlink()
    with target.open("ab"):
        pass
    with target.open("r+b") as handle:
        handle.truncate(total)

    done: set[int] = set()
    if state_path.exists():
        done = set(json.loads(state_path.read_text(encoding="utf-8"))["done"])
        print(f"resuming: {len(done)} of {count} blocks already present", flush=True)

    lock = threading.Lock()
    next_index = [0]
    completed = [len(done)]
    started = time.time()

    def claim() -> int | None:
        with lock:
            while next_index[0] < count:
                index = next_index[0]
                next_index[0] += 1
                if index not in done:
                    return index
        return None

    def worker(handle) -> None:
        while True:
            index = claim()
            if index is None:
                return
            offset = index * block
            length = min(block, total - offset)
            try:
                payload = fetch_range(url, offset, length)
            except Exception as exc:  # noqa: BLE001 - one bad block must not end the run
                # A transient network error used to abort the whole 23 GB run and
                # throw away the in-flight work; the block is now recorded and
                # retried in a later pass instead.
                with lock:
                    failed.append(index)
                    print(f"block {index} failed: {exc}", flush=True)
                continue
            with lock:
                handle.seek(offset)
                handle.write(payload)
                done.add(index)
                completed[0] += 1
                if completed[0] % 4 == 0 or completed[0] == count:
                    state_path.write_text(
                        json.dumps({"total": total, "done": sorted(done)}),
                        encoding="utf-8")
                    elapsed = time.time() - started
                    rate = completed[0] * block / max(elapsed, 1)
                    remaining = (count - completed[0]) * block / max(rate, 1)
                    print(f"{completed[0]}/{count} blocks "
                          f"({completed[0] * block / total * 100:.1f}%), "
                          f"{rate / 1e6:.2f} MB/s, ~{remaining / 60:.0f} min left",
                          flush=True)

    for attempt in range(1, 7):
        failed.clear()
        with target.open("r+b") as handle:
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                list(pool.map(lambda _: worker(handle), range(args.workers)))
            handle.flush()
        state_path.write_text(json.dumps({"total": total, "done": sorted(done)}),
                              encoding="utf-8")
        if len(done) == count:
            break
        print(f"pass {attempt}: {len(done)}/{count} blocks done, {len(failed)} failed; "
              f"retrying", flush=True)
        next_index[0] = 0
        time.sleep(min(15 * attempt, 60))

    state_path.write_text(json.dumps({"total": total, "done": sorted(done)}),
                          encoding="utf-8")
    if target.stat().st_size != total or len(done) != count:
        raise SystemExit(f"incomplete: {len(done)}/{count} blocks, "
                         f"{target.stat().st_size} of {total} bytes")

    print("verifying MD5", flush=True)
    digest = hashlib.md5()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if expected_md5 and actual != expected_md5:
        raise SystemExit(f"MD5 mismatch: {actual} != {expected_md5}")
    manifest = args.manifest or target.parent / "gotham2025_manifest.json"
    manifest.write_text(json.dumps(
        [{"dataset": "GothamDataset2025", "file": str(target),
          "bytes": total, "md5": actual,
          "source": f"https://zenodo.org/records/{args.record}",
          "license": "CC BY 4.0", "retrieved": time.strftime("%Y-%m-%d")}],
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FETCH_GOTHAM_DONE bytes={total} md5={actual} manifest={manifest}")


if __name__ == "__main__":
    main()
