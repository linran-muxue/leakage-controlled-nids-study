"""Quote the three 2025 corpora in the manuscripts and restate the corpus vintage.

The reviewer objection was that the evaluated corpora are old.  Three corpora
published in 2025 (UAVIDS-2025, GeNIS, IDS2025) were downloaded, processed and
evaluated under the same protocol.  This script quotes them in both manuscripts,
rewrites the "ten corpora, 1998-2023" vintage paragraph as "thirteen corpora,
1998-2025", and repairs the corpus count in the limitations section, which still
read "none of the six" in English and "four datasets" in Chinese.

Every replacement is anchored: the old text must be present exactly once, and
the numbers are read from the released benchmark summaries, never typed in.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

Y2025 = (("results_rccf_uavids2025_v1", "UAVIDS-2025"),
         ("results_rccf_genis2025_v1", "GeNIS"),
         ("results_rccf_ids2025_v1", "IDS2025"))

OLD_EN_VINTAGE = (
    "**Corpus vintage.** The ten corpora span 1998-2023, and five of them were released in 2020 "
    "or later: LITNET-2020, IoT-23 (both 2020), RT-IoT2022 (2022), ACI-IoT-2023 and "
    "CIC-IoT-2023. On each of the five the gate is indistinguishable from the equal-weight "
    "fusion of the same members: the differences are +0.000000 (LITNET-2020), +0.000000 "
    "(IoT-23), +0.000235 (RT-IoT2022), +0.000000 (ACI-IoT-2023) and +0.000028 (CIC-IoT-2023), "
    "against Macro-F1 levels of 0.999, 0.985, 0.940, 0.778 and 0.752. The 2020-2023 corpora are "
    "therefore not only newer but also more difficult than the 2017 data, and the "
    "aggregation-rule conclusion does not depend on the vintage of the source corpus. Corpora "
    "released in 2024-2025 are distributed behind request forms; the preparation and evaluation "
    "scripts are released so they can be added under the same protocol.")

OLD_ZH_VINTAGE = (
    "**语料年代。** 本文的十个语料跨越 1998–2023，其中五个发布于 2020 年及以后："
    "LITNET-2020、IoT-23（均 2020）、RT-IoT2022（2022）、ACI-IoT-2023 与 CIC-IoT-2023。"
    "在这五个语料上，门控与同成员等权融合无法区分：差值分别为 "
    "+0.000000（LITNET-2020）、+0.000000（IoT-23）、+0.000235（RT-IoT2022）、"
    "+0.000000（ACI-IoT-2023）与 +0.000028（CIC-IoT-2023）；对应的 Macro-F1 为 "
    "0.999、0.985、0.940、0.778 与 0.752。因此新语料不仅年代更近，判别难度也更高，"
    "而聚合规则的结论并不依赖于源语料的年代。2024–2025 年发布的语料多需申请获取；"
    "本文公开全部处理与评估脚本，可在同一协议下继续补充。")

# The wording this script produced on its first run.  Enumerating the three 2025
# differences as "+0.000000 (X), +0.000000 (Y) and +0.000000 (Z)" made the
# paragraph repeat a numeric pair, which scripts/check_duplicate_sentences_v27.py
# rejects, so the sentence states the shared difference once instead.
EN_VINTAGE_V1 = (
    "**Corpus vintage.** The thirteen corpora span 1998-2025; eight of them were released in "
    "2020 or later (LITNET-2020, IoT-23, RT-IoT2022, ACI-IoT-2023, CIC-IoT-2023, and three "
    "published in 2025: UAVIDS-2025, GeNIS, IDS2025). On the 2020-2023 group the gate is "
    "indistinguishable from the equal-weight fusion of the same members: the differences are "
    "+0.000000 (LITNET-2020), +0.000000 (IoT-23), +0.000235 (RT-IoT2022), +0.000000 "
    "(ACI-IoT-2023) and +0.000028 (CIC-IoT-2023), against Macro-F1 levels of 0.999, 0.985, "
    "0.940, 0.778 and 0.752. The three corpora published in 2025 reproduce the same result "
    "over 5, 4 and 7 classes: the differences are +0.000000 (UAVIDS-2025), +0.000000 (GeNIS) "
    "and +0.000000 (IDS2025), against Macro-F1 levels of 0.9449, 0.9999 and 0.9750. The newer "
    "corpora therefore do not sit at a single difficulty level, and the aggregation-rule "
    "conclusion does not depend on the vintage of the source corpus.")
ZH_VINTAGE_V1 = (
    "**语料年代。** 本文的十三个语料跨越 1998–2025；其中八个发布于 2020 年及以后"
    "（LITNET-2020、IoT-23、RT-IoT2022、ACI-IoT-2023、CIC-IoT-2023，以及 2025 年发布的"
    "三份：UAVIDS-2025、GeNIS、IDS2025）。在 2020–2023 的五个语料上，门控与同成员等权"
    "融合无法区分：差值分别为 +0.000000（LITNET-2020）、+0.000000（IoT-23）、"
    "+0.000235（RT-IoT2022）、+0.000000（ACI-IoT-2023）与 +0.000028（CIC-IoT-2023）；"
    "对应的 Macro-F1 为 0.999、0.985、0.940、0.778 与 0.752。2025 年发布的三份语料在 "
    "5、4、7 个类别上复现了同一结果：差值分别为 +0.000000（UAVIDS-2025）、"
    "+0.000000（GeNIS）与 +0.000000（IDS2025）；对应的 Macro-F1 为 0.9449、0.9999 与 "
    "0.9750。因此新语料并不处在同一个难度水平，而聚合规则的结论并不依赖于源语料的年代。")


def summary(folder: str) -> dict:
    path = ROOT / folder / "benchmark_summary.json"
    if not path.exists():
        raise SystemExit(f"missing released summary: {folder}/benchmark_summary.json")
    return json.loads(path.read_text(encoding="utf-8"))


def replace_once(path: Path, old: str, new: str, note: str = "") -> None:
    """Replace an anchored string, refusing to guess if the anchor is not unique."""
    text = path.read_text(encoding="utf-8")
    if new and new in text and old not in text:
        print(f"{path.name}: already applied ({note or old[:32]!r})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor appears {text.count(old)} times: {old[:60]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note or 'edited'} ({len(old)} -> {len(new)} chars)")


def replace_superseded(path: Path, old: str, new: str, note: str = "") -> bool:
    """Swap an earlier wording for the current one; a no-op if it is absent."""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: superseded wording appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: superseded wording replaced ({note})")
    return True


def main() -> None:
    rows = [(label, summary(folder)) for folder, label in Y2025]
    labels = [label for label, _ in rows]
    diffs = [f"{data['same_members_difference']:+.6f}" for _, data in rows]
    f1s = [f"{data['rccf_mean_macro_f1']:.4f}" for _, data in rows]
    classes = [str(len(data["classes"])) for _, data in rows]
    if len(set(diffs)) != 1:
        raise SystemExit(f"the three 2025 corpora no longer share one difference: {diffs}")
    shared = diffs[0]

    en_new = (
        "**Corpus vintage.** The thirteen corpora span 1998-2025; eight of them were released in "
        "2020 or later (LITNET-2020, IoT-23, RT-IoT2022, ACI-IoT-2023, CIC-IoT-2023, and three "
        "published in 2025: UAVIDS-2025, GeNIS, IDS2025). On the 2020-2023 group the gate is "
        "indistinguishable from the equal-weight fusion of the same members: the differences are "
        "+0.000000 (LITNET-2020), +0.000000 (IoT-23), +0.000235 (RT-IoT2022), +0.000000 "
        "(ACI-IoT-2023) and +0.000028 (CIC-IoT-2023), against Macro-F1 levels of 0.999, 0.985, "
        "0.940, 0.778 and 0.752. The three corpora published in 2025 reproduce the same result "
        f"over {classes[0]}, {classes[1]} and {classes[2]} classes, with a same-members "
        f"difference of {shared} on each, against Macro-F1 levels of {f1s[0]} ({labels[0]}), "
        f"{f1s[1]} ({labels[1]}) and {f1s[2]} ({labels[2]}). The newer corpora therefore do not "
        "sit at a single difficulty level, and the aggregation-rule conclusion does not depend "
        "on the vintage of the source corpus.")
    zh_new = (
        "**语料年代。** 本文的十三个语料跨越 1998–2025；其中八个发布于 2020 年及以后"
        "（LITNET-2020、IoT-23、RT-IoT2022、ACI-IoT-2023、CIC-IoT-2023，以及 2025 年发布的"
        "三份：UAVIDS-2025、GeNIS、IDS2025）。在 2020–2023 的五个语料上，门控与同成员等权"
        "融合无法区分：差值分别为 +0.000000（LITNET-2020）、+0.000000（IoT-23）、"
        "+0.000235（RT-IoT2022）、+0.000000（ACI-IoT-2023）与 +0.000028（CIC-IoT-2023）；"
        "对应的 Macro-F1 为 0.999、0.985、0.940、0.778 与 0.752。2025 年发布的三份语料在 "
        f"{classes[0]}、{classes[1]}、{classes[2]} 个类别上复现了同一结果：差值均为 {shared}；"
        f"对应的 Macro-F1 为 {f1s[0]}（{labels[0]}）、{f1s[1]}（{labels[1]}）与 "
        f"{f1s[2]}（{labels[2]}）。因此新语料并不处在同一个难度水平，而聚合规则的结论并不"
        "依赖于源语料的年代。")

    replace_superseded(EN, EN_VINTAGE_V1, en_new, "vintage wording")
    replace_superseded(ZH, ZH_VINTAGE_V1, zh_new, "语料年代措辞")
    replace_once(EN, OLD_EN_VINTAGE, en_new, "corpus-vintage paragraph")
    replace_once(ZH, OLD_ZH_VINTAGE, zh_new, "语料年代段落")

    # the limitations section counts the corpora; the ten-corpus wording was left
    # behind when the recent corpora were added, and the two languages disagreed.
    replace_once(EN,
                 "**Ten corpora were evaluated, and every corpus comes from one collection "
                 "programme.**",
                 "**Thirteen corpora were evaluated, and every corpus comes from one collection "
                 "programme.**", "limitation heading count")
    replace_once(EN,
                 "; CIC-IDS2018 and CIC-IoT-2023 were added as extension corpora (Section 5.8) "
                 "and reproduce the primary comparison.",
                 "; CIC-IDS2018, CIC-IoT-2023, LITNET-2020, IoT-23, RT-IoT2022, ACI-IoT-2023 and "
                 "the three 2025 corpora (UAVIDS-2025, GeNIS, IDS2025) were added as extension "
                 "corpora (Section 5.8) and reproduce the primary comparison.",
                 "limitation extension list")
    replace_once(EN, "None of the six represents production traffic.",
                 "None of the thirteen represents production traffic.",
                 "limitation corpus count")

    replace_once(ZH,
                 "**评测了四个数据集，但它们来自同一批采集计划的有限覆盖。** 本文结论以 "
                 "CIC-IDS2017（含截断总体与完整去重语料）、NSL-KDD、UNSW-NB15 与 N-BaIoT 为条件。",
                 "**评测了十三个语料，但它们来自同一批采集计划的有限覆盖。** 本文结论以 "
                 "CIC-IDS2017（含截断总体与完整去重语料）、NSL-KDD、UNSW-NB15 与 N-BaIoT 为条件；"
                 "其余九个语料（CIC-IDS2018、CIC-IoT-2023、LITNET-2020、IoT-23、RT-IoT2022、"
                 "ACI-IoT-2023 与 2025 年的 UAVIDS-2025、GeNIS、IDS2025）作为 5.8 节的扩展语料"
                 "复现了主比较。", "局限段落语料数")
    replace_once(ZH, "四个数据集都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
                 "十三个语料都不代表生产流量，也都无法提供同一测试床上时间分离的留出集。",
                 "局限段落生产流量")
    replace_once(ZH, "五天留出实验的 Macro-F1 只有 0.13–0.32。本文评估的十个语料都不代表生产流量。",
                 "五天留出实验的 Macro-F1 只有 0.13–0.32。", "删除重复的语料计数句")
    print("Y2025_CORPORA_SECTION_ADDED")


if __name__ == "__main__":
    main()
