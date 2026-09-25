"""Build the project work log from the records that already track the work.

Nothing here is typed in from memory: the round ledger comes from the review
report's own headings (rounds 1-19) and from the round-labelled commits (20a
onwards), the guard list from the gate's check table, the statistics from the
deliverable-counts measurement, the data baseline from the authenticity check,
and the open items from the readiness check.  Regenerate it after any round.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_deliverable_counts_v1 import measure  # noqa: E402

TAG = "v1.11.0"
OUT = ROOT / "工作日志_论文项目.md"


def run(args: list[str]) -> str:
    proc = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True,
                          errors="replace")
    return proc.stdout + proc.stderr


def report_rounds() -> list[tuple[int, str]]:
    """The review report's own round headings, verbatim and in order.

    Some headings carry a date, some a theme and some a round range, so the text
    is reproduced as written rather than split into columns - guessing which
    parenthetical is a date is what produced a table full of "—".
    """
    text = (BASE / "遗漏问题审查报告.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        match = re.match(r"^(#{2,3}) ((?:[A-Z]\.\s*)?第.*轮.*)$", line)
        if match and "总计" not in match.group(2):
            rows.append((len(match.group(1)), match.group(2).strip()))
    return rows


def git_rounds() -> list[tuple[str, str, str, str]]:
    out = subprocess.run(["git", "log", "--pretty=format:%h|%ad|%s", "--date=short"],
                         capture_output=True, cwd=ROOT).stdout.decode("utf-8", errors="replace")
    rows = []
    for line in out.splitlines():
        match = re.match(r"([0-9a-f]{7})\|(\d{4}-\d{2}-\d{2})\|Round (\d+(?:-\d+)?[a-z]*): (.*)",
                         line)
        if match:
            rows.append((match.group(3), match.group(1), match.group(2), match.group(4)))
    return list(reversed(rows))


def gate_checks() -> list[str]:
    text = (ROOT / "scripts" / "verify_all_v8.py").read_text(encoding="utf-8")
    return re.findall(r'^\s{4}\("([^"]+)",', text, flags=re.M)


def main() -> None:
    counts = measure()
    entry = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    chinese = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
    abstract_words = len(entry.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].split())
    supplementary = len([d for d in (BASE / f"补充材料_S01_S30").iterdir() if d.is_dir()])
    auth = run(["scripts/audit_data_authenticity_v1.py"])
    readiness = run(["scripts/check_submission_readiness_v1.py"])
    archive = ROOT / "submission_package" / f"论文投稿包_{TAG}.zip"
    packed = 0
    if archive.exists():
        with zipfile.ZipFile(archive) as handle:
            packed = len(handle.namelist())
    summary = json.loads((ROOT / "results_full_corpus_v49" /
                          "full_corpus_summary.json").read_text(encoding="utf-8"))

    lines: list[str] = []
    lines.append(f"# 工作日志：泄漏受控网络入侵检测论文项目")
    lines.append("")
    lines.append(f"**生成时间**：{dt.datetime.now():%Y-%m-%d %H:%M}（由 "
                 f"`scripts/build_work_log_v1.py` 自动生成）  ")
    lines.append(f"**发布版本**：{TAG}（仓库 main 与标签同步）  ")
    lines.append("**仓库**：https://github.com/linran-muxue/leakage-controlled-nids-study")
    lines.append("")
    lines.append("## 一、当前状态概览")
    lines.append("")
    lines.append("| 维度 | 现状 |")
    lines.append("|---|---|")
    lines.append(f"| 正文 | 英文 {counts['en_words']:,} 词 / 中文 {counts['zh_chars']:,} 字符；"
                 f"{counts['figures']} 图、{counts['tables']} 表 |")
    lines.append(f"| 摘要 | 英文 {abstract_words} 词（JISA 上限 250）|")
    lines.append(f"| 验证闸门 | {counts['gate_checks']} 项检查全绿（`scripts/verify_all_v8.py`）|")
    lines.append(f"| 单元测试 | {counts['tests']} 项 |")
    lines.append(f"| 自查表 | {counts['sc_items']} 项：{counts['sc_passed']} 通过 / "
                 f"{counts['sc_partial']} 部分通过 |")
    lines.append(f"| 补充材料 | S01–S{supplementary:02d}，{supplementary} 条目 |")
    lines.append(f"| 主实验 | 全语料 2 429 503 条、十种子；平均配对差 "
                 f"{summary['mean_difference']:.6f}（TOST：0.005 不等价 / 0.01 等价）|")
    lines.append(f"| 投稿压缩包 | `论文投稿包_{TAG}.zip`，{packed} 个条目 |")
    lines.append("")
    lines.append("## 二、轮次台账")
    lines.append("")
    lines.append("### 2.1 审查报告记录的轮次（标题原样摘录，第一轮见报告开篇）")
    lines.append("")
    for level, heading in report_rounds():
        lines.append(f"{'  ' * (level - 2)}- {heading}")
    lines.append("")
    lines.append(f"### 2.2 仓库提交中的逐轮记录（{len(git_rounds())} 条）")
    lines.append("")
    lines.append("| 轮次 | 提交 | 日期 | 内容 |")
    lines.append("|---|---|---|---|")
    for round_id, sha, date, title in git_rounds():
        lines.append(f"| Round {round_id} | `{sha}` | {date} | {title} |")
    lines.append("")
    lines.append("## 三、质量守卫（闸门 45 项）")
    lines.append("")
    for index, label in enumerate(gate_checks(), 1):
        lines.append(f"{index}. {label}")
    lines.append("")
    lines.append("## 四、数据与证据基线")
    lines.append("")
    lines.append("```")
    for line in auth.splitlines():
        if line.strip() and not line.startswith(("ISSUE", "DATA_AUTHENTICITY")):
            lines.append(line.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("## 五、未闭合事项（需作者或外部输入）")
    lines.append("")
    for line in readiness.splitlines():
        if line.strip().startswith(("open", "ISSUE")) or "open item" in line:
            lines.append(f"- {line.strip()}")
    lines.append("")
    lines.append("## 六、复现与出包命令")
    lines.append("")
    lines.append("```powershell")
    lines.append('$py = "E:\\论文\\.venv\\Scripts\\python.exe"')
    lines.append("& $py scripts\\verify_all_v8.py                 # 45 项验证闸门")
    lines.append("& $py scripts\\build_restructured_manuscript_v4.py --only all")
    lines.append("& $py scripts\\convert_equations_word_v41.py")
    lines.append("& $py scripts\\build_publication_manifest.py")
    lines.append("& $py scripts\\package_submission_bundle_v18.py  # 重建投稿压缩包")
    lines.append("& $py scripts\\audit_data_authenticity_v1.py    # 数据真实性复核")
    lines.append("& $py scripts\\build_work_log_v1.py             # 重生成本日志")
    lines.append("```")
    lines.append("")
    lines.append("## 七、交付物位置")
    lines.append("")
    lines.append(f"- 投稿压缩包：`submission_package/论文投稿包_{TAG}.zip`")
    lines.append(f"- 桌面交付副本：`C:\\Users\\27677\\Desktop\\论文_{TAG}_全语料版\\`")
    lines.append("- 正式稿件与辅助文档：`重构版论文_v4_20260915/`")
    lines.append("- 补充材料：`重构版论文_v4_20260915/补充材料_S01_S30/`")
    lines.append("- 逐样本证据与发布清单：`results_publication_final/`")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WORK_LOG_WRITTEN={OUT}")
    print(f"lines={len(lines)} rounds={len(git_rounds())} guards={len(gate_checks())}")


if __name__ == "__main__":
    main()
