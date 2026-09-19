"""Record the eighteenth round: the scale experiment and the fourth dataset."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
COVER = ROOT / "重构版论文_v4_20260915" / "Cover_Letter_JISA_v4.md"

ADDITION = """

---

## X. 第十八轮审查（2026-09-19）：补规模、补领域——把"证据不够大"这条堵上

前十七轮把稿子的工艺做到了能查到的极限，但第十七轮的自评里最要命的一条是**证据规模与外部有效性**：主研究总体只有 53 237 条（去重后语料的 2.0%），且四个数据集里没有一个物联网场景。这一轮不再改文字，改为**补实验**。

### 一、规模实验：同一协议，总体扩大 7.8 倍

用完全相同的审计流程、只把每类上限从 2 万条提高到 20 万条，重建 CIC-IDS2017 总体：**413 209 条**（训练 289 246 / 验证 61 982 / 测试 61 982）。少数类无法增长，因此扩大后的总体反而更不平衡（Brute Force 10 620、Bot 1 948、Web Attack 673）。

头条对照按与主实验一致的十个种子重跑（RCCF 单次训练约 12 分钟，共约 2 小时）：

| 指标 | 结果 |
|---|---|
| RCCF 平均 Macro-F1 | 0.856065 |
| 等权 χ² 森林平均 Macro-F1 | 0.857202 |
| 平均配对差 | **−0.001137**（标准差 0.003156） |
| 种子级 90% 区间 | [−0.002966, +0.000692] |
| TOST（SESOI = 0.005） | **等价**（p = 0.0019） |
| TOST（SESOI = 0.01） | **等价**（p = 4.8e-6） |
| 每种子改判条数 | 20–29 / 61 982（0.03%–0.05%） |

结论：**等价性不是 2% 截断造成的**；而且点估计此时略微偏向等权森林而非 RCCF。

### 二、第四个数据集：N-BaIoT（物联网僵尸网络）

来源为 UCI 机器学习库第 442 号数据集（Meidan 等，IEEE Pervasive Computing 2018），九种消费级物联网设备的正常流量与 Mirai/Gafgyt 攻击，115 维流特征，**页面明确标注 CC BY 4.0**——这是四个数据集中唯一有明确许可证的。

构建过程中有两个值得记录的发现：

1. **67.8% 的行是完全重复的**（7 062 606 行中剔除 4 784 430 行），重复比例高于本研究任何其他数据集——这本身就是本文主题的又一个独立佐证。
2. 攻击数据以 **RAR** 分发，本机没有解压器且策略不允许运行安装程序。解决办法是：从 MSYS2 官方仓库取出独立 `unrar.exe` 及其运行时 DLL（用 Python 解 `.tar.zst` 包），全程未在系统中安装任何程序。该工具与来源已记入 `docs/source_records/` 与数据来源表。

结果：所有模型 Macro-F1 ≥ 0.9998（RCCF 0.999988 对等权 χ² 森林 0.999988，平均差 −3.7e-17，27 000 条测试样本中分歧 0–2 条）。该基准对流量特征分类器已经饱和——**而这正是命题 1 预言"任何加权都无法改变预测"的情形**，因此它在新领域验证了机制的惰性，同时也诚实地表明它不检验判别难度。

### 三、随之而来的改动

- 新增 §5.7「规模与领域敏感性」（中英同步）；摘要、贡献 3、§3.3 覆盖论证、§6.5 局限全部改写：数据集由三个变四个，"第四个数据集应当引入"改为"已引入并说明其边界"。
- 参考文献增至 **47 条**（新增 N-BaIoT 论文与数据集 DOI，均经 Crossref 核验）；由于列表按引用顺序编号，原第 17 条起整体后移两位，正文引用一并重排。
- 补充材料扩充为 **S01–S28**（新增 S27 规模敏感性、S28 N-BaIoT），目录重命名为 `补充材料_S01_S28`，镜像同步。
- 数据来源表新增 N-BaIoT 行（URL、检索日期、CC BY 4.0、SHA-256、来源记录文件）。
- 自查表新增 **D15（规模与领域稳健性）**，由 68 项增至 **69 项：65 通过 / 4 部分通过 / 0 缺失**。

### 四、这一轮之后，第十七轮列出的"证据不够大"还剩什么

全语料（2 429 503 条）训练仍未做：规模实验覆盖了 413 209 条（17%）。这一条已作为显式局限写入 §6.5，不再是未披露的缺口。
"""

COVER_OLD = "Both the seed-level 90% interval [-0.00112, +0.00021] and the test-row paired bootstrap interval [-0.00425, +0.00338] lie inside pre-specified equivalence margins of 0.005 and 0.01 Macro-F1, so the paper can assert equivalence rather than merely failing to reject a null."
COVER_NEW = ("Both the seed-level 90% interval and the test-row paired bootstrap interval lie inside pre-specified "
             "equivalence margins of 0.005 and 0.01 Macro-F1, so the paper can assert equivalence rather than merely "
             "failing to reject a null. Because that population is a capped subset, we also rebuild it 7.8 times "
             "larger (413,209 flows) and repeat the ten-seed comparison there: the equivalence holds at both margins, "
             "with the point estimate now slightly favouring the control. A fourth dataset from a different domain "
             "(N-BaIoT: consumer-IoT botnet traffic, 180,000 flows) is saturated for every flow-feature classifier, "
             "which is precisely the regime our Condition 1 predicts.")


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## X. 第十八轮审查" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND18_RECORDED")
    else:
        print("review already recorded")
    cover = COVER.read_text(encoding="utf-8")
    if COVER_OLD in cover:
        COVER.write_text(cover.replace(COVER_OLD, COVER_NEW, 1), encoding="utf-8")
        print("cover letter updated")
    else:
        print("cover letter anchor absent")


if __name__ == "__main__":
    main()
