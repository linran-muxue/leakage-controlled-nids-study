"""Record the full-corpus run in the self-check table (rows D15 and F4).

Reads the ten-seed summary written by ``finalize_full_corpus_v56.py`` so the
evidence line carries the measured numbers rather than placeholders, and
refreshes the supplementary item/file counts from the assembled bundle.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SC = BASE / "论文自查表.md"
SUMMARY = ROOT / "results_full_corpus_v49" / "full_corpus_summary.json"
DEDUP = ROOT / "data_processed_cic_natural_v4_full" / "dedup_audit.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from supplementary_paths_v1 import supplementary_bundle


def bundle_counts() -> tuple[str, int, int]:
    bundle = supplementary_bundle(BASE)
    readme = (bundle / "README.md").read_text(encoding="utf-8")
    items = len(re.findall(r"^\| (S\d+) \|", readme, flags=re.M))
    checksums = (bundle / "checksums.sha256").read_text(encoding="utf-8")
    files = len([line for line in checksums.splitlines() if line.strip()])
    return bundle.name, items, files


def tost_text(summary: dict) -> str:
    tost = summary.get("tost") or {}
    if tost and all(v.get("equivalent") for v in tost.values()):
        margins = "、".join(sorted(tost))
        return f"TOST 在 {margins} 边界下均成立"
    # Report each margin separately: on the full corpus the 0.005 margin can
    # fail while 0.01 still holds, and collapsing that into a single verdict
    # would misstate the result in either direction.
    parts = []
    for margin in sorted(tost):
        verdict = "等价" if tost[margin].get("equivalent") else "不等价"
        parts.append(f"{margin} 边界{verdict}")
    return "TOST " + "、".join(parts) if parts else "TOST 未能判定"


def d15_row(summary: dict) -> str:
    lo, hi = summary["seed_level_90_interval"]
    rows = json.loads(DEDUP.read_text(encoding="utf-8"))["unique_rows_after_conflict"]
    rows_text = f"{rows:,}".replace(",", " ")
    cost = ""
    if summary.get("rccf_mean_train_seconds"):
        cost = (f"每个种子 RCCF 训练 {summary['rccf_mean_train_seconds']:.0f} 秒、"
                f"等权森林 {summary['control_mean_train_seconds']:.0f} 秒"
                f"（约 {summary['train_slowdown']:.0f} 倍）；")
    return (
        "| D15 | 规模与领域稳健性 | 结论不得依赖被截断的子集 | **通过** | "
        "规模实验把 CIC-IDS2017 总体扩大 7.8 倍（413 209 条，十种子）：平均配对差 −0.001137，"
        "90% 区间 [−0.002966, +0.000692]，TOST 在 0.005 与 0.01 边界下均成立；"
        f"取消每类上限后在完整去重语料 {rows_text} 条上完成十种子配对："
        f"平均差 {summary['mean_difference']:+.6f}，种子级 90% 区间 [{lo:+.6f}, {hi:+.6f}]，"
        f"{tost_text(summary)}，{cost}"
        "第四个数据集 N-BaIoT（18 万条、IoT 领域）上所有模型 Macro-F1 ≥ 0.9998，RCCF 与等权森林差异为 0"
        "（结果见 §5.7 与补充材料 S27、S28、S29） |"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-non-equivalent", action="store_true",
                        help="permit writing D15 when TOST does not establish equivalence")
    args = parser.parse_args(argv)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if summary.get("n_seeds", 0) < 10 and not args.dry_run:
        raise SystemExit(f"only {summary.get('n_seeds')} seed(s) available; refusing to write D15")
    equivalent = bool(summary.get("tost")) and all(
        v.get("equivalent") for v in summary["tost"].values())
    if not equivalent and not args.dry_run and not args.allow_non_equivalent:
        raise SystemExit(
            "TOST does not establish equivalence at both margins; D15 would need to be "
            "rerated (部分通过) and the closing counts updated. Re-run with "
            "--allow-non-equivalent only after that review.")

    name, items, files = bundle_counts()
    text = SC.read_text(encoding="utf-8")
    changed: list[str] = []

    new_d15 = d15_row(summary)
    updated, count = re.subn(r"^\| D15 \|.*$", new_d15, text, count=1, flags=re.M)
    if count:
        text = updated
        changed.append("D15")
    else:
        print("D15 row not found")

    f4_new = (f"| F4 | 补充材料 | 与清单一致且存在 | **通过** | `{name}/`：{items} 条目、"
              f"{files} 个材料文件，另含 `README.md` 索引与 `checksums.sha256` 校验")
    updated, count = re.subn(r"^\| F4 \| 补充材料 \|.*$", f4_new, text, count=1, flags=re.M)
    if count:
        text = updated
        changed.append("F4")
    else:
        print("F4 row not found")

    hist_old = "目录随后扩充至 S01–S28，69 个材料文件"
    hist_new = f"目录随后扩充至 S01–S{items:02d}，{files} 个材料文件"
    if hist_old in text:
        text = text.replace(hist_old, hist_new, 1)
        changed.append("F4 history row")
    old_name = "目录重命名为 `补充材料_S01_S28/`，条目数重算"
    new_name = f"目录重命名为 `{name}/`，条目数重算"
    if old_name in text:
        text = text.replace(old_name, new_name, 1)
        changed.append("bundle rename row")

    if args.dry_run:
        print("DRY RUN, would update:", ", ".join(changed))
        print(new_d15)
        return 0

    SC.write_text(text, encoding="utf-8")
    print("updated:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
