"""Audit official UNSW-NB15 CSV files before they enter SCI experiments."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def file_hash(path: Path, block=1024 * 1024):
    md5 = hashlib.md5(); sha = hashlib.sha256(); size = 0
    with path.open("rb") as fh:
        while True:
            data = fh.read(block)
            if not data: break
            size += len(data); md5.update(data); sha.update(data)
    return {"bytes": size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def audit_csv(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    label = next((c for c in frame.columns if str(c).strip().lower() in {"label", "attack_cat"}), None)
    if label is None: raise ValueError(f"No label/attack_cat column in {path}")
    labels = frame[label].fillna("<NA>").astype(str).str.strip().value_counts().rename_axis("label").reset_index(name="count")
    return {"file": path.name, "rows": int(len(frame)), "columns": int(len(frame.columns)), "label_column": label, "labels": labels.to_dict("records"), "missing_cells": int(frame.isna().sum().sum()), "duplicate_rows": int(frame.duplicated().sum())}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--raw-dir",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args(); args.output.parent.mkdir(parents=True,exist_ok=True)
    files=sorted(args.raw_dir.glob("*.csv"));
    if not files: raise FileNotFoundError(f"No CSV files under {args.raw_dir}")
    result={"source":"UNSW Canberra Cyber official UNSW-NB15 project page","local_dir":str(args.raw_dir),"files":{p.name:{**file_hash(p),"audit":audit_csv(p)} for p in files}}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
