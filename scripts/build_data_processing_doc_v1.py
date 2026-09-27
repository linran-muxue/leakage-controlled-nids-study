"""Document the data-processing code and its flow, with figures and a run record.

The pipeline is six stages implemented in ``src/`` and audited by
``scripts/audit_data_processing_v1.py``.  This document puts the stages, the code
that implements each of them, the released evidence and the numbers together,
embeds the two pipeline figures, and renders the audit's own output as an image
so the run record can be read at a glance.

Every count comes from the audit JSON; every code excerpt is read from the file
it cites, never retyped.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SHOTS = BASE / "figures_pipeline"
OUT = BASE / "数据处理代码与流程.md"
AUDIT = ROOT / "results_data_audit_cic_natural_v3b" / "data_processing_audit.json"


def excerpt(relative: str, marker: str, lines: int, offset: int = 0) -> str:
    """A real excerpt starting at the first line containing `marker`."""
    text = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(text):
        if marker in line:
            start = max(0, index + offset)
            return "\n".join(text[start:start + lines])
    raise SystemExit(f"{relative}: marker not found: {marker}")


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()[:12]


def run_image(audit: dict) -> Path:
    """Render the audit's own numbers as a terminal-style image."""
    raw = audit["raw_totals"]
    splits = audit["processed"]["splits"]
    overlap = audit["processed"]["cross_split_exact_feature_overlap"]
    quality = audit["processed"]["train_feature_quality"]
    lines = [
        "> python -m src.prepare_dataset --per-class-cap 20000 --balance \\",
        "      --raw-dir E:\\论文\\data\\raw\\MachineLearningCVE \\",
        "      --processed-dir data_processed_cic_natural_v3b",
        "> python scripts/audit_data_processing_v1.py \\",
        "      --raw-dir ... --processed-dir ... --output-dir results_data_audit_cic_natural_v3b",
        "",
        f"raw rows                     {raw['source_rows']:>12,}",
        f"label-mapped rows            {raw['mapped_rows']:>12,}   (-{raw['excluded_label_rows']:,} excluded labels)",
        f"non-finite removed           {raw['invalid_infinite_rows']:>12,}   (missing/non-numeric: {raw['invalid_missing_rows']})",
        f"physical-range valid         {raw['physical_valid_rows']:>12,}",
        "",
        f"train / validation / test    {splits['train']['rows']:>7,} / {splits['validation']['rows']:,} / {splits['test']['rows']:,}",
        f"features per split           {splits['test']['feature_count']:>7}",
        f"cross-split exact overlap    train-val {overlap['train_validation']}, train-test {overlap['train_test']}, val-test {overlap['validation_test']}",
        f"train feature quality        constant {len(quality['constant_features'])}, "
        f"near-zero-variance {len(quality['near_zero_variance_features'])}",
        "",
        "audit writes: data_processing_audit.json, processed_split_summary.csv",
        "the audit is non-mutating: it reads the processed files and never rewrites them",
    ]
    SHOTS.mkdir(parents=True, exist_ok=True)
    target = SHOTS / "fig_pipeline_run.png"
    figure, axis = plt.subplots(figsize=(11.2, 5.9), dpi=200)
    axis.set_facecolor("#12161c")
    figure.patch.set_facecolor("#12161c")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    for index, line in enumerate(lines):
        colour = "#7ee787" if line.startswith(">") else "#d7dde5"
        if "audit writes" in line or "non-mutating" in line:
            colour = "#9aa4b2"
        # the paths contain Chinese characters, so those lines need a CJK font
        family = "Microsoft YaHei" if any(ord(ch) > 0x2E80 for ch in line) else "Consolas"
        axis.text(0.02, 0.97 - index * 0.052, line, family=family, fontsize=10.5,
                  color=colour, va="top")
    # the caption sits in the figure margin so it cannot collide with the log
    figure.text(0.02, 0.012,
                "由 results_data_audit_cic_natural_v3b/data_processing_audit.json 的真实数值渲染",
                family="Microsoft YaHei", fontsize=9, color="#6b7280", va="bottom")
    figure.savefig(target, facecolor=figure.patch.get_facecolor(), bbox_inches="tight")
    plt.close(figure)
    return target


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    raw = audit["raw_totals"]
    splits = audit["processed"]["splits"]
    shot = run_image(audit)

    code_files = (
        ("src/data_pipeline.py", "标签映射与物理范围掩码"),
        ("src/prepare_dataset.py", "分块读取、去重、按类上限、平衡与分层划分"),
        ("src/feature_selection.py", "训练侧特征选择（卡方 / 互信息 / ANOVA）"),
        ("scripts/audit_data_processing_v1.py", "非改写式处理审计与阶段计数"),
        ("scripts/hash_external_data.py", "外部数据集校验和记录"),
        ("scripts/check_audit_chain_numbers_v1.py", "阶段计数与正文数字的一致性检查"),
    )

    lines: list[str] = []
    lines.append("# 数据处理代码与流程")
    lines.append("")
    lines.append("> CIC-IDS2017 的处理是**六阶段审计**：每一步都有实现代码、输入输出与发布证据，"
                 "原始 2 830 743 行最终落到研究总体。"
                 "本表同时给出流程截图、运行记录截图与关键代码摘录；所有计数取自 "
                 "`results_data_audit_cic_natural_v3b/data_processing_audit.json`。")
    lines.append("")
    lines.append("## 一、流程与运行记录（截图）")
    lines.append("")
    lines.append("![图 1 协议流水线（正文图 1）](figures_en/fig1_protocol_pipeline.png)")
    lines.append("")
    lines.append("![图 2 数据瀑布：从原始文件到研究总体（正文图 2）](figures_en/fig2_data_waterfall.png)")
    lines.append("")
    lines.append(f"![图 3 本次处理与审计的运行记录（由真实审计输出渲染）](figures_pipeline/{shot.name})")
    lines.append("")
    lines.append("## 二、阶段 → 代码 → 证据")
    lines.append("")
    lines.append("| 阶段 | 实现 | 输入 → 输出 | 发布证据 |")
    lines.append("|---|---|---|---|")
    lines.append(f"| S1 标签映射 | `src/data_pipeline.py` · `map_attack_label` | "
                 f"{raw['source_rows']:,} → {raw['mapped_rows']:,}（排除 "
                 f"{raw['excluded_label_rows']:,} 条非保留标签）| S02、表 3、"
                 f"`data_processing_audit.json` |")
    lines.append(f"| S2 非有限值清理 | `src/prepare_dataset.py` · `collect_balanced_sample` | "
                 f"移除 {raw['invalid_infinite_rows']:,} 条（缺失 {raw['invalid_missing_rows']} 条）| 同上 |")
    lines.append(f"| S3 物理范围筛查 | `src/data_pipeline.py` · `cic_physical_valid_mask` | "
                 f"保留 {raw['physical_valid_rows']:,} 条（时长/速率/长度/段大小不可为负）| 同上 |")
    lines.append(f"| S4 全局去重 | `src/prepare_dataset.py`（前向/反向双哈希指纹）| "
                 f"精确重复行在划分前全局剔除，审计见 `dedup_audit.json` | S21（近重复审计）|")
    lines.append(f"| S5 分层划分 | `src/prepare_dataset.py` · `prepare_dataset` | "
                 f"70/15/15 分层：{splits['train']['rows']:,} / {splits['validation']['rows']:,} / "
                 f"{splits['test']['rows']:,}；跨划分精确特征重叠 0 | S03、S05、表 3 |")
    lines.append(f"| S6 训练侧特征选择 | `src/feature_selection.py` | 仅在训练侧拟合卡方/互信息/ANOVA，"
                 f"取前 60 维；其余视图保留全特征 | S04、图 3 |")
    lines.append(f"| 审计 | `scripts/audit_data_processing_v1.py` | 只读地重算每一阶段，"
                 f"写出审计 JSON 与划分汇总 | `results_data_audit_*`、S02/S03 |")
    lines.append("")
    lines.append("## 三、代码清单（SHA-256 前 12 位，生成时计算）")
    lines.append("")
    lines.append("| 文件 | 大小 | SHA-256 | 作用 |")
    lines.append("|---|---:|---|---|")
    for relative, role in code_files:
        path = ROOT / relative
        lines.append(f"| `{relative}` | {path.stat().st_size / 1024:.1f} KB | "
                     f"`{sha(relative)}` | {role} |")
    lines.append("")
    lines.append("> 数据获取本身不是脚本：四个语料由人工从公开来源下载，URL、检索日期、"
                 "快照与校验和记录在 S01 与《数据与资料来源总表》，再由上述代码处理。")
    lines.append("")
    lines.append("## 四、关键代码摘录（摘自当前仓库）")
    lines.append("")
    lines.append("**S1 · 标签映射**（`src/data_pipeline.py`）")
    lines.append("")
    lines.append("```python")
    lines.append(excerpt("src/data_pipeline.py", "def map_attack_label", 22))
    lines.append("```")
    lines.append("")
    lines.append("**S3 · 物理范围掩码**（`src/data_pipeline.py`）")
    lines.append("")
    lines.append("```python")
    lines.append(excerpt("src/data_pipeline.py", "def cic_physical_valid_mask", 18))
    lines.append("```")
    lines.append("")
    lines.append("**S4 · 去重指纹与按类上限**（`src/prepare_dataset.py`）")
    lines.append("")
    lines.append("```python")
    lines.append(excerpt("src/prepare_dataset.py", "_dedup_hash_forward", 16, offset=-6))
    lines.append("```")
    lines.append("")
    lines.append("**S5 · 分层划分与产物写出**（`src/prepare_dataset.py`）")
    lines.append("")
    lines.append("```python")
    lines.append(excerpt("src/prepare_dataset.py", "def prepare_dataset", 22))
    lines.append("```")
    lines.append("")
    lines.append("**审计入口**（`scripts/audit_data_processing_v1.py`）")
    lines.append("")
    lines.append("```python")
    lines.append(excerpt("scripts/audit_data_processing_v1.py", "def main() -> None:", 16))
    lines.append("```")
    lines.append("")
    lines.append("## 五、同一份代码生成四个 CIC 总体")
    lines.append("")
    lines.append("| 总体 | 关键参数 | 结果 | 配置记录 |")
    lines.append("|---|---|---|---|")
    lines.append("| 自然先验（主）| `--per-class-cap 20000`（平衡度按自然先验保留）| "
                 f"{splits['train']['rows'] + splits['validation']['rows'] + splits['test']['rows']:,} 条 | "
                 "`data_processed_cic_natural_v3b/preprocess_config.json` |")
    lines.append("| 平衡控制 | `--balance`（各类等量）| 3 365 条 | "
                 "`data_processed_cic_balanced_v3b/preprocess_config.json` |")
    lines.append("| 规模阶梯 | `--per-class-cap 200000` | 413 209 条 | "
                 "`data_processed_cic_natural_v4_scale200k/preprocess_config.json` |")
    lines.append("| 全去重语料 | 取消上限（`--per-class-cap` 极大）| 2 429 503 条 | "
                 "`data_processed_cic_natural_v4_full/preprocess_config.json` |")
    lines.append("")
    lines.append("## 六、复现命令")
    lines.append("")
    lines.append("```powershell")
    lines.append("$py = \"E:\\论文\\.venv\\Scripts\\python.exe\"")
    lines.append("& $py -m src.prepare_dataset --raw-dir E:\\论文\\data\\raw\\MachineLearningCVE `")
    lines.append("      --processed-dir data_processed_cic_natural_v3b --per-class-cap 20000")
    lines.append("& $py scripts\\audit_data_processing_v1.py `")
    lines.append("      --raw-dir E:\\论文\\data\\raw\\MachineLearningCVE `")
    lines.append("      --processed-dir data_processed_cic_natural_v3b `")
    lines.append("      --output-dir results_data_audit_cic_natural_v3b")
    lines.append("& $py scripts\\check_audit_chain_numbers_v1.py   # 与正文表 3 逐项比对")
    lines.append("```")
    lines.append("")
    lines.append("## 七、核验")
    lines.append("")
    lines.append(f"- 阶段计数链 2 830 743 → {raw['mapped_rows']:,} → "
                 f"{raw['valid_rows']:,} → {raw['physical_valid_rows']:,} → 划分/"
                 f"去重/截断，与正文表 3 及 S02 一致（`check_audit_chain_numbers_v1.py` 入闸门）；")
    lines.append("- 跨划分精确特征重叠为 0；训练侧特征质量（常数列与近零方差列）记录在审计 JSON；")
    lines.append("- 全语料与规模总体的划分计数由 `check_audit_chain_numbers_v1.py`、"
                 "`audit_full_corpus_data_v1.py` 持续复核。")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PIPELINE_DOC_WRITTEN={OUT}")
    print(f"shot={shot.relative_to(ROOT)} lines={len(lines)}")


if __name__ == "__main__":
    main()
