"""Insert the English Section 5.7 that the earlier pass missed.
The English heading is "## 6. Discussion" (with a period), so the anchor used
for the Chinese manuscript did not match.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"
SECTION = """### 5.7 Scale and domain sensitivity

The primary population is a capped subset, so the equivalence reported above could in principle be an artefact of that cap. Two further runs address the question directly.

**A population 7.8 times larger.** Rebuilding the CIC-IDS2017 population with the identical audit but a 200,000-per-class cap yields 413,209 flows (train 289,246 / validation 61,982 / test 61,982). The minority classes cannot grow, so the enlarged population is more imbalanced than the primary one: Brute Force contributes 10,620 rows, Bot 1,948 and Web Attack 673. The headline pair was re-run over the full ten seeds. RCCF averages 0.856065 Macro-F1 against 0.857202 for the equal-weight chi-square forest, a mean paired difference of -0.001137 (SD 0.003156; seed-level 90% interval [-0.002966, +0.000692]). TOST is significant at both pre-specified margins (p = 0.0019 at 0.005, p = 4.8e-6 at 0.01), so the equivalence statement survives a 7.8-fold increase in population size; the point estimate now favours the control slightly rather than RCCF. The two arms disagree on 20-29 of the 61,982 test rows per seed (0.03%-0.05%), the same order as on the primary population. The context baselines behave as before: XGBoost reaches 0.827656 Macro-F1, extremely randomised trees 0.783747, an equal-weight full-feature forest 0.852953 and a depth-limited decision tree 0.809695.

**A fourth dataset from a different domain.** N-BaIoT records benign traffic and Mirai/Gafgyt botnet activity from nine consumer IoT devices with 115 flow-statistics features [17,18]. Deduplication removes 4,784,430 of 7,062,606 rows (67.8%), a higher duplicate share than any other dataset here, leaving a 180,000-flow three-class benchmark (60,000 per class; train 126,000 / validation 27,000 / test 27,000). Every model reaches at least 0.99983 Macro-F1: RCCF and the equal-weight chi-square forest are identical to machine precision (mean difference -3.7e-17, with 0-2 disagreements among 27,000 test rows). The benchmark is saturated for flow-feature classifiers, which is precisely the regime in which Condition 1 predicts that no weighting can act: it confirms the mechanism's inertness in a new domain without testing discrimination difficulty.

Together the two runs bound the result from both sides: the equivalence is not an artefact of the 53,237-flow cap, and it reproduces in a domain whose classes are trivially separable.

"""
def main() -> None:
    text = EN.read_text(encoding="utf-8")
    if "### 5.7 Scale and domain sensitivity" in text:
        print("already inserted")
        return
    anchor = "## 6. Discussion"
    if anchor not in text:
        raise SystemExit("discussion anchor not found")
    EN.write_text(text.replace(anchor, SECTION + anchor, 1), encoding="utf-8")
    print("English Section 5.7 inserted")
if __name__ == "__main__":
    main()
