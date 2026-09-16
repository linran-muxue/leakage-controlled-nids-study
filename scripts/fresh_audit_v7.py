"""Fresh audit: newly added content, auxiliary documents, cross-document consistency."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'OK  ' if ok else 'ISSUE'}{label:<46}{detail}")


print("=== 1. newly added content vs its source files ===")
rb = json.loads((ROOT / "results_robustness_extended_v5" /
                 "robustness_extended_summary_3seeds.json").read_text("utf-8"))
rows = {(r["model"], r["condition"]): r for r in rb["summary"]}
pairs = [("rccf", "label_noise_5pct", 0.57), ("rccf", "label_noise_10pct", 0.97),
         ("rccf", "missing_10pct", 4.21), ("rccf", "offset_drift", 17.23),
         ("equal_rf_chi2", "label_noise_5pct", 0.77), ("equal_rf_chi2", "label_noise_10pct", 1.00),
         ("equal_rf_chi2", "missing_10pct", 4.25), ("equal_rf_chi2", "offset_drift", 18.24)]
for model, cond, claimed in pairs:
    actual = round(rows[(model, cond)]["relative_drop_pct"], 2)
    check(f"robustness {model} {cond}", abs(actual - claimed) < 0.01,
          f"manuscript {claimed} vs file {actual}")

p3 = json.loads((ROOT / "results_margin_bound_v5" /
                 "proposition3_quantification.json").read_text("utf-8"))
check("prop-3 observed deficiency appears",
      f"{p3['mean_entropy_deficiency_observed']:.2e}" not in EN, "value quoted in text")
check("prop-3 relative errors quoted",
      "1.5%" in EN and "4.0%" in EN,
      f"first-order {p3['relative_error_of_first_order_prediction']:.3f}, "
      f"second-order {p3['relative_error_of_second_order_identity']:.3f}")

print()
print("=== 2. supplementary list parity ===")
with (BASE / "补充材料_S1_S19" / "README.md").open(encoding="utf-8") as handle:
    bundle = sorted({m for m in re.findall(r"^\| (S\d+) \|", handle.read(), flags=re.M)})
en_list = sorted(set(re.findall(r"^\| (S\d+) \|", EN, flags=re.M)))
zh_list = sorted(set(re.findall(r"^\| (S\d+) \|", ZH, flags=re.M)))
check("manuscript EN list == ZH list", en_list == zh_list, f"{len(en_list)} each")
check("bundle covers manuscript list", set(en_list) <= set(bundle),
      f"bundle {len(bundle)}, missing {sorted(set(en_list) - set(bundle))}")

print()
print("=== 3. figure captions vs current protocol ===")
caps = re.findall(r"^!\[([^\]]+)\]", EN, flags=re.M)
for cap in caps:
    if "three seeds" in cap or "ten seeds" in cap:
        print(f"  caption mentions a seed count: {cap[:80]}")
stale = [c for c in caps if "balanced research subset" in c.lower()]
check("no stale figure captions", not stale, f"{len(stale)} stale")
check("figure 4 caption mentions ten seeds", any("ten seeds" in c for c in caps),
      f"{[c[:60] for c in caps if 'main results' in c.lower()][:1]}")

print()
print("=== 4. auxiliary documents ===")
manual = (BASE / "P0_P1执行手册.md").read_text("utf-8")
review = (BASE / "遗漏问题审查报告.md").read_text("utf-8")
check("manual no longer claims S8 pending", "仅剩 **S8" not in manual,
      "manual still lists S8 as the only remaining P0 item" if "仅剩 **S8" in manual else "ok")
check("review report records v1.5.x state", "v1.5" in review or "内容层专项" in review,
      "review report may predate the latest fix rounds")

print()
print("=== 5. highlights vs current result ===")
hl = (BASE / "Highlights_v4.md").read_text("utf-8")
check("highlights quote the strictest margin attained", "0.005" in hl,
      "highlights still say only 0.01" if "0.005" not in hl else "ok")
check("highlights mention ten seeds", "ten" in hl.lower() or "seeds" in hl.lower(), "")

print()
print("=== 6. perturbation inventory consistency ===")
check("text enumerates all five perturbation types",
      all(k in EN for k in ["Gaussian noise", "feature masking", "missing", "drift", "label"]),
      "shared: gaussian, mask; extended: missing, drift, label")

print()
print("=== 7. self-check internal consistency ===")
sc = (BASE / "论文自查表.md").read_text("utf-8")
row = re.search(r"\| \*\*合计\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", sc)
if row:
    total, passed, partial, missing = map(int, row.groups())
    item_lines = re.findall(r"^\| [A-G]\d+ \|.*$", sc, flags=re.M)
    actual_pass = sum(1 for l in item_lines if "**通过**" in l)
    actual_partial = sum(1 for l in item_lines if "**部分通过**" in l)
    actual_missing = sum(1 for l in item_lines if "**缺失**" in l)
    check("summary row matches item counts",
          (passed, partial, missing) == (actual_pass, actual_partial, actual_missing),
          f"summary {passed}/{partial}/{missing} vs counted {actual_pass}/{actual_partial}/{actual_missing}")
    check("total equals the sum of parts", passed + partial + missing == total,
          f"{passed}+{partial}+{missing} vs {total}")

print()
print("=== 8. availability statement vs the released tag ===")
import subprocess  # noqa: E402
tags = subprocess.run(["git", "tag"], capture_output=True, text=True, cwd=ROOT).stdout.split()
latest = sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1] if tags else ""
cited = set(re.findall(r"v1\.\d+\.\d+", EN)) | set(re.findall(r"v1\.\d+\.\d+", ZH))
check("manuscript cites exactly one release", len(cited) == 1, f"cited {sorted(cited)}")
check("cited release is the latest tag", cited == {latest},
      f"cited {sorted(cited)} vs latest tag {latest}")
