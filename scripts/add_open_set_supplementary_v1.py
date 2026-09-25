"""Give the open-set diagnostics their own supplementary item (S30).

Section 5.6 reports the study's most adverse result - the conditional branch
reaches 0.643-0.694 AUROC against 0.919-0.948 for the equal-weight forest - and
none of the 29 supplementary items contained it: S15 covers calibration,
robustness and latency, S18 the diversity suite, S20 the ten-seed run.  A
reviewer could not check the open-set numbers from the bundle at all, which is
how the range came to quote two of three seeds for three review rounds.

S30 ships the released, verified open-set metrics (three seeds x uncalibrated,
temperature-scaled and conformal exports for both arms) and the
family-combination matrix that Section 6.5 refers to when it says the results
are reported per family.  The four endpoints Section 5.6 prints are asserted
here before the item is registered.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
PY = sys.executable

SOURCES = [
    "results_cfrg_open_set_v5_verified/open_set_metrics.csv",
    "results_open_set_matrix_v2/open_set_matrix_metrics.csv",
]

ITEM = ('    # Section 5.6 reports an open-set range that no earlier item carried:\n'
        '    # S15 covers calibration, robustness and latency only.\n'
        '    "S30": ("开放集诊断：三个留出未知族、逐种子与逐家族组合敏感性",\n'
        '            ["results_cfrg_open_set_v5_verified/open_set_metrics.csv",\n'
        '             "results_open_set_matrix_v2/open_set_matrix_metrics.csv"]),\n')
S29_TAIL = '             "results_rccf_cic_natural_v4_full/metrics_by_seed.csv"]),\n'

EDITS = {
    "English_SCI_Manuscript_v4.md": (
        ("| S29 | Full-corpus run: 2,429,503 flows, per-seed metrics and paired comparison |",
         "| S29 | Full-corpus run: 2,429,503 flows, per-seed metrics and paired comparison |\n"
         "| S30 | Open-set diagnostics: three held-out unknown families, per seed and per "
         "probability export |",
         "supplementary index"),
        ("the uncalibrated and temperature-scaled probability exports.",
         "the uncalibrated and temperature-scaled probability exports (Supplementary S30).",
         "Section 5.6 open-set citation"),
        ("so only per-family results are reported and no pooled open-set conclusion is drawn.",
         "so only per-family results are reported and no pooled open-set conclusion is drawn; "
         "the family-combination matrix is in Supplementary S30.",
         "Section 6.5 open-set citation"),
    ),
    "中文SCI论文_v4_重构版.md": (
        ("| S29 | 全语料运行：2 429 503 条、逐种子指标与配对比较 |",
         "| S29 | 全语料运行：2 429 503 条、逐种子指标与配对比较 |\n"
         "| S30 | 开放集诊断：三个留出未知族、逐种子与逐概率导出 |",
         "补充材料清单"),
        ("（区间覆盖三个已发布种子，以及未校准与温度缩放两种概率导出）",
         "（区间覆盖三个已发布种子，以及未校准与温度缩放两种概率导出；逐种子数值见补充材料 S30）",
         "第 5.6 节开放集引用"),
        ("本文只报告分族结果，不给出合并结论。",
         "本文只报告分族结果，不给出合并结论；各家族组合的矩阵见补充材料 S30。",
         "第 6.5 节开放集引用"),
    ),
}


def assert_sources() -> None:
    metrics = pd.read_csv(ROOT / SOURCES[0])
    conditional = metrics[metrics.model.isin(("cfrg_forest", "cfrg_forest_temperature_scaled"))]
    equal = metrics[metrics.model.isin(("equal_rf", "equal_rf_temperature_scaled"))]
    if len(metrics) != 18 or len(conditional) != 6 or len(equal) != 6:
        raise SystemExit(f"unexpected shape: {len(metrics)} rows")
    for label, value, source in (
            ("conditional AUROC low", 0.643513, conditional.auroc.min()),
            ("conditional AUROC high", 0.693891, conditional.auroc.max()),
            ("conditional recall low", 0.001466, conditional.unknown_recall.min()),
            ("conditional recall high", 0.039570, conditional.unknown_recall.max()),
            ("equal AUROC low", 0.919140, equal.auroc.min()),
            ("equal AUROC high", 0.947932, equal.auroc.max()),
            ("equal recall low", 0.056668, equal.unknown_recall.min()),
            ("equal recall high", 0.373718, equal.unknown_recall.max())):
        if abs(float(source) - value) > 5e-7:
            raise SystemExit(f"{label}: {source} != {value}")
        print(f"  source {label:<24}{float(source):.6f}")
    matrix = pd.read_csv(ROOT / SOURCES[1])
    if len(matrix) != 7:
        raise SystemExit(f"family-combination matrix changed: {len(matrix)} rows")
    print(f"  source family-combination matrix: {len(matrix)} combinations, "
          f"AUROC {matrix.unknown_auroc.min():.4f}-{matrix.unknown_auroc.max():.4f}")


def register() -> None:
    path = SCRIPTS / "assemble_supplementary_v5.py"
    text = path.read_text(encoding="utf-8")
    if '"S30"' in text:
        print("assembler: S30 already registered")
        return
    if text.count(S29_TAIL) != 1:
        raise SystemExit("S29 entry tail not found; cannot place S30 in order")
    path.write_text(text.replace(S29_TAIL, S29_TAIL + ITEM, 1), encoding="utf-8")
    print("assembler: S30 registered")


def edit_manuscripts() -> None:
    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        for old, new, label in edits:
            if old in text:
                if text.count(old) != 1:
                    raise SystemExit(f"{label}: anchor not unique in {name}")
                text = text.replace(old, new, 1)
            elif new not in text:
                raise SystemExit(f"{label}: neither the old nor the new text is present in {name}")
        path.write_text(text, encoding="utf-8")
        print(f"updated {name}")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if "`S01-S29`" in text:
        readme.write_text(text.replace("`S01-S29`", "`S01-S30`", 1), encoding="utf-8")
        print("updated README.md")


def rebuild_bundle() -> tuple[int, int]:
    assembler = importlib.import_module("assemble_supplementary_v5")
    assembler.main()
    current = assembler.OUT
    for stale in BASE.glob("补充材料_S01_S*"):
        if stale.resolve() == current.resolve():
            continue
        if not str(stale.resolve()).startswith(str(BASE.resolve())):
            raise SystemExit(f"refusing to remove {stale}")
        shutil.rmtree(stale)
        print(f"removed the superseded bundle {stale.name}")
    subprocess.run([PY, str(SCRIPTS / "sync_supplementary_mirror_v16.py")], cwd=ROOT, check=True)
    items = len([d for d in current.iterdir() if d.is_dir()])
    files = [f for f in current.rglob("*") if f.is_file() and f.parent != current]
    return items, len(files)


def update_selfcheck(items: int, files: int) -> None:
    path = BASE / "论文自查表.md"
    text = path.read_text(encoding="utf-8")
    old_prefix = "| F4 | 补充材料 | 与清单一致且存在 | **通过** | `补充材料_"
    if old_prefix not in text:
        raise SystemExit("F4 row not found in the self-check table")
    start = text.index(old_prefix)
    end = text.index("\n", start)
    old_row = text[start:end]
    new_row = (f"| F4 | 补充材料 | 与清单一致且存在 | **通过** | "
               f"`补充材料_S01_S{items:02d}/`：{items} 条目、{files} 个材料文件，"
               f"另含 `README.md` 索引与 `checksums.sha256` 校验")
    if old_row != new_row:
        path.write_text(text.replace(old_row, new_row, 1), encoding="utf-8")
        print(f"self-check F4: {items} items, {files} material files")


def main() -> None:
    assert_sources()
    register()
    edit_manuscripts()
    items, files = rebuild_bundle()
    update_selfcheck(items, files)
    for name, needles in (("English_SCI_Manuscript_v4.md",
                           ("Supplementary S30", "| S30 |")),
                          ("中文SCI论文_v4_重构版.md",
                           ("补充材料 S30", "| S30 |"))):
        text = (BASE / name).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"{name} does not cite {needle}")
    print("OPEN_SET_SUPPLEMENTARY_ADDED")


if __name__ == "__main__":
    main()
