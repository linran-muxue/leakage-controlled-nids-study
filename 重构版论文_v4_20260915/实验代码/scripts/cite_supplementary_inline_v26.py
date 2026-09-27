"""Cite every supplementary item from the section where its content is used.
JISA requires each supplementary file to be referenced in the text; the items
were previously listed only in the closing table, so nothing pointed at them
from the body. One sentence is appended to each of the seven subsections plus
the reference note, covering S01-S26 exactly once between them.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
TARGETS_EN = [
    ("### 4.1", "Per-file processing counts, class support and the training-side feature scores of all "
                "four views are provided in Supplementary S01-S04."),
    ("### 4.3", "The row-wise margin bound and the quantification of Condition 3 are provided in "
                "Supplementary S17 and S25."),
    ("### 5.2", "Per-seed metrics, per-class reports, normalised confusion matrices and the equivalence "
                "tests are provided in Supplementary S05-S07 and S20."),
    ("### 5.3", "The gate search, the row-wise weight records and the expert-diversity suite are provided "
                "in Supplementary S08-S09, S16 and S18."),
    ("### 5.4", "The protocol-sensitivity runs and the nested cross-validation fold metrics are provided "
                "in Supplementary S10-S11."),
    ("### 5.5", "The external benchmarks, the file-level extrapolation and the neural baseline comparison "
                "are provided in Supplementary S12-S14 and S19."),
    ("### 5.6", "Calibration, robustness, latency, resource, cost-sensitive and near-duplicate results are "
                "provided in Supplementary S15 and S21-S23, S26."),
]
TARGETS_ZH = [
    ("### 4.1", "逐原始文件处理计数、类别支持数与四种特征视图的训练侧特征得分见补充材料 S01–S04。"),
    ("### 4.3", "逐行边距上界与命题 3 的定量验证见补充材料 S17 与 S25。"),
    ("### 5.2", "逐种子指标、逐类别报告、归一化混淆矩阵与等价性检验见补充材料 S05–S07 与 S20。"),
    ("### 5.3", "门控搜索、逐行权重记录与专家多样性实验见补充材料 S08–S09、S16 与 S18。"),
    ("### 5.4", "协议敏感性实验与嵌套交叉验证逐折指标见补充材料 S10–S11。"),
    ("### 5.5", "外部数据集基准、文件级外推与神经基线对照见补充材料 S12–S14 与 S19。"),
    ("### 5.6", "校准、鲁棒性、延迟、资源、代价敏感与近重复结果见补充材料 S15 与 S21–S23、S26。"),
]
REF_NOTE = {
    "English_SCI_Manuscript_v4.md": ("## References", "## References", "\n\nThe individual checks are recorded in Supplementary S24.\n"),
    "中文SCI论文_v4_重构版.md": ("## 参考文献", "## 参考文献", "\n\n逐条核验记录见补充材料 S24。\n"),
}
def append_to_section(lines: list[str], heading: str, sentence: str) -> bool:
    for i, line in enumerate(lines):
        if line.startswith(heading):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#"):
                j += 1
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            lines.insert(j, "")
            lines.insert(j + 1, sentence)
            return True
    return False
def main() -> None:
    for name, targets, marker in (("English_SCI_Manuscript_v4.md", TARGETS_EN, "Supplementary S"),
                                  ("中文SCI论文_v4_重构版.md", TARGETS_ZH, "补充材料 S")):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        if text.count(marker) > 30:
            print(f"{name}: already cited inline")
            continue
        lines = text.splitlines()
        added = 0
        for heading, sentence in targets:
            added += 1 if append_to_section(lines, heading, sentence) else 0
        text = "\n".join(lines)
        heading, anchor, note = REF_NOTE[name]
        note_line = [l for l in text.splitlines() if "verified against Crossref" in l or "通过 Crossref" in l]
        if note_line and "Supplementary S24" not in text and "补充材料 S24" not in text:
            text = text.replace(note_line[0], note_line[0].rstrip() + note.strip(), 1)
            added += 1
        path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        print(f"{name}: {added} supplementary references inserted")
if __name__ == "__main__":
    main()
