"""Close the Round 20 documentation debt and refresh the meta documents.

The paper and the release artefacts were current after Round 20bi, but the
meta layer was not: the review report stopped at Round 19, the gap audit and
the self-check predate the modern-corpus programme, and Section 5.8 still said
"six extensions" although the extension report now carries fourteen.

Every edit is assertion-anchored and idempotent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def replace(path: Path, old: str, new: str, note: str, already: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    marker = already if already is not None else new
    if marker in text:
        print(f"{path.name}: already applied ({note})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note}")


def append(path: Path, block: str, sentinel: str, note: str) -> None:
    text = path.read_text(encoding="utf-8")
    if sentinel in text:
        print(f"{path.name}: already applied ({note})")
        return
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + block, encoding="utf-8")
    print(f"{path.name}: {note}")


def numbers() -> dict:
    def load(name: str) -> dict:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))

    return dict(
        b=load("results_rccf_cic_iot2023_cap200k/benchmark_summary.json"),
        c=load("results_rccf_cic_iot2023_cap500k/benchmark_summary.json"),
        g=load("results_rccf_gotham2025_cap200k/benchmark_summary.json"),
        full=load("results_rccf_gotham2025_full/benchmark_summary.json"),
        t=load("results_rccf_6tisch2026_uncapped/benchmark_summary.json"),
        u=load("results_rccf_ctu_idseval6_uncapped/benchmark_summary.json"),
        hg=load("results_source_holdout_gotham_v1/holdout_summary.json"),
        ht=load("results_source_holdout_6tisch_v1/holdout_summary.json"),
        k8=load("results_rccf_cic_iot2023_k8/benchmark_summary.json"),
        k16=load("results_rccf_cic_iot2023_k16/benchmark_summary.json"),
        k32=load("results_rccf_cic_iot2023_k32/benchmark_summary.json"),
        k60=load("results_rccf_cic_iot2023_k60/benchmark_summary.json"),
        mc=load("results_margin_bound_cic-iot2023_v1/margin_bound_summary.json"),
        mg=load("results_margin_bound_gotham2025_v1/margin_bound_summary.json"),
    )


def review_section(n: dict) -> str:
    return f"""
## Z. 第二十轮审查（2026-10-06）：现代语料阶梯——规模、分布位移与机制

**这一轮要解决的问题。** 第十九轮把 CIC-IDS2017 的每类上限取消到 2 429 503 条，
结论仍是「小而稳定的劣势」，但那只说明一个 2017 年的语料。老师的意见是语料太老，
于是本轮的检验目标变成：把规模阶梯搬到现代语料、再叠加真实分布位移（换设备、
换运行），主结论还站不站得住；如果站得住，机制上为什么。

**跑了什么（全部十种子、同一协议）。**

| 组件 | 测试行 | RCCF | 同成员等权 | 差值 |
|---|---:|---:|---:|---:|
| CIC-IoT-2023 每类 20 万 | {n['b']['test_rows']:,} | {n['b']['rccf_mean_macro_f1']:.6f} | {n['b']['equal_fusion_mean_macro_f1']:.6f} | {n['b']['same_members_difference']:+.6f} |
| CIC-IoT-2023 每类 50 万 | {n['c']['test_rows']:,} | {n['c']['rccf_mean_macro_f1']:.6f} | {n['c']['equal_fusion_mean_macro_f1']:.6f} | {n['c']['same_members_difference']:+.6f} |
| Gotham-2025 每类 20 万 | {n['g']['test_rows']:,} | {n['g']['rccf_mean_macro_f1']:.6f} | {n['g']['equal_fusion_mean_macro_f1']:.6f} | {n['g']['same_members_difference']:+.6f} |
| Gotham-2025 不限上限 | {n['full']['test_rows']:,} | {n['full']['rccf_mean_macro_f1']:.6f} | {n['full']['equal_fusion_mean_macro_f1']:.6f} | {n['full']['same_members_difference']:+.6f} |
| 6TiSCHSet 不限上限 | {n['t']['test_rows']:,} | {n['t']['rccf_mean_macro_f1']:.6f} | {n['t']['equal_fusion_mean_macro_f1']:.6f} | {n['t']['same_members_difference']:+.6f} |
| CTU-IDSEVAL-6 不限上限 | {n['u']['test_rows']:,} | {n['u']['rccf_mean_macro_f1']:.6f} | {n['u']['equal_fusion_mean_macro_f1']:.6f} | {n['u']['same_members_difference']:+.6f} |

来源留出（换设备、换运行的分布位移）：Gotham 逐设备 {n['hg']['groups_evaluated']}/{n['hg']['groups_total']} 台，
RCCF 均值 {n['hg']['rccf_macro_f1_mean']:.6f}、最小 {n['hg']['rccf_macro_f1_min']:.6f}、
两臂差 {n['hg']['mean_difference']:+.6f}；6TiSCHSet 逐运行 {n['ht']['groups_evaluated']}/{n['ht']['groups_total']} 次，
均值 {n['ht']['rccf_macro_f1_mean']:.6f}、最小 {n['ht']['rccf_macro_f1_min']:.6f}、
两臂差 {n['ht']['mean_difference']:+.6f}。

特征预算扫描（CIC-IoT-2023）：k=8 {n['k8']['same_members_difference']:+.6f}、
k=16 {n['k16']['same_members_difference']:+.6f}、k=32 {n['k32']['same_members_difference']:+.6f}、
k=60 {n['k60']['same_members_difference']:+.6f}——单调，k≥32 归零。

机制套件：Gotham 全档两臂改判 {n['mg']['empirical_changed_rows']}/{n['mg']['total_rows']:,} 行，
CIC-IoT-2023 改判 {n['mc']['empirical_changed_rows']}/{n['mc']['total_rows']:,} 行
（理论界可证 {n['mc']['provable_by_bound_rate_mean'] * 100:.2f}%），树权重只偏离均匀值约 ±3%。

**本轮发现并修掉的缺陷（全部为断言锚点脚本修复，未改动任何已报数字）。**

1. **训练进程四次被内存打断。** 前三次是 `numpy._ArrayMemoryError`：一次在单视图森林拟合
   （申请 109 MiB 失败），两次在门控自身。定位到真凶是 `src/rccf_forest.py` 的峰值结构：
   对 1 210 万训练行 × 4 专家 × 18 类，out-of-fold 概率张量 `oof` 约 7 GB、`oof_desc` 约 1.2 GB，
   随后风险模型又把 `risk_features` 复制成 `scaled`（再约 8 GB），峰值逼近 24 GB。
   修法是在用完那一刻 `del oof, oof_desc`、风险模型循环后 `del risk_features, risk_targets, scaled`、
   单视图森林开训前释放门控与临时数组，并在运行器加 `--n-jobs`（默认 8）与可用内存守卫。
2. **计划任务的电池策略会静默杀进程。** `CodexGothamFullRun` 带「切电池即停止」，
   笔记本一旦切到电池就整棵树被杀、且不留 traceback——这正是 19:42 那次「无声死亡」。
   两个任务改为允许电池运行（原 XML 备份在 `logs/task_xml_backup/`）。
3. **我自己引入的编码缺陷。** 上述重注册用了 UTF-8，而任务 XML 声明 UTF-16，
   任务路径里的「论文」被解码成乱码，15 分钟一次的自愈从此以 0x80070002 失败。
   已用 UTF-16LE 重注册并逐条查询确认命令行正确。
4. **phase-2 驱动会提前放行。** 续跑返回后它顺流往下跑，把两个留出与后续档位在
   Gotham 未完成时就启动；改为续跑即返回、且 Gotham 汇总缺失时不启动后续步骤。
5. **来源留出「校准集缺类」。** 原实现按位置切分训练集，导致留出某个设备/运行后
   校准确认集缺类，两个留出都以退出码 1 失败、零指标。改为分层切分且每类至少两行进确认集。
6. **多样性套件两处硬编码。** 互斥特征视图按 60 列硬编码（CIC-IoT-2023 只有 39 列）导致
   `IndexError`；宏 F1 的类别表沿用 CIC-IDS2017 五类，使等权 F1 只算出 0.143。
   已改为按语料实际宽度切分、按语料自身类别表评分（对历史语料加断言，已报数字不变）。
   7. **六处结果目录的记账错误。** `results_rccf_{{cic_iot2023_cap20k,cap200k,cap500k,k8,k16,k32,k60,
   gotham2025_cap200k,gotham2025_full,6tisch2026_uncapped,ctu_idseval6_uncapped}}` 的
   `test_samples_mean` 记成了组数（10）而不是测试行数，闸门的数据真实性检查抓到后由
   `fix_extension_metrics_v1.py` 按预测文件行数重算。

**验证与交付。** 四次中断全部自动续跑，四个已完成种子在重启后回放出的数值与崩溃前逐位一致；
53 项闸门全绿（`GATE_PASSED all checks green`）；提交 `edfaf14`（Round 20bi）、标签 `v1.11.0`
（`449e0a4`）已推送；投稿包 909 文件 / 22.9 MB；桌面交付目录由 `sync_desktop_delivery_v1.py`
镜像并对 7 个关键文件做了 SHA-256 校验。

**结论。** 2017 语料上那个 -0.005533 的规模性劣势没有在现代语料上复现：CIC-IoT-2023 在
246 万训练行上仍只有 -0.000004，Gotham 全档在 1 425 万训练行、719 万测试行上是 +0.000009。
真正决定等价性的是成员可互换性：特征预算压到 8 维时门控赢 +0.001663，用满时回到噪声水平；
机制套件（改判 0–12 行、权重偏离均匀 ±3%）给出同一条因果链的定量形式。

**仍未闭合的项。** 全部集中在需要作者输入的四处：A5 署名与 CRediT、A6 基金与利益冲突、
E6 母语润色、F9 期刊模板排版。数据与论证侧无未闭合项。
"""


def correct_weight_claim() -> None:
    """State the tree-weight spread exactly instead of the "about ±3%" shorthand.

    The Gotham-2025 weight mechanism spans 0.0091-0.0102, i.e. 9.1% below and
    2.0% above the 0.01 uniform value; "±3%" was true for the CIC-IoT-2023 run
    (0.0097-0.0102) but not for Gotham.  The measurements do not change - only
    the sentence that describes them.
    """
    pairs = [
        ("树权重只偏离均匀值约 ±3%。", "树权重落在 0.0091–0.0102 之间（均匀值为 0.01）。"),
        ("幅度只偏离均匀值约 ±3%", "幅度落在 0.0091–0.0102 之间（均匀值为 0.01）"),
        ("权重偏离均匀值约 ±3%", "权重落在 0.0091–0.0102 之间"),
        ("权重机制（偏离均匀 ±3%）", "权重机制（树权重 0.0091–0.0102）"),
        ("权重偏离均匀 ±3%", "权重落在 0.0091–0.0102 之间"),
        ("树权重偏离均匀值约 ±3%", "树权重落在 0.0091–0.0102 之间"),
        ("with tree weights within about ±3% of uniform",
         "with tree weights in 0.0091-0.0102 against the 0.01 uniform value"),
        ("weights within about ±3% of uniform",
         "weights in 0.0091-0.0102 against the 0.01 uniform value"),
    ]
    targets = [BASE / "中文SCI论文_v4_重构版.md", BASE / "English_SCI_Manuscript_v4.md",
               BASE / "扩展实验报告.md", BASE / "遗漏问题审查报告.md",
               BASE / "研究缺口审计与优先级清单.md", BASE / "论文介绍.md",
               BASE / "向老师汇报要点.md",
               ROOT / "scripts" / "add_modern_ladder_to_paper_v1.py",
               ROOT / "scripts" / "build_extension_report_v1.py",
               ROOT / "scripts" / "add_ladder_to_briefings_v1.py"]
    changed = 0
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in pairs:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"{path.name}: weight claim corrected")
    print(f"weight claim: {changed} file(s) updated")
    print("ROUND20_DOCS_FINALISED")


def main() -> None:
    n = numbers()
    correct_weight_claim()
    add_figure_references()
    trim_abstract()
    assert_abstract_has_no_ladder()
    drop_cjk_from_english()
    review = BASE / "遗漏问题审查报告.md"
    append(review, review_section(n), "## Z. 第二十轮审查", "review report: Round 20 entry")

    audit = BASE / "研究缺口审计与优先级清单.md"
    replace(audit,
            "## 一、定位与主张层",
            "## 〇、第二十轮补充：现代语料阶梯（2026-10-06）\n\n"
            "本轮把「主语料换成现代语料」的验证从单点扩到规模档位、分布位移与机制分解，"
            "原先列在「语料陈旧」「规模不足」「只有相关性证据」三条下的缺口均已闭环：\n\n"
            "- **语料陈旧**：17 个语料覆盖 1998–2026，其中 2020 年后 12 个、2025 年 4 个、2026 年 3 个；\n"
            "- **规模不足**：CIC-IoT-2023 到 246 万训练行、Gotham-2025 到 1 425 万训练行 /"
            "719 万测试行，-0.005533 的劣势未复现；\n"
            "- **分布位移**：Gotham 逐设备留出（12/78）与 6TiSCHSet 逐运行留出（12/122）下的两臂差"
            f"分别为 {n['hg']['mean_difference']:+.6f} 与 {n['ht']['mean_difference']:+.6f}；\n"
            "- **机制解释**：边距上界（Gotham 改判 0 行）、权重机制（偏离均匀 ±3%）与多样性"
            "剂量—反应（r = 0.744）三条证据链到位；\n"
            "- **可复现性**：`docs/ladder_scripts_index.md` 给出这一批 20 个脚本的索引与运行顺序。\n\n"
            "仍未闭合的只有作者输入项（署名与 CRediT、基金与利益冲突、母语润色、期刊模板排版）。\n\n"
            "## 一、定位与主张层",
            "gap audit: Round 20 subsection",
            already="## 〇、第二十轮补充：现代语料阶梯")

    selfcheck = BASE / "论文自查表.md"
    replace(selfcheck,
            "**69 项检查中 65 项通过、4 项部分通过、0 项缺失。**",
            "**第二十轮补充证据（不改动 69 项计数）**：现代语料阶梯四项结果（B/C 档、"
            "Gotham 每类 20 万与不限上限）与来源留出、特征预算扫描、机制套件已写入论文与"
            "扩展实验报告，并由 `scripts/add_modern_ladder_to_paper_v1.py` 断言源值；"
            "53 项闸门新增覆盖阶梯脚本、结果目录与数据真实性记账。据此，"
            "数据与论证类条目仍为全部通过，剩余四项部分通过仍集中在作者输入与排版。\n\n"
            "**69 项检查中 65 项通过、4 项部分通过、0 项缺失。**",
            "self-check: Round 20 evidence note",
            already="第二十轮补充证据")

    zh = BASE / "中文SCI论文_v4_重构版.md"
    en = BASE / "English_SCI_Manuscript_v4.md"
    replace(zh, "六个扩展实验界定了主结论的边界；",
            "十四个扩展实验界定了主结论的边界；",
            "ZH §5.8 extension count", already="十四个扩展实验界定了主结论的边界；")
    replace(en, "Six extensions probe the boundaries of the main result;",
            "Fourteen extensions probe the boundaries of the main result;",
            "EN §5.8 extension count",
            already="Fourteen extensions probe the boundaries of the main result;")


    readme = ROOT / "README.md"
    replace(readme, "## Main artifacts",
            "## 重型预测产物与再生成\n\n"
            "现代语料阶梯那几档（Gotham 全档、CIC-IoT-2023 两档、6TiSCH/CTU 不限上限、"
            "特征预算四档）的逐样本预测是多 GB 级文件，合计约 70 GB，存放于本地重产物卷 "
            "`E:\\论文\\_heavy_results\\`（工作区的同名目录是指向它的联接），并已列入 `.gitignore`；"
            "随仓库与投稿包分发的是汇总、逐种子指标与 `checksums.sha256`。\n\n"
            "再生成方式（幂等，产物已存在则跳过）：\n\n"
            "```powershell\n"
            "& $py scripts\\run_modern_ladder_queue_v1.py     # 总队列\n"
            "& $py scripts\\run_modern_ladder_phase2_v1.py    # 守护：等 Gotham 全档并补齐后续步骤\n"
            "```\n\n"
            "脚本清单与运行顺序见 `docs/ladder_scripts_index.md`。\n\n"
            "## Main artifacts",
            "README: heavy predictions note",
            already="## 重型预测产物与再生成")


def add_figure_references() -> None:
    """Point Section 5.8 at Figure 12 in both language editions."""
    zh = BASE / "中文SCI论文_v4_重构版.md"
    en = BASE / "English_SCI_Manuscript_v4.md"
    replace(zh,
            "树权重落在 0.0091–0.0102 之间（均匀值为 0.01）。",
            "树权重落在 0.0091–0.0102 之间（均匀值为 0.01）。\n\n"
            "![图 12 现代语料阶梯：规模档位、特征预算与机制]"
            "(figures/fig12_ladder_modern.png)",
            "ZH §5.8 Figure 12 reference",
            already="![图 12 现代语料阶梯")
    replace(en,
            "with tree weights in 0.0091-0.0102 against the 0.01 uniform value.",
            "with tree weights in 0.0091-0.0102 against the 0.01 uniform value.\n\n"
            "![Figure 12. The modern-corpus ladder: scale rungs, feature budget and "
            "mechanism](figures_en/fig12_ladder_modern.png)",
            "EN §5.8 Figure 12 reference",
            already="![Figure 12. The modern-corpus ladder")


def trim_abstract() -> None:
    """Remove the ladder clause from the English abstract (JISA caps it at 250 words).

    The original abstract already sat at 248 words, so the ladder is reported in
    Sections 5.8-5.9, the extension report, the supervisor deck and the briefings
    instead.  The routine is idempotent and collapses the duplicated form an
    earlier partial run could leave behind.
    """
    en = BASE / "English_SCI_Manuscript_v4.md"
    short = ("Uncapped modern corpora (7,189,693 test rows) differ by +0.000009; "
             "device- and run-level holdouts remain indistinguishable. ")
    long_form = ("Replacing the primary corpus with modern ones leaves the conclusion "
                 "intact: the uncapped Gotham-2025 corpus (7,189,693 test rows) differs by "
                 "+0.000009, device-level and run-level holdouts remain indistinguishable, "
                 "and the gate wins only when the feature budget is small enough to make "
                 "the members mutually exclusive. ")
    text = en.read_text(encoding="utf-8")
    original = text
    if short + long_form in text:
        text = text.replace(short + long_form, short, 1)
    if long_form in text:
        text = text.replace(long_form, "", 1)
    if short in text:
        text = text.replace(short, "", 1)
    if text != original:
        en.write_text(text, encoding="utf-8")
        print("English_SCI_Manuscript_v4.md: ladder clause removed from the abstract")
    else:
        print("English_SCI_Manuscript_v4.md: abstract already clean")


def assert_abstract_has_no_ladder() -> None:
    """The JISA abstract cap (250 words) leaves no room for the ladder clause.

    The original English abstract already sat at 248 words, so the ladder is
    reported in Sections 5.8-5.9, the extension report, the supervisor deck and
    the briefings instead - all of which have no such limit.  This guard keeps a
    future re-run of add_modern_ladder_to_paper_v1.py from pushing it back in.
    """
    en = BASE / "English_SCI_Manuscript_v4.md"
    zh = BASE / "中文SCI论文_v4_重构版.md"
    en_text = en.read_text(encoding="utf-8")
    zh_text = zh.read_text(encoding="utf-8")
    abstract_en = en_text[en_text.find("## Abstract"):en_text.find("**Keywords")]
    if "modern corpora" in abstract_en and "7,189,693" in abstract_en:
        raise SystemExit("English abstract carries a ladder clause; the JISA cap is 250 words")
    i = zh_text.find("## 摘要")
    abstract_zh = zh_text[i:zh_text.find("**关键词", i)]
    if "现代语料阶梯" in abstract_zh or "7 189 693" in abstract_zh:
        raise SystemExit("Chinese abstract carries a ladder clause; keep the pair symmetric")
    print("abstracts: no ladder clause (JISA 250-word cap respected)")


def drop_cjk_from_english() -> None:
    """Keep the English manuscript free of CJK characters.

    Section 5.8 pointed at the extension report by its Chinese title; the file is
    released with a Chinese name, but an English manuscript should describe it in
    English and let the path carry the name.
    """
    en = BASE / "English_SCI_Manuscript_v4.md"
    replace(en,
            "ship with the release (扩展实验报告, `results_*_v1/`)",
            "ship with the release (the extension-experiment report, `results_*_v1/`)",
            "EN §5.8: report named in English",
            already="the extension-experiment report, `results_*_v1/`")


if __name__ == "__main__":
    main()
