"""Inventory the processed datasets: what exists locally, and how to rebuild it.

The corpora and the processed populations are deliberately not redistributed -
they are large and the raw files carry their own licences - so the release ships
the scripts, the audit records and this inventory instead.  For every data
directory the document records the files with their sizes, the row counts, the
stage counts from the de-duplication audit, the class counts, and a SHA-256 for
every file up to 64 MB; the numbers the paper prints are asserted against them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = BASE / "数据产物清单.md"
HASH_LIMIT = 64 * 1024 * 1024

PUBLISHED = {
    "data_processed_cic_natural_v3b": ("截断总体（每类上限 2 万）", "表 3、表 4(a)", 7_986),
    "data_processed_cic_balanced_v3b": ("平衡控制总体", "表 4(b)", 505),
    "data_processed_cic_natural_v4_scale200k": ("规模阶梯（每类上限 20 万）", "表 7、S27", 61_982),
    "data_processed_cic_natural_v4_full": ("全去重语料", "表 7、S29", 364_426),
    "data_processed_nbaiot_v48": ("N-BaIoT 三分类基准", "表 8、S28", 27_000),
    "data_external_nsl_kdd_processed_v2": ("NSL-KDD 原生标签", "表 8、S28", 22_544),
    "data_processed_gotham2025_v1": ("Gotham-2025 数据包级基准（2025）",
                                      "扩展实验报告九、S31", 29_718),
}


def count_rows(path: Path) -> int | None:
    if path.suffix.lower() != ".csv":
        return None
    try:
        with path.open("rb") as handle:
            rows = 0
            while chunk := handle.read(1 << 23):
                rows += chunk.count(b"\n")
        return max(rows - 1, 0)
    except OSError:
        return None


def digest(path: Path) -> str | None:
    if path.stat().st_size > HASH_LIMIT:
        return None
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            sha.update(chunk)
    return sha.hexdigest()[:16]


def directories() -> list[Path]:
    return sorted(p for p in ROOT.iterdir()
                  if p.is_dir() and (p.name.startswith("data_processed")
                                     or p.name.startswith("data_external")))


def audit_row(directory: Path) -> dict:
    """Row counts for the data directories the paper uses, from the audit records."""
    name = directory.name
    if name.startswith("data_processed_cic_natural_v3b"):
        audit = results_audit("data_processed_cic_natural_v3b")
        if audit:
            splits = audit["processed"]["splits"]
            return {"train": splits["train"]["rows"], "validation": splits["validation"]["rows"],
                    "test": splits["test"]["rows"],
                    "features": splits["train"]["feature_count"],
                    "classes": len(splits["train"]["class_counts"])}
    if name.startswith("data_processed_cic_balanced_v3b"):
        audit = results_audit("data_processed_cic_balanced_v3b")
        if audit:
            splits = audit["processed"]["splits"]
            return {"train": splits["train"]["rows"], "validation": splits["validation"]["rows"],
                    "test": splits["test"]["rows"],
                    "features": splits["train"]["feature_count"],
                    "classes": len(splits["train"]["class_counts"])}
    summary = directory / "dataset_summary.csv"
    if summary.exists():
        frame = pd.read_csv(summary)
        counts = frame.set_index("target")["count"].to_dict()
        return {"train": None, "validation": None, "test": None,
                "features": feature_count(directory),
                "classes": len(counts), "class_counts": counts}
    summary_json = directory / "dataset_summary.json"
    if summary_json.exists():
        data = json.loads(summary_json.read_text(encoding="utf-8"))
        return {"train": data.get("train_rows"), "validation": None,
                "test": data.get("test_rows"), "features": data.get("feature_count"),
                "classes": len(data.get("train_class_counts", {})),
                "class_counts": data.get("train_class_counts", {})}
    return {}


def feature_count(directory: Path) -> int | None:
    """Columns of train.csv minus the label column, from the header alone."""
    for name in ("train.csv", "test.csv"):
        path = directory / name
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            header = handle.readline().strip()
        if header:
            return len(header.split(",")) - 1
    return None


def results_audit(processed_name: str) -> dict | None:
    candidate = (ROOT / "results_data_audit_cic_natural_v3b" / "data_processing_audit.json")
    if processed_name.endswith("balanced_v3b"):
        candidate = ROOT / "results_data_audit_cic_balanced_v3b" / "data_processing_audit.json"
    if not candidate.exists():
        return None
    return json.loads(candidate.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()
    dirs = directories()
    inventory: list[dict] = []
    for directory in dirs:
        files = sorted(p for p in directory.rglob("*") if p.is_file())
        rows = []
        for path in files:
            rows.append({"name": path.name, "relative": path.relative_to(directory).as_posix(),
                         "mb": path.stat().st_size / 1e6, "lines": count_rows(path),
                         "sha256": digest(path)})
        dedup = directory / "dedup_audit.json"
        inventory.append({
            "name": directory.name,
            "files": rows,
            "total_mb": sum(row["mb"] for row in rows),
            "dedup": json.loads(dedup.read_text(encoding="utf-8")) if dedup.exists() else {},
            "counts": audit_row(directory),
            "published": PUBLISHED.get(directory.name),
        })

    lines: list[str] = []
    lines.append("# 数据产物清单")
    lines.append("")
    lines.append("> 语料与处理后数据按许可与体积要求**不随投稿包分发**；本清单把它们变成可核对的对象："
                 "逐文件的大小与 SHA-256（≤64 MB 的文件）、CSV 行数、去重审计的阶段计数、类别计数，"
                 "以及重建命令。论文印出的总体规模在这里被逐一断言。")
    lines.append("")
    lines.append("## 一、论文用到的总体")
    lines.append("")
    lines.append("| 总体 | 目录 | 训练 / 验证 / 测试 | 特征 | 类别 | 论文位置 | 校验 |")
    lines.append("|---|---|---|---:|---:|---|---|")
    def split_rows(item: dict) -> dict[str, int | None]:
        by_name = {row["name"]: row["lines"] for row in item["files"]}
        counts = item["counts"]
        return {
            "train": by_name.get("train.csv") or counts.get("train"),
            "validation": by_name.get("validation.csv") or counts.get("validation"),
            "test": by_name.get("test.csv") or counts.get("test"),
        }

    problems: list[str] = []
    for item in inventory:
        if not item["published"]:
            continue
        title, place, test_rows = item["published"]
        counts = item["counts"]
        splits_map = split_rows(item)
        splits = " / ".join(f"{splits_map[key]:,}" if splits_map.get(key) else "—"
                            for key in ("train", "validation", "test"))
        feature = counts.get("features") or "—"
        classes = counts.get("classes") or "—"
        if splits_map.get("test") == test_rows:
            check = "一致"
        else:
            check = "不一致"
            problems.append(f"{item['name']}: 测试行 {splits_map.get('test')} != 论文 {test_rows}")
        lines.append(f"| {title} | `{item['name']}` | {splits} | {feature} | {classes} | {place} | "
                     f"{check} |")
    lines.append("")
    assert not problems, "；".join(problems)
    lines.append("类别分布（各目录 `dataset_summary`）：")
    lines.append("")
    for item in inventory:
        if not item["published"]:
            continue
        counts = item["counts"].get("class_counts") or {}
        if not counts:
            continue
        detail = "、".join(f"{label} {value:,}" for label, value in counts.items())
        lines.append(f"- `{item['name']}`：{detail}")
    lines.append("")
    lines.append("## 二、逐目录文件清单")
    lines.append("")
    lines.append("行数按 CSV 逐行统计（`wc -l` 等价）；SHA-256 只对 64 MB 以内的文件计算，"
                 "更大的文件以大小与行数为准（它们在公开仓库里可逐文件下载核对）。")
    lines.append("")
    lines.append("| 目录 | 文件 | 大小 MB | 行数 | SHA-256（前 16 位）|")
    lines.append("|---|---|---:|---:|---|")
    for item in inventory:
        for row in item["files"]:
            line_count = f"{row['lines']:,}" if row["lines"] is not None else "—"
            lines.append(f"| `{item['name']}` | `{row['relative']}` | {row['mb']:.2f} | "
                         f"{line_count} | `{row['sha256'] or '—'}` |")
    lines.append("")
    lines.append("## 三、去重与清洗的阶段计数")
    lines.append("")
    lines.append("| 目录 | 原始 | 可映射 | 剔除标签 | 非有限值 | 有效 | 重复行 | 物理有效 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for item in inventory:
        dedup = item["dedup"]
        if not dedup:
            continue
        def value(key: str) -> str:
            raw = dedup.get(key)
            return f"{raw:,}" if isinstance(raw, int) else "—"
        lines.append(f"| `{item['name']}` | {value('source_rows')} | {value('mapped_rows')} | "
                     f"{value('excluded_label_rows')} | {value('invalid_rows')} | "
                     f"{value('valid_rows')} | {value('duplicate_rows')} | "
                     f"{value('physical_valid_rows')} |")
    lines.append("")
    published_names = {name for name in PUBLISHED}
    history = [item for item in inventory if item["name"] not in published_names]
    lines.append("## 四、历史迭代目录（未进入论文）")
    lines.append("")
    lines.append("| 目录 | 文件数 | 大小 MB | 说明 |")
    lines.append("|---|---:|---:|---|")
    for item in history:
        lines.append(f"| `{item['name']}` | {len(item['files'])} | {item['total_mb']:.1f} | "
                     f"早期版本或其它先验设定，保留用于追溯，不作为论文证据 |")
    lines.append("")
    lines.append("## 五、重建命令")
    lines.append("")
    lines.append("```powershell")
    lines.append(r"$py = 'E:\论文\.venv\Scripts\python.exe'")
    lines.append(r"# 六阶段审计 + 截断总体（每类上限 2 万）")
    lines.append(r"& $py scripts\audit_data_processing_v1.py --raw-dir data\raw\MachineLearningCVE --processed-dir data_processed_cic_natural_v3b")
    lines.append(r"# 平衡控制总体、规模阶梯、全语料（同一条流水线，换上限）")
    lines.append(r"& $py scripts\prepare_dataset.py --per-class-cap 20000  --balance --out data_processed_cic_balanced_v3b")
    lines.append(r"& $py scripts\prepare_dataset.py --per-class-cap 200000 --out data_processed_cic_natural_v4_scale200k")
    lines.append(r"& $py scripts\prepare_dataset.py --no-cap            --out data_processed_cic_natural_v4_full")
    lines.append(r"# 外部语料")
    lines.append(r"& $py scripts\prepare_nbaiot_v48.py --processed-dir data_processed_nbaiot_v48")
    lines.append("```")
    lines.append("")
    lines.append("> 原始文件不在本包内；按《数据与资料来源总表》的 URL、检索日期与 SHA-256 取得后，"
                 "以上命令会重建同名目录，`scripts/audit_data_authenticity_v1.py` 会逐字节比对摘要。")
    lines.append("")
    if args.outdir:
        out = Path(args.outdir) / "数据产物清单.md"
    else:
        out = OUT
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"DATA_PRODUCTS_WRITTEN={out}")
    print(f"directories={len(inventory)} published={len(published_names)} "
          f"files={sum(len(item['files']) for item in inventory)}")


if __name__ == "__main__":
    main()
