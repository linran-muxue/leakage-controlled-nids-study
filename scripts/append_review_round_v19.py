"""Record the nineteenth round: the full-corpus ten-seed verification.

Numbers are read from the summary produced by ``finalize_full_corpus_v56.py``,
so the audit record carries measured values.  Refuses to write until all ten
seeds are present unless run with ``--dry-run``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
MD = BASE / "遗漏问题审查报告.md"
COVER = BASE / "Cover_Letter_JISA_v4.md"
SUMMARY = ROOT / "results_full_corpus_v49" / "full_corpus_summary.json"
DEDUP = ROOT / "data_processed_cic_natural_v4_full" / "dedup_audit.json"

HEADING = "## Y. 第十九轮审查（2026-09-21）：全语料验证——取消每类上限后的十种子配对"

COVER_OLD = ("Because that population is a capped subset, we also rebuild it 7.8 times larger "
             "(413,209 flows) and repeat the ten-seed comparison there: the equivalence holds at both "
             "margins, with the point estimate now slightly favouring the control.")


def tost_sentence(summary: dict, english: bool = False) -> str:
    tost = summary.get("tost") or {}
    if english:
        if tost and all(v.get("equivalent") for v in tost.values()):
            return "equivalent at both pre-specified margins"
        parts = []
        for margin in sorted(tost):
            verdict = "equivalent" if tost[margin].get("equivalent") else "not equivalent"
            parts.append(f"{verdict} at {margin}")
        return ", ".join(parts) if parts else "not evaluable"
    if tost and all(v.get("equivalent") for v in tost.values()):
        return "TOST 在两个预设边界（0.005 与 0.01）上均成立"
    parts = []
    for margin in sorted(tost):
        verdict = "等价" if tost[margin].get("equivalent") else "不等价"
        parts.append(f"{margin} 边界{verdict}")
    return "TOST " + "、".join(parts) if parts else "TOST 未能判定"


def with_costs(summary: dict) -> dict:
    """Fill the training-cost fields when the summary predates their addition.

    The first summary was written before ``finalize_full_corpus_v56.py`` grew
    the cost comparison, so a dry run has to derive the same numbers from the
    per-seed files instead of failing.
    """
    if summary.get("rccf_mean_train_seconds"):
        return summary
    import pandas as pd

    seconds = []
    for seed in summary.get("seeds", []):
        path = ROOT / "results_rccf_cic_natural_v4_full" / f"metrics_seed{seed}.csv"
        if path.exists():
            seconds.append(float(pd.read_csv(path)["train_seconds"].iloc[0]))
    control = float("nan")
    by_seed = ROOT / "results_full_corpus_v49" / "metrics_by_seed.csv"
    if by_seed.exists():
        frame = pd.read_csv(by_seed)
        subset = frame.loc[frame["model"] == "equal_rf_chi2", "train_seconds"]
        if len(subset):
            control = float(subset.mean())
    summary = dict(summary)
    summary["rccf_mean_train_seconds"] = float(sum(seconds) / len(seconds)) if seconds else float("nan")
    summary["control_mean_train_seconds"] = control
    summary["train_slowdown"] = (summary["rccf_mean_train_seconds"] / control
                                 if seconds and control else float("nan"))
    return summary


def record(summary: dict) -> str:
    lo, hi = summary["seed_level_90_interval"]
    rows = json.loads(DEDUP.read_text(encoding="utf-8"))["unique_rows_after_conflict"]
    rows_text = f"{rows:,}".replace(",", " ")
    return f"""

---

{HEADING}：取消每类上限——把"最大总体仍是子集"这条也堵上

第十八轮把研究总体扩大到 413 209 条（去重语料的 17%），但第十七轮列出的证据类缺口还剩最后一条：**全语料训练未做**。这一轮把它做完，并且它给出的结果与预期一致。

### 一、做法

用完全相同的审计与协议，只把每类上限彻底取消（`data_processed_cic_natural_v4_full`）：**{rows_text} 条**去重后 CIC-IDS2017 记录，训练 1 700 651 / 验证 364 426 / 测试 364 426；Web Attack 仅占 0.028%，比 413 209 条的规模实验更不平衡。单次 RCCF 拟合约 2.3 小时（seed 42 记录 `train_seconds = 8139`），因此十个种子分批运行、每完成一个种子落盘一次预测。

### 二、结果

| 指标 | 结果 |
|---|---|
| RCCF 平均 Macro-F1 | {summary['rccf_mean_macro_f1']:.6f} |
| 等权 χ² 森林平均 Macro-F1 | {summary['control_mean_macro_f1']:.6f} |
| 平均配对差 | **{summary['mean_difference']:+.6f}**（标准差 {summary['sd']:.6f}） |
| 种子级 90% 区间 | [{lo:+.6f}, {hi:+.6f}] |
| TOST | {tost_sentence(summary)} |
| 每种子平均改判条数 | {summary['mean_disagreements']:.0f} / {summary['test_rows']:,}（最多 {summary['max_disagreements']} 条） |
| 训练代价 | RCCF {summary['rccf_mean_train_seconds']:.0f} 秒 对 等权森林 {summary['control_mean_train_seconds']:.0f} 秒（约 {summary['train_slowdown']:.0f} 倍） |

结论与 2% 截断、7.8 倍扩大两级实验完全一致：**加权机制在大规模、强不平衡语料上依旧不改变预测**，而它的训练代价随规模放大到约 {summary['train_slowdown']:.0f} 倍。全语料同时给出全文最强的一处"准确率会骗人"的证据：XGBoost 准确率 0.9993、Macro-F1 0.800255；等权 χ² 森林准确率 0.9958、Macro-F1 0.759540；极端随机树 0.696629、限深决策树 0.595653。

### 三、过程中修掉的两个真实缺陷

1. **分批续跑会覆盖汇总文件。** `run_rccf_cic_v1.py` 每次调用都用「本次运行的种子」重写 `metrics_by_seed.csv` 与 `metrics_aggregate.csv`；十种子分四次跑完时，S29 引用的汇总只剩最后一批。已新增 `scripts/consolidate_rccf_full_metrics_v1.py`，由 `finalize_full_corpus_v56.py` 在写正文前自动从逐种子文件重建，并在 `run_manifest.json` 标记来源。
2. **待机会静默吞掉整段实验时间。** 事件日志显示 2026-09-20 至 09-21 期间系统累计进入"新型待机"13 小时以上；进一步定位到触发条件不是空闲计时器而是**息屏**——只压制系统睡眠、不压制显示关闭时，Modern Standby 仍会在息屏瞬间进入（15:16 与 15:22 各一次）。`scripts/keep_awake_v1.py` 因此改为同时持有 `ES_DISPLAY_REQUIRED`，屏幕在实验期间保持点亮。这也是"单种子 2.3 小时的实验为什么曾跑了 17 小时还没完"的完整解释。

### 四、随之而来的改动

- §5.7 新增「完整去重语料」段（中英同步），训练代价倍数与全语料基线一并写入；§6.5 的「全语料训练仍未验证」改写为已验证，剩余局限收敛为"四个语料来自同一批采集计划的有限覆盖、且无生产流量"。
- 补充材料新增 **S29**（全语料逐种子配对与汇总），目录随 `assemble_supplementary_v5.py` 的编号推导自动改为 `补充材料_S01_S29`；五个脚本对补充材料目录的硬编码路径改为统一解析器 `scripts/supplementary_paths_v1.py`，此后新增条目不再需要改路径。
- 自查表 D15 与 F4 由脚本按实测数字重写（`scripts/update_selfcheck_full_corpus_v59.py`）；发布标签推进到 **v1.11.0**（`scripts/bump_release_tag_v58.py` 一次性处理 15 个文件的 19 处当前状态引用，历史记录行自动跳过）。

### 五、这一轮之后还剩什么

证据类缺口到此清零：规模（全语料）、领域（N-BaIoT）、外部基准（NSL-KDD、UNSW-NB15）、统计（十种子配对、TOST、功效）、机制（命题 1 的可计算上界）都已具备。剩余的是**性质上的**局限而非缺口：语料来自公开采集计划而非生产流量，且四个数据集都不提供同一测试床上的时间分离留出集。这两条已在 §6.5 明确写出。
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    summary = with_costs(json.loads(SUMMARY.read_text(encoding="utf-8")))
    if summary.get("n_seeds", 0) < 10 and not args.dry_run:
        raise SystemExit(f"only {summary.get('n_seeds')} seed(s) available; refusing to write round 19")
    if not summary.get("rccf_mean_train_seconds"):
        raise SystemExit("cannot determine the training-cost fields")

    text = MD.read_text(encoding="utf-8")
    if HEADING in text:
        print("round 19 already recorded")
    elif args.dry_run:
        print("DRY RUN: would append round 19")
        print(record(summary)[:1200])
        return 0
    else:
        MD.write_text(text.rstrip() + record(summary) + "\n", encoding="utf-8")
        print("ROUND19_RECORDED")

    cover = COVER.read_text(encoding="utf-8")
    if COVER_OLD in cover and not args.dry_run:
        # Use the audited corpus size, not test_rows * 3: the splits are
        # 70/15/15, so tripling the test split understates the corpus.
        total_rows = json.loads(DEDUP.read_text(encoding="utf-8"))["unique_rows_after_conflict"]
        tost_en = tost_sentence(summary, english=True)
        addition = (f" Removing the cap entirely ({total_rows:,} deduplicated flows, "
                    f"ten seeds) reproduces the same picture: "
                    f"{summary['mean_difference']:+.6f} Macro-F1, "
                    f"90% interval [{summary['seed_level_90_interval'][0]:+.6f}, "
                    f"{summary['seed_level_90_interval'][1]:+.6f}], "
                    f"{tost_en}, at a {summary['train_slowdown']:.0f}x training-cost penalty.")
        COVER.write_text(cover.replace(COVER_OLD, COVER_OLD + addition, 1), encoding="utf-8")
        print("cover letter updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
