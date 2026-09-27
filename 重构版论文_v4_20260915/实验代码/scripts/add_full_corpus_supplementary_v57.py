"""Register the full-corpus experiment in the paper's supporting material.
Run after finalize_full_corpus_v56.py: adds supplementary item S29, rewrites the
Section 6.5 sentence that currently says the full corpus was not run, updates
the self-check row D15, and records the nineteenth review round.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
ASSEMBLER = ROOT / "scripts" / "assemble_supplementary_v5.py"

S29_ITEM = ('    "S29": ("全语料规模运行：2 429 503 条、逐种子指标与配对比较",\n'
            '            ["results_full_corpus_v49/full_corpus_paired_by_seed.csv",\n'
            '             "results_full_corpus_v49/full_corpus_summary.json",\n'
            '             "results_full_corpus_v49/metrics_by_seed.csv",\n'
            '             "results_rccf_cic_natural_v4_full/metrics_by_seed.csv"]),\n')
# Append after the S28 entry so the README index stays in numeric order.
S28_TAIL = '             "results_rccf_nbaiot_v48/metrics_by_seed.csv"]),\n'

EN_OLD = ("**Four datasets were evaluated, and the largest population is still a subset.** The conclusions "
          "are conditional on CIC-IDS2017, NSL-KDD, UNSW-NB15 and N-BaIoT. The scale check of Section 5.7 "
          "trains on 413,209 of the 2,429,503 deduplicated CIC records (17%), so a full-corpus run remains "
          "untested, and N-BaIoT is saturated for flow-feature classifiers (every model at or above 0.9998 "
          "Macro-F1), so it probes the mechanics of the aggregation step rather than discrimination "
          "difficulty. None of the four datasets represents production traffic.")
EN_NEW = ("**Four datasets were evaluated, and every corpus comes from one collection programme.** The "
          "conclusions are conditional on CIC-IDS2017 (both its capped populations and the full "
          "deduplicated corpus), NSL-KDD, UNSW-NB15 and N-BaIoT. N-BaIoT is saturated for flow-feature "
          "classifiers (every model at or above 0.9998 Macro-F1), so it probes the mechanics of the "
          "aggregation step rather than discrimination difficulty, and the external datasets remain "
          "independent native-label benchmarks rather than transfer tests. None of the four datasets "
          "represents production traffic, and no time-separated holdout on a common testbed exists in any "
          "of them.")

ZH_OLD = ("**评测了四个数据集，但最大总体仍是语料子集。** 本文结论以 CIC-IDS2017、NSL-KDD、UNSW-NB15 与 N-BaIoT 为条件。"
          "5.7 节的规模实验在 2 429 503 条去重后的 CIC 记录中训练了 413 209 条（17%），因此全语料训练仍未验证；"
          "而 N-BaIoT 对流量特征分类器已经饱和（所有模型 Macro-F1 均在 0.9998 以上），它检验的是聚合环节的机制而非判别难度。"
          "四个数据集都不代表生产流量。")
ZH_NEW = ("**评测了四个数据集，但它们来自同一批采集计划的有限覆盖。** 本文结论以 CIC-IDS2017（含截断总体与完整去重语料）、"
          "NSL-KDD、UNSW-NB15 与 N-BaIoT 为条件。N-BaIoT 对流量特征分类器已经饱和（所有模型 Macro-F1 均在 0.9998 以上），"
          "它检验的是聚合环节的机制而非判别难度；两个外部数据集仍只是独立原生标签基准，不构成迁移实验。四个数据集都不代表生产流量，"
          "也都无法提供同一测试床上时间分离的留出集。")

EN_S28_ROW = "| S28 | N-BaIoT benchmark: audit, class support, per-seed metrics and paired comparison |"
ZH_S28_ROW = "| S28 | N-BaIoT 基准：审计、类别支持度、逐种子指标与配对比较 |"
EN_S29_ROW = "| S29 | Full-corpus run: 2,429,503 flows, per-seed metrics and paired comparison |"
ZH_S29_ROW = "| S29 | 全语料运行：2 429 503 条、逐种子指标与配对比较 |"


def edit(path: Path, pairs: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
        else:
            print(f"  [{path.name}] anchor absent: {old[:50]}...")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    script = ASSEMBLER.read_text(encoding="utf-8")
    if '"S29"' not in script:
        if S28_TAIL not in script:
            raise SystemExit("S28 entry tail not found; cannot place S29 in order")
        script = script.replace(S28_TAIL, S28_TAIL + S29_ITEM, 1)
        ASSEMBLER.write_text(script, encoding="utf-8")
        print("assembler: S29 registered")

    edit(BASE / "English_SCI_Manuscript_v4.md",
         [(EN_OLD, EN_NEW), (EN_S28_ROW, EN_S28_ROW + "\n" + EN_S29_ROW)])
    edit(BASE / "中文SCI论文_v4_重构版.md",
         [(ZH_OLD, ZH_NEW), (ZH_S28_ROW, ZH_S28_ROW + "\n" + ZH_S29_ROW)])
    print("manuscripts: limitation rewritten, S29 listed")


if __name__ == "__main__":
    main()
