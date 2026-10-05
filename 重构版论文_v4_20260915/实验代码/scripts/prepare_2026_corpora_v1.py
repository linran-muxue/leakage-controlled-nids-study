"""Prepare the three 2026 corpora under the study's reservoir protocol.

  ctu      CTU-IDSEVAL-6      Zeek connection logs, labels Benign/Malicious/Background
  6tisch   6TiSCHSet-2026     6TiSCH telemetry, 8 classes (NONE + 7 attack families)
  rtn      RTN traffic        packet-level CSV, benign vs attack

Each source states which columns are identifiers; those are excluded before any
model sees the data, and the exclusions are recorded in the audit.  6TiSCHSet
ships its own leakage-aware feature list (15 raw + 2 derived, three identifiers
excluded) and this script follows it exactly.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"E:\论文\data\external\y2026")

CTU_FEATURES = ["duration", "orig_bytes", "resp_bytes", "missed_bytes", "orig_pkts",
                "orig_ip_bytes", "resp_pkts", "resp_ip_bytes", "id.orig_p", "id.resp_p",
                "ip_proto"]
CTU_DROP = ["ts", "uid", "id.orig_h", "id.resp_h", "proto", "service", "conn_state",
            "local_orig", "local_resp", "history", "tunnel_parents",
            "detailedlabel", "label"]

TISCH_DROP = ["timestamp", "node_id", "parent_id", "is_attacker", "attack_type"]
TISCH_NAMES = {0: "NONE", 1: "Blackhole", 2: "Decreased Rank", 3: "DIS Flooding",
               4: "App Flooding", 5: "Shared Cell", 6: "6P Exhaustion",
               7: "TSCH Desync"}

RTN_DROP = ["frame.number", "frame.time_epoch", "frame.protocols", "ip.src", "ip.dst",
            "dns.qry.name", "http.request.method", "http.request.uri", "label"]
RTN_HEX = ["ip.checksum", "tcp.checksum", "udp.checksum"]


def say(message: str) -> None:
    print(message, flush=True)


class Reservoir:
    """Same rule as the other extension corpora: fingerprint dedup plus per-class caps."""

    def __init__(self, train_cap: int, test_cap: int, test_fraction: float) -> None:
        self.train_cap, self.test_cap = train_cap, test_cap
        self.cut = int(round(test_fraction * 100))
        self.seen: dict[str, dict[str, set]] = {"train": {}, "test": {}}
        self.kept: dict[str, list] = {"train": [], "test": []}
        self.labels: dict[str, list] = {"train": [], "test": []}
        self.totals: dict[str, int] = {}
        self.duplicates = {"train": 0, "test": 0}
        self.features: list[str] | None = None
        self.dropped: list[str] = []
        self.rows = 0

    def add(self, numeric: pd.DataFrame, labels: pd.Series) -> None:
        numeric = numeric.copy()
        if self.features is None:
            self.dropped = [column for column in numeric.columns
                            if numeric[column].isna().all()]
            self.features = [column for column in numeric.columns
                             if column not in self.dropped]
        numeric = numeric.reindex(columns=self.features).astype("float32")
        present = np.isfinite(numeric.to_numpy(dtype=float)).sum(axis=1) > 0
        numeric = numeric.fillna(0.0)
        self.rows += len(numeric)
        fingerprint = pd.util.hash_pandas_object(numeric, index=False).to_numpy(dtype=np.uint64)
        label_values = labels.to_numpy()
        for position in np.flatnonzero(present):
            label = str(label_values[position])
            self.totals[label] = self.totals.get(label, 0) + 1
            split = "test" if int(fingerprint[position]) % 100 < self.cut else "train"
            cap = self.test_cap if split == "test" else self.train_cap
            bucket = self.seen[split].setdefault(label, set())
            if len(bucket) >= cap:
                continue
            key = int(fingerprint[position])
            if key in bucket:
                self.duplicates[split] += 1
                continue
            bucket.add(key)
            self.kept[split].append(numeric.iloc[position].to_numpy(dtype=np.float32))
            self.labels[split].append(label)

    def audit(self, extra: dict) -> dict:
        return {"rows_scanned": self.rows, "per_class_total": self.totals,
                "per_class_kept_train": {k: len(v) for k, v in self.seen["train"].items()},
                "per_class_kept_test": {k: len(v) for k, v in self.seen["test"].items()},
                "duplicates_in_reservoir": self.duplicates,
                "dropped_all_nan_columns": self.dropped, "features": self.features,
                "split_rule": f"fingerprint % 100 < {self.cut} -> test",
                "caps": {"train": self.train_cap, "test": self.test_cap}, **extra}


def ctu(reservoir: Reservoir) -> None:
    path = DATA / "CTU-IDSEVAL-6" / "zeek.zip"
    with zipfile.ZipFile(path) as archive:
        names = sorted(n for n in archive.namelist()
                       if n.startswith("zeek/") and n.endswith(".log"))
        say(f"CTU-IDSEVAL-6: {len(names)} flow files")
        for name in names:
            with archive.open(name) as handle:
                raw = handle.read().decode("utf-8", "replace").splitlines()
            # Zeek writes the column names in a "#fields" comment, so they have to
            # be lifted out by hand; letting pandas infer them would make the
            # first flow the header.
            fields = None
            data = []
            for line in raw:
                if line.startswith("#fields"):
                    fields = line.split("\t")[1:]
                elif not line.startswith("#") and line.strip():
                    data.append(line.split("\t"))
            if not fields or not data:
                continue
            frame = pd.DataFrame(data, columns=fields)
            frame = frame.replace("-", np.nan)
            for column in CTU_FEATURES:
                if column not in frame:
                    frame[column] = np.nan
            numeric = frame[CTU_FEATURES].apply(pd.to_numeric, errors="coerce")
            reservoir.add(numeric, frame["label"].astype(str))
            say(f"  {name.split('/')[-1]}: {len(frame):,} rows")


def tisch(reservoir: Reservoir) -> None:
    path = DATA / "6TiSCHSet-2026" / "6tisch-attack-dataset-v1.0.0.zip"
    with zipfile.ZipFile(path) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith(".csv")
                       and ("/data/single/" in n or "/data/multiattack/" in n))
        say(f"6TiSCHSet-2026: {len(names)} telemetry runs (single + multiattack)")
        for name in names:
            with archive.open(name) as handle:
                frame = pd.read_csv(io.TextIOWrapper(handle, encoding="utf-8",
                                                     errors="replace"))
            frame = frame.sort_values(["node_id", "timestamp"], kind="stable")
            parent_rank = frame.set_index(["node_id", "timestamp"])["rank"]
            parents = frame["parent_id"].to_numpy()
            ranks = frame["rank"].to_numpy()
            # rank of the preferred parent, taken from that node's own latest record
            latest = frame.groupby("node_id")["rank"].last().to_dict()
            frame["rank_increase"] = ranks - np.array(
                [latest.get(int(p), np.nan) if p else np.nan for p in parents])
            frame["d_app"] = frame.groupby("node_id")["app_packet_count"].diff().fillna(0.0)
            del parent_rank, latest
            label = frame["attack_type"].astype(int).map(
                lambda value: TISCH_NAMES.get(value, f"Attack {value}"))
            numeric = frame.drop(columns=TISCH_DROP, errors="ignore").apply(
                pd.to_numeric, errors="coerce")
            reservoir.add(numeric, label)
            say(f"  {name.split('/')[-1]}: {len(frame):,} rows")


def rtn(reservoir: Reservoir) -> None:
    path = DATA / "RTN-traffic" / "RTN_traffic_dataset.csv"
    say("RTN traffic: streaming packet table")
    for chunk in pd.read_csv(path, chunksize=200_000, low_memory=False):
        for column in RTN_HEX:
            if column in chunk:
                chunk[column] = chunk[column].map(
                    lambda value: float(int(str(value), 16))
                    if isinstance(value, str) and str(value).strip().startswith("0x")
                    else np.nan)
        if "tcp.flags" in chunk:
            chunk["tcp.flags_count"] = chunk["tcp.flags"].map(
                lambda value: float(len(str(value).strip())) if isinstance(value, str) else np.nan)
        if "ip.flags" in chunk:
            chunk["ip.flags_count"] = chunk["ip.flags"].map(
                lambda value: float(len(str(value).strip())) if isinstance(value, str) else np.nan)
        label = chunk["label"].astype(str).map({"0": "Benign", "1": "Attack"})
        numeric = chunk.drop(columns=RTN_DROP, errors="ignore").apply(
            pd.to_numeric, errors="coerce")
        reservoir.add(numeric, label)


BUILDERS = {"ctu": ctu, "6tisch": tisch, "rtn": rtn}
DIRS = {"ctu": ("data_processed_ctu_idseval6_v1", "results_data_audit_ctu_idseval6_v1",
                "CTU-IDSEVAL-6"),
        "6tisch": ("data_processed_6tisch2026_v1", "results_data_audit_6tisch2026_v1",
                   "6TiSCHSet-2026"),
        "rtn": ("data_processed_rtn2026_v1", "results_data_audit_rtn2026_v1",
                "RTN-traffic-2026")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=sorted(BUILDERS), required=True)
    ap.add_argument("--train-cap", type=int, default=5000)
    ap.add_argument("--test-cap", type=int, default=2000)
    ap.add_argument("--min-class-rows", type=int, default=200)
    ap.add_argument("--test-fraction", type=float, default=0.30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--processed-dir", default=None,
                    help="override the output directory (used for the uncapped variant)")
    ap.add_argument("--audit-dir", default=None)
    args = ap.parse_args()

    processed, audit_dir, title = DIRS[args.dataset]
    if args.processed_dir:
        processed = args.processed_dir
    if args.audit_dir:
        audit_dir = args.audit_dir
    out = ROOT / processed
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / audit_dir).mkdir(parents=True, exist_ok=True)

    reservoir = Reservoir(args.train_cap, args.test_cap, args.test_fraction)
    BUILDERS[args.dataset](reservoir)
    X_train_all = np.vstack(reservoir.kept["train"])
    y_train_all = np.array(reservoir.labels["train"])
    X_test = np.vstack(reservoir.kept["test"])
    y_test = np.array(reservoir.labels["test"])
    say(f"reservoir: train {X_train_all.shape} test {X_test.shape}")

    counts = pd.Series(y_train_all).value_counts()
    small = [label for label, count in counts.items() if count < args.min_class_rows]
    if small:
        keep = ~np.isin(y_train_all, small)
        X_train_all, y_train_all = X_train_all[keep], y_train_all[keep]
        keep = ~np.isin(y_test, small)
        X_test, y_test = X_test[keep], y_test[keep]
        say(f"dropped classes with fewer than {args.min_class_rows} train rows: {small}")

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_all, y_train_all, test_size=0.15, stratify=y_train_all,
        random_state=args.seed)
    features = reservoir.features
    for name, values, target in (("train", X_train, y_train), ("validation", X_val, y_val),
                                 ("test", X_test, y_test)):
        frame = pd.DataFrame(values, columns=features)
        frame["target"] = target
        frame.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
        say(f"  wrote {name}: {frame.shape}")
    pd.Series(y_train_all).value_counts().rename_axis("target").reset_index(
        name="count").to_csv(out / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    config = {"dataset": title, "per_class_cap_train": args.train_cap,
              "per_class_cap_test": args.test_cap,
              "reservoir_rule": ("streamed rows admitted per class until the cap; exact "
                                 "128-bit fingerprint dedup inside the reservoir"),
              "seed": args.seed, "features": features,
              "source": "E:\\论文\\data\\external\\y2026"}
    (out / "preprocess_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = reservoir.audit({"splits": {"train": int(len(X_train)),
                                        "validation": int(len(X_val)),
                                        "test": int(len(X_test))},
                             "dropped_small_classes": {label: int(counts[label])
                                                       for label in small} or None})
    (ROOT / audit_dir / "data_processing_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    say(json.dumps(audit["splits"], ensure_ascii=False))
    say(f"PREPARED_{args.dataset.upper()}")


if __name__ == "__main__":
    main()
