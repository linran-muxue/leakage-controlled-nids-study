"""Repair the two soft spots a supervisor flagged: causal wording on a
correlation, and cost numbers quoted without their source.

(1) The diversity evidence is fifteen constructed configurations measured with
    three-fold cross-fitting.  The manuscripts said the gain is "governed by"
    expert diversity, which reads as a causal claim.  The wording becomes
    co-variation, and a limitation states explicitly that no intervention was
    run.
(2) The cost figures mix two different measurements: training and batch
    inference from the ten-seed primary run, the resource profile (model size,
    throughput) from a single seed, and the latency percentiles from three
    seeds.  Each statement now names its source.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

EN_EDITS: list[tuple[str, str]] = [
    ("All 108 gate configurations yield six distinct validation scores; the gain is governed by "
     "expert diversity (slope 0.0646, r = 0.749).",
     "All 108 gate configurations yield six distinct validation scores; across the fifteen "
     "configurations tested, the gain co-varies with expert diversity (slope 0.0646, r = 0.749, "
     "an association rather than an intervention)."),
    ("**Measurement 6: the gain is governed by expert diversity, not by the implementation.**",
     "**Measurement 6: the gain co-varies with expert diversity; the inertness is not an "
     "implementation artefact.**"),
    ("This yields the most important mechanistic conclusion of the study: **the gain of "
     "conditional weighting is governed by expert diversity.**",
     "This yields the most important mechanistic conclusion of the study: **the gain of "
     "conditional weighting moves with expert diversity.** The relation is measured over fifteen "
     "constructed configurations, so it is a dose-response association: it shows that the gain "
     "and expert disagreement move together, not that disagreement alone causes a gain."),
    ("A reverse experiment shows that the gain is governed by expert diversity:",
     "A deliberately constructed reverse experiment shows that the gain moves with expert "
     "diversity:"),
    ("The cost is about an 80-fold increase in training time and a fivefold increase in batch "
     "inference time.",
     "The cost is about an 80-fold increase in training time and a fivefold increase in batch "
     "inference time (ten-seed means, Table 4(a))."),
    ("The mechanism is 4.1 times larger and 4.6 times slower, without cost-sensitive advantage.",
     "The mechanism is 4.1 times larger and 4.6 times slower (single-seed resource profile, S22), "
     "without cost-sensitive advantage."),
    ("**Resource footprint.** Model size and throughput separate the two designs more sharply than "
     "wall-clock time.",
     "**Resource footprint** (single seed, whole test batch; S22). Model size and throughput "
     "separate the two designs more sharply than wall-clock time."),
    ("**Latency.** For single-row inference on one thread,",
     "**Latency** (three seeds, 7,986 test rows; S15). For single-row inference on one thread,"),
    ("The gap widens on the balanced control, where training takes 9.13 s against 0.45 s.",
     "The gap widens on the balanced control, where training takes 9.13 s against 0.45 s "
     "(three seeds, Table 4(b))."),
    ("**The same-members control covers the primary population.**",
     "**The diversity evidence is associational.** The dose-response relation rests on fifteen "
     "constructed expert configurations evaluated with three-fold cross-fitting; it shows that "
     "the gain moves with expert disagreement, not that disagreement alone causes a gain. No "
     "intervention that fixes disagreement while holding everything else constant was run.\n\n"
     "**The same-members control covers the primary population.**"),
]

ZH_EDITS: list[tuple[str, str]] = [
    ("108 种门控配置只产生 6 个不同的验证集取值，增益受专家多样性支配（斜率 0.0646，r = 0.749）。",
     "108 种门控配置只产生 6 个不同的验证集取值；在本文测试的十五个配置上，"
     "增益与专家多样性同步变化（斜率 0.0646，r = 0.749，属相关性证据而非干预实验）。"),
    ("**测量六：增益受专家多样性支配，而不是受实现限制（反向验证）。**",
     "**测量六：增益与专家多样性同步变化，惰性不是实现问题（反向验证）。**"),
    ("这给出本文最重要的机制结论：**条件加权的增益受专家多样性支配；",
     "这给出本文最重要的机制结论：**条件加权的增益与专家多样性同步变化**"
     "（十五个构造配置上的剂量—反应关系，属相关性证据：它表明增益与专家分歧同向变化，"
     "而不是证明分歧本身单独导致增益）；"),
    ("第二，**失效是可解释的，而且是定量的。**增益受专家多样性支配：",
     "第二，**失效是可解释的，而且是定量的。**增益与专家多样性同步变化："),
    ("代价则是训练时间增加约 80 倍、整批推理时间增加约 5.3 倍。",
     "代价则是训练时间增加约 80 倍、整批推理时间增加约 5.3 倍（十种子均值，表 4(a)）。"),
    ("该机制体积是单个等权森林的 4.1 倍、吞吐低 4.6 倍，没有代价敏感优势。",
     "该机制体积是单个等权森林的 4.1 倍、吞吐低 4.6 倍（单种子资源画像，S22），"
     "没有代价敏感优势。"),
    ("**资源占用。** 模型体积与吞吐率比墙钟时间更能区分两种设计。",
     "**资源占用**（单种子、完整测试批次，S22）。模型体积与吞吐率比墙钟时间更能区分两种设计。"),
    ("**延迟。** 单线程单条推理下，",
     "**延迟**（三个种子、7 986 条测试行，S15）。单线程单条推理下，"),
    ("差距在平衡控制协议上更大：训练 9.13 秒对 0.45 秒。",
     "差距在平衡控制协议上更大：训练 9.13 秒对 0.45 秒（三个种子，表 4(b)）。"),
    ("**同成员对照只覆盖主总体。**",
     "**多样性证据是相关性而非因果。** 剂量—反应关系建立在十五个构造的专家配置上，"
     "且使用三折交叉拟合；它表明增益与专家分歧同向变化，而不是证明分歧本身单独导致增益。"
     "我们没有做「固定分歧、只改变其余条件」的干预实验。\n\n"
     "**同成员对照只覆盖主总体。**"),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        if anchor not in text:
            # already applied, or superseded by a later trim; the guards at the
            # end of main() check that the intended wording is present
            continue
        head = replacement.strip()[:80]
        if head and head in text and not replacement.startswith(anchor):
            # insert-before-anchor edit that is already in place: the anchor is
            # still there, but the inserted text precedes it
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(anchor)} times: "
                             f"{anchor[:70]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    # repair pass: the insert-before-anchor edits were applied by every run of an
    # earlier version of this script, which left five copies of the limitation
    # paragraph; the run is collapsed back to a single copy here.
    repairs = {
        EN: ["**The diversity evidence is associational.** The dose-response relation rests on "
             "fifteen constructed expert configurations evaluated with three-fold cross-fitting; "
             "it shows that the gain moves with expert disagreement, not that disagreement alone "
             "causes a gain. No intervention that fixes disagreement while holding everything "
             "else constant was run."],
        ZH: ["**多样性证据是相关性而非因果。** 剂量—反应关系建立在十五个构造的专家配置上，"
             "且使用三折交叉拟合；它表明增益与专家分歧同向变化，而不是证明分歧本身单独导致增益。"
             "我们没有做「固定分歧、只改变其余条件」的干预实验。"],
    }
    for path, paragraphs in repairs.items():
        text = path.read_text(encoding="utf-8")
        removed = 0
        for paragraph in paragraphs:
            copies = text.count(paragraph)
            while copies > 1:
                run = (paragraph + "\n\n") * (copies - 1)
                if run in text:
                    text = text.replace(run, "", 1)
                    removed += copies - 1
                    break
                copies -= 1
        # unbalance introduced when the bold span of the Chinese 5.3 sentence was
        # split into two spans
        unbalanced = "门控在结构上不可能产生增益。** 当分歧率"
        if unbalanced in text:
            text = text.replace(unbalanced, "门控在结构上不可能产生增益。 当分歧率", 1)
            print(f"{path.name}: repaired the bold marker")
        if removed:
            print(f"{path.name}: removed {removed} duplicated paragraph(s)")
        path.write_text(text, encoding="utf-8")

    # the safer wording pushed the abstract four words over the JISA limit, so the
    # same sentences are tightened until it fits again
    abstract_trims: list[tuple[str, str]] = [
        ("across the fifteen configurations tested, the gain co-varies with expert diversity "
         "(slope 0.0646, r = 0.749, an association rather than an intervention).",
         "across fifteen configurations the gain co-varies with expert diversity (slope 0.0646, "
         "r = 0.749; an association, not an intervention)."),
        ("(single-seed resource profile, S22)", "(S22)"),
        ("at a 175-fold training cost; the IoT corpus saturates.",
         "at a 175-fold cost; the IoT corpus saturates."),
        ("the seed-level 90% and test-row paired bootstrap intervals both lie inside equivalence "
         "margins of 0.005 and 0.01.",
         "the seed-level 90% and paired bootstrap intervals lie inside equivalence margins of "
         "0.005 and 0.01."),
        ("All 108 gate configurations yield six distinct validation scores;",
         "All 108 gate configurations yield six distinct scores;"),
        ("All 108 gate configurations yield six distinct scores;",
         "108 gate configurations yield six distinct scores;"),
        ("with a median decision margin 3,469-5,038 times it",
         "with a median margin 3,469-5,038 times it"),
        ("where it becomes a small, consistent deficit (-0.005533, all ten seeds)",
         "where it becomes a consistent deficit (-0.005533, all ten seeds)"),
        ("r = 0.749; an association, not an intervention).",
         "r = 0.749; association, not intervention)."),
        ("The experts never disagree; weight entropy is 0.99998;",
         "Experts never disagree; weight entropy is 0.99998;"),
        ("the seed-level 90% and paired bootstrap intervals lie inside equivalence margins of "
         "0.005 and 0.01.",
         "the seed-level 90% and paired bootstrap intervals lie inside the 0.005 and 0.01 "
         "equivalence margins."),
    ]
    for path, edits in ((EN, EN_EDITS + abstract_trims), (ZH, ZH_EDITS)):
        applied = apply(path, edits)
        text = path.read_text(encoding="utf-8")
        for banned in ("governed by expert diversity", "受专家多样性支配"):
            if banned in text:
                raise SystemExit(f"{path.name}: causal wording survives: {banned!r}")
        print(f"{path.name}: {applied} edit(s) applied")
    abstract = EN.read_text(encoding="utf-8")
    abstract = abstract[abstract.index("## Abstract"):abstract.index("**Keywords:**")]
    words = len(abstract.split("## Abstract", 1)[1].split())
    print(f"English abstract: {words} words")
    if words > 250:
        raise SystemExit(f"abstract over the JISA limit: {words} words")
    print("LOGIC_SOFTSPOTS_FIXED")


if __name__ == "__main__":
    main()
