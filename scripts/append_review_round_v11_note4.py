"""Add the stale supplementary mirror to the eleventh review round."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
ADDITION = """
### 同轮续查（第九处）：仓库里仍留着被取代的补充材料目录

`results_publication_final/supplementary/` 里放的还是**早期命名**的补充材料（`S1_cic_cfrg_class_report.csv` … `S15_temperature_calibration.csv`），而稿件与正式成册目录用的是 `S01`–`S26`。结果是：任何人（包括导师、审稿人、未来的自己）下载 `results_publication_final/` 之后，看到的补充材料与论文清单**对不上**，且无法判断哪一份是当前的。

处置：把该目录改成**由规范化目录生成的镜像**。

1. 新增 `scripts/sync_supplementary_mirror_v16.py`：默认从 `重构版论文_v4_20260915/补充材料_S01_S26/` 同步，`--check` 只做校验。脚本在动手前校验目标路径确实位于仓库内的 `results_publication_final/supplementary`，避免误删。
2. 同步后镜像为 60 个文件（58 个材料文件 + 索引 + 校验清单），旧命名文件不再存在。
3. 校验器并入闸门：逐文件比对两侧的 SHA-256，出现新增、缺失或改动即报 `SUPPLEMENTARY_MIRROR_MISMATCH`。闸门现含 **14 类检查**。

这条与第十一处（发布清单）、第十处（补充材料目录名）同源：**同一个事实在仓库里存了多份，只有一份被更新**。至此本项目里所有"同一事实多副本"的位置都已改为「单一来源 + 自动派生 + 闸门校验」。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第九处）" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND11_NOTE4_RECORDED")
if __name__ == "__main__":
    main()
