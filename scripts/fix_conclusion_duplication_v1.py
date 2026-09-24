"""Remove the second copy of the uncapped-corpus claim from the conclusion.

Section 7 of the English manuscript stated the same two facts twice inside one
paragraph:

    ... the same comparison turns into a consistent deficit of -0.005533 across
    all ten seeds, at a 175-fold training cost. ... That equivalence is a
    property of the population, not of the mechanism: on the fully uncapped
    2,429,503-flow corpus the difference turns into a consistent deficit of
    -0.005533 (all ten seeds, equivalent at 0.01 but not at 0.005) at a
    175-fold training cost.

The second sentence is the tail of a rewrite that was never deleted; it keeps 47
characters of the first verbatim and 54 with the opening claim.  The exact-match
guard (``check_duplicate_sentences_v27.py``) cannot see it, and the duplicates
therefore survived into the submission draft while the self-check table claimed
that no paragraph repeats a set of decimals.

The only information the second copy carries that the first does not is the TOST
verdict, so that verdict is folded into the first sentence rather than dropped.
Every value is asserted against ``results_full_corpus_v49/full_corpus_summary.json``
before the edit.  The Chinese conclusion states the claim once and already
carries the TOST verdict, so only the English manuscript changes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SUMMARY = ROOT / "results_full_corpus_v49" / "full_corpus_summary.json"

OLD = ("On the fully uncapped 2,429,503-flow corpus the same comparison turns into "
       "a consistent deficit of -0.005533 across all ten seeds, at a 175-fold training "
       "cost. The cause is not the weighting - Section 5.3 shows the weights never move "
       "a label - but the price of averaging over feature views whose quality diverges "
       "at scale: the full-feature view falls 0.021397 behind the chi-square view, and "
       "one such expert inside a four-way average accounts for the whole gap (0.005349 "
       "predicted against -0.005533 measured). That equivalence is a property of the "
       "population, not of the mechanism: on the fully uncapped 2,429,503-flow corpus "
       "the difference turns into a consistent deficit of -0.005533 (all ten seeds, "
       "equivalent at 0.01 but not at 0.005) at a 175-fold training cost.")

NEW = ("On the fully uncapped 2,429,503-flow corpus the same comparison turns into "
       "a consistent deficit of -0.005533 across all ten seeds (equivalent at 0.01 but "
       "not at 0.005), at a 175-fold training cost. The cause is not the weighting - "
       "Section 5.3 shows the weights never move a label - but the price of averaging "
       "over feature views whose quality diverges at scale: the full-feature view falls "
       "0.021397 behind the chi-square view, and one such expert inside a four-way "
       "average accounts for the whole gap (0.005349 predicted against -0.005533 "
       "measured).")

DELETED = ("That equivalence is a property of the population, not of the mechanism: "
           "on the fully uncapped 2,429,503-flow corpus")


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if abs(summary["mean_difference"] - (-0.005532805069742508)) > 1e-12:
        raise SystemExit(f"source changed: mean_difference = {summary['mean_difference']}")
    if summary["n_seeds"] != 10:
        raise SystemExit(f"source changed: n_seeds = {summary['n_seeds']}")
    tost = summary["tost"]
    if tost["0.005"]["equivalent"] or not tost["0.01"]["equivalent"]:
        raise SystemExit(f"source changed: tost verdicts {tost}")
    if abs(summary["train_slowdown"] - 175.08864037142965) > 1e-9:
        raise SystemExit(f"source changed: train_slowdown = {summary['train_slowdown']}")
    print(f"source: deficit {summary['mean_difference']:.6f}, "
          f"slowdown {summary['train_slowdown']:.2f}x, "
          f"equivalent at 0.01={tost['0.01']['equivalent']}, "
          f"at 0.005={tost['0.005']['equivalent']}")

    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        if name.startswith("English"):
            if OLD in text:
                if text.count(OLD) != 1:
                    raise SystemExit(f"anchor not found exactly once in {name}")
                text = text.replace(OLD, NEW, 1)
                (BASE / name).write_text(text, encoding="utf-8")
                print(f"updated {name}")
            elif NEW in text:
                print(f"{name}: already fixed")
            else:
                raise SystemExit(f"neither the old nor the new paragraph is present in {name}")
        elif DELETED in text:
            raise SystemExit(f"{name} carries the duplicated claim too; extend the fix")

    english = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    for phrase in ("(equivalent at 0.01 but not at 0.005)", "175-fold training cost",
                   "0.005349"):
        if phrase not in english:
            raise SystemExit(f"the edit dropped {phrase!r}")
    paragraph = next((line for line in english.splitlines()
                      if line.startswith("**A qualification on that equivalence.**")), "")
    if paragraph.count("-0.005533") != 2:
        raise SystemExit("the qualification paragraph should state the deficit exactly "
                         f"twice (result and dilution arithmetic), found "
                         f"{paragraph.count('-0.005533')}")
    if paragraph.count("property of the population, not of the mechanism") != 1:
        raise SystemExit("the qualification still repeats its opening claim")
    print("CONCLUSION_DUPLICATION_FIXED")


if __name__ == "__main__":
    main()
