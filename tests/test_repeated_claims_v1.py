"""The paraphrase detector must separate an accident from a deliberate contrast.

The threshold in ``scripts/check_repeated_claims_v1.py`` is calibrated on the
manuscripts, so these tests pin the two calls that set it: the duplicated pair
that was removed from the conclusion, and the legitimate Section 5.2 contrast
that must not be flagged.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_repeated_claims_v1", ROOT / "scripts" / "check_repeated_claims_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


claims = _load()


def test_identical_sentences_share_their_whole_length() -> None:
    sentence = "Weights never move a label on this population."
    size, sample = claims.longest_common_run(sentence, sentence)
    assert size == len(sentence)
    assert sample == sentence


def test_the_removed_duplication_is_over_the_threshold() -> None:
    first = ("On the fully uncapped 2,429,503-flow corpus the same comparison turns "
             "into a consistent deficit of -0.005533 across all ten seeds.")
    second = ("That equivalence is a property of the population, not of the mechanism: "
              "on the fully uncapped 2,429,503-flow corpus the difference turns into a "
              "consistent deficit of -0.005533 at a 175-fold training cost.")
    size, _ = claims.longest_common_run(first, second)
    assert size >= claims.MIN_RUN


def test_a_legitimate_contrast_stays_below_the_threshold() -> None:
    first = ("On the natural-prior population over ten seeds the difference is "
             "-0.000456.")
    second = ("On the balanced control population over three seeds the difference is "
              "-0.001408.")
    size, _ = claims.longest_common_run(first, second)
    assert size < claims.MIN_RUN
