"""Reflect the two extension corpora and the day-level holdout in the manuscripts."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

EN_EDITS = [
    ("Four public datasets are used, all obtained from official or public sources [14-18].",
     "Four public datasets are used, all obtained from official or public sources [14-18]. "
     "Two further corpora, CIC-IDS2018 and CIC-IoT-2023, are used only in the extension "
     "experiments of Section 5.8."),
    ("**Four datasets were evaluated, and every corpus comes from one collection programme.** "
     "The conclusions are conditional on CIC-IDS2017 (both its capped populations and the full "
     "deduplicated corpus), NSL-KDD, UNSW-NB15 and N-BaIoT. N-BaIoT is saturated for flow-feature "
     "classifiers (every model at or above 0.9998 Macro-F1), so it probes the mechanics of the "
     "aggregation step rather than discrimination difficulty, and the external datasets remain "
     "independent native-label benchmarks rather than transfer tests. None of the four datasets "
     "represents production traffic, and no time-separated holdout on a common testbed exists in "
     "any of them.",
     "**Six datasets were evaluated, and every corpus comes from one collection programme.** The "
     "conclusions are conditional on CIC-IDS2017 (capped populations and the full deduplicated "
     "corpus), NSL-KDD, UNSW-NB15 and N-BaIoT; CIC-IDS2018 and CIC-IoT-2023 were added as "
     "extension corpora (Section 5.8) and reproduce the primary comparison. N-BaIoT is saturated "
     "for flow-feature classifiers (every model at or above 0.9998 Macro-F1), so it probes the "
     "mechanics of the aggregation step rather than discrimination difficulty, and the external "
     "datasets remain independent native-label benchmarks rather than transfer tests. None of the "
     "six represents production traffic. A day-level split of CIC-IDS2017 is constructible, but "
     "every capture day carries only a subset of the five classes (Monday Normal only; Tuesday "
     "Normal and Brute Force; Wednesday Normal and DoS/DDoS; Thursday adds Web Attack; Friday adds "
     "Bot), so it is not category-complete: the measured day-holdout Macro-F1 collapses to "
     "0.13-0.32 across the five days, which is what that limitation now quantifies."),
]

ZH_EDITS = [
    ("本文使用四个公开数据集，全部通过官方或公开镜像获取 [14-18]，不使用任何扫描、探测或真实攻击流量。",
     "本文使用四个公开数据集，全部通过官方或公开镜像获取 [14-18]，不使用任何扫描、探测或真实攻击流量。"
     "另有两个语料（CIC-IDS2018 与 CIC-IoT-2023）仅用于 5.8 节的扩展实验。"),
    ("## 7 结论",
     "**时间留出的现状。** CIC-IDS2017 可以按采集日划分，但每一天只覆盖五个类别中的一部分"
     "（周一仅正常流量；周二为正常与暴力破解；周三为正常与 DoS/DDoS；周四增加 Web 攻击；周五增加 Bot），"
     "因此按天留出可以构造、但类别不完整：五天留出实验的 Macro-F1 只有 0.13–0.32。"
     "本文评估的六个语料都不代表生产流量。\n\n## 7 结论"),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        if anchor not in text:
            continue
        if replacement in text:
            continue
        if not replacement.startswith(anchor) and replacement.split(anchor)[0] == "":
            pass
        if text.count(anchor) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(anchor)} times: "
                             f"{anchor[:60]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    for path, edits in ((EN, EN_EDITS), (ZH, ZH_EDITS)):
        applied = apply(path, edits)
        print(f"{path.name}: {applied} edit(s)")
    print("DATASET_SCOPE_UPDATED")


if __name__ == "__main__":
    main()
