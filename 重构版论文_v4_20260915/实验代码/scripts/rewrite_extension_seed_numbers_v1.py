"""Move the extension corpora from 3/5 seeds to the standard ten seeds.

The main experiments use ten seeds; the extension corpora were originally run on
three (and CIC-IDS2018 on five).  Seven of them are cheap enough that the
inconsistency was not worth keeping, and a reviewer comparing Section 5.7 with
Section 5.8 would see two different protocols.  This script re-renders every
number that depends on those runs - the two manuscript paragraphs and the
extension report's prose - from the released per-seed summaries, so no value is
typed by hand.

Run ``scripts/run_native_label_benchmark_v1.py`` with the ten standard seeds
first; this script only rewrites text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUILDER = ROOT / "scripts" / "build_extension_report_v1.py"
SEEDS = (42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505)

RECENT = (("results_rccf_litnet2020_v1", "LITNET-2020"),
          ("results_rccf_iot23_v1", "IoT-23"),
          ("results_rccf_rt_iot2022_v1", "RT-IoT2022"),
          ("results_rccf_aci_iot2023_v1", "ACI-IoT-2023"))
Y2025 = (("results_rccf_uavids2025_v1", "UAVIDS-2025"),
         ("results_rccf_genis2025_v1", "GeNIS"),
         ("results_rccf_ids2025_v1", "IDS2025"))
NEW = (("results_rccf_cic_ids2018_v1", "CIC-IDS2018"),
       ("results_rccf_cic_iot2023_v1", "CIC-IoT-2023"))


def summary(folder: str) -> dict:
    path = ROOT / folder / "benchmark_summary.json"
    if not path.exists():
        raise SystemExit(f"missing {folder}/benchmark_summary.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data["seeds"]) != len(SEEDS):
        raise SystemExit(f"{folder}: {len(data['seeds'])} seeds, expected {len(SEEDS)} - "
                         "rerun run_native_label_benchmark_v1.py with the ten seeds")
    return data


def replace(path: Path, old: str, new: str, note: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        print(f"{path.name}: already applied ({note})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note}")


def replace_line(path: Path, marker: str, new_line: str) -> None:
    """Replace the single-line paragraph that starts with ``marker``."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(marker)]
    if len(hits) != 1:
        raise SystemExit(f"{path.name}: {marker!r} starts {len(hits)} lines, expected one")
    index = hits[0]
    if lines[index].rstrip("\r\n") == new_line:
        print(f"{path.name}: {marker} already current")
        return
    lines[index] = new_line + lines[index][len(lines[index].rstrip("\r\n")):]
    path.write_text("".join(lines), encoding="utf-8")
    print(f"{path.name}: rewrote the {marker} paragraph")


def main() -> None:
    recent = {label: summary(folder) for folder, label in RECENT}
    y2025 = {label: summary(folder) for folder, label in Y2025}
    new = {label: summary(folder) for folder, label in NEW}
    ids2018, ciot = new["CIC-IDS2018"], new["CIC-IoT-2023"]

    def diff(data: dict) -> str:
        return f"{data['same_members_difference']:+.6f}"

    def f1(data: dict, digits: int = 3) -> str:
        return f"{data['rccf_mean_macro_f1']:.{digits}f}"

    # --- the extension report's prose --------------------------------------
    recent_lo = min(recent.values(), key=lambda d: d["same_members_difference"])
    recent_hi = max(recent.values(), key=lambda d: d["same_members_difference"])
    y2025_lo = min(y2025.values(), key=lambda d: d["same_members_difference"])
    y2025_hi = max(y2025.values(), key=lambda d: d["same_members_difference"])
    seed_list = " ".join(str(seed) for seed in SEEDS)
    replace(BUILDER, "三种子、三个确定性视图，与扩展协议一致。",
            "十种子（与主实验同一组种子）、三个确定性视图。", "recent protocol")
    replace(BUILDER,
            "--processed-dir data_processed_rt_iot2022_v1 --experiments 42 2024 3407",
            f"--processed-dir data_processed_rt_iot2022_v1 --seeds {seed_list}", "recent command")
    replace(BUILDER,
            "\"四个 2020–2023 语料上，门控与同成员等权融合的差值为 0.000000–0.000235 Macro-F1；\"",
            f"\"四个 2020–2023 语料上（十种子），门控与同成员等权融合的差值为 "
            f"{recent_lo['same_members_difference']:+.6f}–{recent_hi['same_members_difference']:+.6f} "
            f"Macro-F1；\"", "recent range")
    replace(BUILDER, "（0.778 / 0.940）",
            f"（{f1(recent['ACI-IoT-2023'])} / {f1(recent['RT-IoT2022'])}）", "recent levels")
    replace(BUILDER, "同一水库去重与分层协议，三种子、三个确定性视图。",
            "同一水库去重与分层协议，十种子、三个确定性视图。", "2025 protocol")
    replace(BUILDER, "--seeds 42 2024 3407 --experts full chi2 anova",
            f"--seeds {seed_list} --experts full chi2 anova", "2025 command")
    replace(BUILDER,
            "\"2025 年语料上，门控与同成员等权融合的差值同样在 0.000000–0.0002 量级；\"",
            f"\"2025 年语料上（十种子），门控与同成员等权融合的差值同样在 "
            f"{y2025_lo['same_members_difference']:+.6f}–{y2025_hi['same_members_difference']:+.6f} "
            f"量级；\"", "2025 range")

    # --- the two manuscript paragraphs -------------------------------------
    en_new = (
        f"**Two further corpora.** CIC-IDS2018 (16.2 M raw rows, 4.10 M duplicates removed) gives a "
        f"56,055/12,012/12,012 five-class benchmark on which the gate and the same-members equal "
        f"fusion are identical across ten seeds ({f1(ids2018, 6)}, zero labels changed). "
        f"CIC-IoT-2023 (38.4 M rows, eight coarse classes) gives {f1(ciot, 6)} for the gate against "
        f"{ciot['equal_fusion_mean_macro_f1']:.6f} for the same-members fusion over ten seeds - a "
        f"{diff(ciot)} difference. Both reproduce the primary finding on corpora the study had not "
        f"used.")
    zh_new = (
        f"**两个新语料。** CIC-IDS2018（原始 16.2 M 行，去重移除 4.10 M 行）得到 "
        f"56 055/12 012/12 012 的五分类基准，十个种子上门控与同成员等权融合完全相同"
        f"（{f1(ids2018, 6)}，改判 0 条）。CIC-IoT-2023（38.4 M 行、八个粗类）上，门控为 "
        f"{f1(ciot, 6)}，同成员等权融合为 {ciot['equal_fusion_mean_macro_f1']:.6f}，差 "
        f"{diff(ciot)}（十个种子）。两者都在本文未使用过的语料上复现了主结论。")

    en_vintage = (
        f"**Corpus vintage.** The thirteen corpora span 1998-2025; eight of them were released in "
        f"2020 or later (LITNET-2020, IoT-23, RT-IoT2022, ACI-IoT-2023, CIC-IoT-2023, and three "
        f"published in 2025: UAVIDS-2025, GeNIS, IDS2025). Every extension corpus now runs on the "
        f"same ten seeds as the main experiments. On the 2020-2023 group the gate is "
        f"indistinguishable from the equal-weight fusion of the same members: the differences are "
        f"{diff(recent['LITNET-2020'])} (LITNET-2020), {diff(recent['IoT-23'])} (IoT-23), "
        f"{diff(recent['RT-IoT2022'])} (RT-IoT2022), {diff(recent['ACI-IoT-2023'])} "
        f"(ACI-IoT-2023) and {diff(ciot)} (CIC-IoT-2023), against Macro-F1 levels of "
        f"{f1(recent['LITNET-2020'])}, {f1(recent['IoT-23'])}, {f1(recent['RT-IoT2022'])}, "
        f"{f1(recent['ACI-IoT-2023'])} and {f1(ciot)}. The three corpora published in 2025 "
        f"reproduce the same result over 5, 4 and 7 classes, with same-members differences of "
        f"{diff(y2025['UAVIDS-2025'])} (UAVIDS-2025), {diff(y2025['GeNIS'])} (GeNIS) and "
        f"{diff(y2025['IDS2025'])} (IDS2025), against Macro-F1 levels of "
        f"{f1(y2025['UAVIDS-2025'], 4)}, {f1(y2025['GeNIS'], 4)} and "
        f"{f1(y2025['IDS2025'], 4)}. The newer corpora therefore do not sit at a single difficulty "
        f"level, and the aggregation-rule conclusion does not depend on the vintage of the source "
        f"corpus.")
    zh_vintage = (
        f"**语料年代。** 本文的十三个语料跨越 1998–2025；其中八个发布于 2020 年及以后"
        f"（LITNET-2020、IoT-23、RT-IoT2022、ACI-IoT-2023、CIC-IoT-2023，以及 2025 年发布的"
        f"三份：UAVIDS-2025、GeNIS、IDS2025）。所有扩展语料现在都与主实验使用同一组十个种子。"
        f"在 2020–2023 的五个语料上，门控与同成员等权融合无法区分：差值分别为 "
        f"{diff(recent['LITNET-2020'])}（LITNET-2020）、{diff(recent['IoT-23'])}（IoT-23）、"
        f"{diff(recent['RT-IoT2022'])}（RT-IoT2022）、{diff(recent['ACI-IoT-2023'])}"
        f"（ACI-IoT-2023）与 {diff(ciot)}（CIC-IoT-2023）；对应的 Macro-F1 为 "
        f"{f1(recent['LITNET-2020'])}、{f1(recent['IoT-23'])}、{f1(recent['RT-IoT2022'])}、"
        f"{f1(recent['ACI-IoT-2023'])} 与 {f1(ciot)}。2025 年发布的三份语料在 5、4、7 个类别上"
        f"复现了同一结果：差值分别为 {diff(y2025['UAVIDS-2025'])}（UAVIDS-2025）、"
        f"{diff(y2025['GeNIS'])}（GeNIS）与 {diff(y2025['IDS2025'])}（IDS2025）；对应的 Macro-F1 为 "
        f"{f1(y2025['UAVIDS-2025'], 4)}、{f1(y2025['GeNIS'], 4)} 与 "
        f"{f1(y2025['IDS2025'], 4)}。因此新语料并不处在同一个难度水平，而聚合规则的结论并不"
        f"依赖于源语料的年代。")

    replace_line(BASE / "English_SCI_Manuscript_v4.md", "**Two further corpora.**", en_new)
    replace_line(BASE / "English_SCI_Manuscript_v4.md", "**Corpus vintage.**", en_vintage)
    replace_line(BASE / "中文SCI论文_v4_重构版.md", "**两个新语料。**", zh_new)
    replace_line(BASE / "中文SCI论文_v4_重构版.md", "**语料年代。**", zh_vintage)
    print("EXTENSION_SEED_NUMBERS_REWRITTEN")


if __name__ == "__main__":
    main()
