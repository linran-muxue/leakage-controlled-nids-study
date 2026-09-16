"""Update the self-check table after the DOI, resource, container and CI work."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    text = fix(text, "| A 诚信与合规 | 10 | 7 | 3 | 0 |", "| A 诚信与合规 | 10 | 8 | 2 | 0 |", "sA")
    text = fix(text, "| D 实验与统计 | 14 | 12 | 2 | 0 |", "| D 实验与统计 | 14 | 13 | 1 | 0 |", "sD")
    text = fix(text, "| F 可复现与投稿合规 | 9 | 6 | 0 | 3 |", "| F 可复现与投稿合规 | 9 | 8 | 1 | 0 |", "sF")
    text = fix(text, "| **合计** | **59** | **47** | **8** | **4** |",
               "| **合计** | **59** | **51** | **7** | **1** |", "sT")

    # A3
    text = fix(text,
               "| A3 | 引文准确性 | 正文逐条标注且条目不虚构 | **部分通过** | `check_citation_coverage_v5.py`：中英各 45/45 全覆盖；`spotcheck_citations_v5.py` 抽查 21 条零失配。**但 13 条 DOI 仍标「待核验」** |",
               "| A3 | 引文准确性 | 正文逐条标注且条目不虚构 | **通过** | 中英各 45/45 全覆盖，抽查 21 条零失配；**45 条 DOI 已全部通过 Crossref 核验**（1 条补全、10 条确认为 PMLR/NeurIPS/JMLR/USENIX 无 DOI 并显式标注），待核验占位符清零（`results_review_v5/doi_verification.json`） |",
               "A3")

    # D7
    text = fix(text,
               "| D7 | 资源成本 | 时间、内存、体积、吞吐 | **部分通过** | 有训练时间、单条延迟 P50/P95/P99；**缺内存、模型体积、吞吐率** |",
               "| D7 | 资源成本 | 时间、内存、体积、吞吐 | **通过** | 已补：模型体积 9.09 MB 对 2.21 MB（4.1 倍）、整批吞吐 43 100 对 200 300 行/秒（4.6 倍）、峰值内存增量 37.0 对 78.3 MB（`results_resources_v5/`） |",
               "D7")

    # F6 / F7 / F9
    text = fix(text,
               "| F6 | 容器化 | 可复现环境 | **缺失** | 无 Dockerfile 或 conda 环境文件，仅 `requirements-lock.txt` |",
               "| F6 | 容器化 | 可复现环境 | **通过** | 已添加 `Dockerfile`（python:3.11-slim + 锁定依赖 + 测试入口） |",
               "F6")
    text = fix(text,
               "| F7 | 持续集成 | 回归可自动发现 | **缺失** | 无 `.github/workflows` |",
               "| F7 | 持续集成 | 回归可自动发现 | **通过** | 已添加 `.github/workflows/tests.yml`：安装直接依赖、运行 118 项测试、编译全部源码 |",
               "F7")
    text = fix(text,
               "| F9 | 图形摘要与投稿信 | 与现主线一致 | **缺失** | 现有 `Graphical_Abstract_JISA`、`cover_letter_template_en` 均为旧定位产物；未按新主线重做，也尚未套用目标期刊模板 |",
               "| F9 | 图形摘要与投稿信 | 与现主线一致 | **部分通过** | 已按新主线重做 `Graphical_Abstract_v4.png/pdf`（四面板：协议、十种子等价、机制、协议效应）与 `Cover_Letter_JISA_v4.md`；**尚余按 JISA 官方模板排版** |",
               "F9")

    # closing
    text = fix(text,
               "结论（十种子扩展后）：**47 项通过、8 项部分通过、4 项缺失**。",
               "结论（DOI 核验、资源画像、容器化、CI 与投稿材料之后）：**51 项通过、7 项部分通过、1 项缺失**。",
               "closing")
    text = fix(text, "### 缺失项（4 项，均不影响数据与论证正确性）",
               "### 缺失项（仅剩 1 项）", "action-head")
    text = fix(text, "| E6 | 母语润色 | 送专业润色，或逐章人工改写 | 是（需确认是否付费润色） |\n",
               "| E6 | 母语润色 | 送专业润色，或逐章人工改写 | 是（需确认是否付费润色） |\n"
               "| F9（余项） | 按 JISA 官方模板排版 | 下载模板后套用 | 否 |\n", "action-add")

    # record the new disclosures
    text = fix(text, "### 部分通过项中必须由你处理的",
               "### 本轮新增的诚实披露\n\n"
               "6.5 节新增两条局限说明，消除了此前「引言提出危害但未处理」的落差：\n\n"
               "- **近重复只按精确形式剔除**：四位有效数字下另有 0.36% 的行构成近重复，104 条测试行（0.21%）与训练行重叠；"
               "剔除后三模型 Macro-F1 变化不超过 0.00057，另有敏感性检验。\n"
               "- **未评估对抗鲁棒性**：只施加随机扰动，不构成对自适应对手的保证。\n\n"
               "### 部分通过项中必须由你处理的",
               "disclosure")

    MD.write_text(text, encoding="utf-8")
    print("SELFCHECK_V5B_UPDATED")


if __name__ == "__main__":
    main()
