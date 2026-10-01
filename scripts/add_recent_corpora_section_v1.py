"""State the corpus vintage in the manuscripts and add the recent-corpus results."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"


def summary(name: str) -> dict:
    return json.loads((ROOT / name / "benchmark_summary.json").read_text(encoding="utf-8"))


def main() -> None:
    lit = summary("results_rccf_litnet2020_v1")
    iot23 = summary("results_rccf_iot23_v1")
    rt = summary("results_rccf_rt_iot2022_v1")
    aci = summary("results_rccf_aci_iot2023_v1")
    ciciot = summary("results_rccf_cic_iot2023_v1")

    en_block = (
        "**Corpus vintage.** The ten corpora span 1998-2023, and five of them were released in 2020 "
        "or later: LITNET-2020, IoT-23 (both 2020), RT-IoT2022 (2022), ACI-IoT-2023 and "
        "CIC-IoT-2023. On each of the five the gate is indistinguishable from the equal-weight "
        "fusion of the same members: the differences are "
        f"{lit['same_members_difference']:+.6f} (LITNET-2020), "
        f"{iot23['same_members_difference']:+.6f} (IoT-23), "
        f"{rt['same_members_difference']:+.6f} (RT-IoT2022), "
        f"{aci['same_members_difference']:+.6f} (ACI-IoT-2023) and "
        f"{ciciot['same_members_difference']:+.6f} (CIC-IoT-2023), against Macro-F1 levels of "
        f"{lit['rccf_mean_macro_f1']:.3f}, {iot23['rccf_mean_macro_f1']:.3f}, "
        f"{rt['rccf_mean_macro_f1']:.3f}, {aci['rccf_mean_macro_f1']:.3f} and "
        f"{ciciot['rccf_mean_macro_f1']:.3f}. The 2020-2023 corpora are therefore not only newer "
        "but also more difficult than the 2017 data, and the aggregation-rule conclusion does not "
        "depend on the vintage of the source corpus. Corpora released in 2024-2025 are distributed "
        "behind request forms; the preparation and evaluation scripts are released so they can be "
        "added under the same protocol.\n\n")
    zh_block = (
        "**语料年代。** 本文的十个语料跨越 1998–2023，其中五个发布于 2020 年及以后："
        "LITNET-2020、IoT-23（均 2020）、RT-IoT2022（2022）、ACI-IoT-2023 与 CIC-IoT-2023。"
        "在这五个语料上，门控与同成员等权融合无法区分：差值分别为 "
        f"{lit['same_members_difference']:+.6f}（LITNET-2020）、"
        f"{iot23['same_members_difference']:+.6f}（IoT-23）、"
        f"{rt['same_members_difference']:+.6f}（RT-IoT2022）、"
        f"{aci['same_members_difference']:+.6f}（ACI-IoT-2023）与 "
        f"{ciciot['same_members_difference']:+.6f}（CIC-IoT-2023）；对应的 Macro-F1 为 "
        f"{lit['rccf_mean_macro_f1']:.3f}、{iot23['rccf_mean_macro_f1']:.3f}、"
        f"{rt['rccf_mean_macro_f1']:.3f}、{aci['rccf_mean_macro_f1']:.3f} 与 "
        f"{ciciot['rccf_mean_macro_f1']:.3f}。因此新语料不仅年代更近，判别难度也更高，"
        "而聚合规则的结论并不依赖于源语料的年代。2024–2025 年发布的语料多需申请获取；"
        "本文公开全部处理与评估脚本，可在同一协议下继续补充。\n\n")

    for path, block, anchor in ((EN, en_block, "## 6. Discussion"), (ZH, zh_block, "## 6 讨论")):
        text = path.read_text(encoding="utf-8")
        if "Corpus vintage" in text or "语料年代" in text:
            print(f"{path.name}: vintage paragraph already present")
            continue
        if anchor not in text:
            raise SystemExit(f"{path.name}: anchor {anchor!r} missing")
        text = text.replace(anchor, block + anchor, 1)
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: inserted the vintage paragraph")

    # the limitation sentence counts the corpora
    pairs = ((EN, "**Six datasets were evaluated", "**Ten corpora were evaluated"),
             (ZH, "本文评估的六个语料都不代表生产流量", "本文评估的十个语料都不代表生产流量"))
    for path, old, new in pairs:
        text = path.read_text(encoding="utf-8")
        if old in text:
            text = text.replace(old, new, 1)
            path.write_text(text, encoding="utf-8")
            print(f"{path.name}: corpus count updated")
        else:
            print(f"{path.name}: corpus-count anchor not found (already updated?)")
    print("RECENT_CORPORA_SECTION_ADDED")


if __name__ == "__main__":
    main()
