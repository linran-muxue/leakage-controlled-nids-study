"""Guard the supplementary-bundle registration path.

Adding S29 rewrites ``assemble_supplementary_v5.py`` with a textual insertion,
and five other scripts derive the bundle directory name from that file.  A
malformed insertion or a stale resolver would only surface during the final
release, so the whole chain is checked here.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from supplementary_paths_v1 import latest_bundle_name  # noqa: E402

ASSEMBLER = ROOT / "scripts" / "assemble_supplementary_v5.py"
S28_TAIL = '             "results_rccf_nbaiot_v48/metrics_by_seed.csv"]),\n'
S29_ITEM = ('    "S29": ("全语料规模运行：2 429 503 条、逐种子指标与配对比较",\n'
            '            ["results_full_corpus_v49/full_corpus_paired_by_seed.csv",\n'
            '             "results_full_corpus_v49/full_corpus_summary.json",\n'
            '             "results_full_corpus_v49/metrics_by_seed.csv",\n'
            '             "results_rccf_cic_natural_v4_full/metrics_by_seed.csv"]),\n')


def _items(source: str) -> dict:
    # ``__file__`` is used by the assembler to locate the repository root, so it
    # has to be supplied explicitly when the module is executed from a string.
    namespace: dict = {"__file__": str(ASSEMBLER), "__name__": "assembler_under_test"}
    exec(compile(source, "assembler", "exec"), namespace)
    return namespace["ITEMS"]


def test_registered_items_derive_the_bundle_name() -> None:
    source = ASSEMBLER.read_text(encoding="utf-8")
    items = _items(source)
    expected = f"补充材料_S01_S{max(int(key[1:]) for key in items):02d}"
    assert expected == latest_bundle_name()


def test_s29_insertion_keeps_the_module_valid() -> None:
    source = ASSEMBLER.read_text(encoding="utf-8")
    if '"S29"' in source:
        return  # already registered by the release pipeline
    assert S28_TAIL in source
    simulated = source.replace(S28_TAIL, S28_TAIL + S29_ITEM, 1)
    ast.parse(simulated)
    items = _items(simulated)
    assert list(items)[-1] == "S29", "S29 must be appended last so the index stays ordered"
    assert len(items["S29"][1]) == 4
    assert f"补充材料_S01_S{max(int(k[1:]) for k in items):02d}" == "补充材料_S01_S29"


def test_every_registered_source_exists_or_is_produced_by_the_pipeline() -> None:
    """Sources must exist now, except the two written by finalize_full_corpus."""
    produced = {
        "results_full_corpus_v49/full_corpus_paired_by_seed.csv",
        "results_full_corpus_v49/full_corpus_summary.json",
    }
    items = _items(ASSEMBLER.read_text(encoding="utf-8"))
    missing = [
        source
        for _, sources in items.values()
        for source in sources
        if source not in produced and not (ROOT / source).exists()
    ]
    assert not missing, f"supplementary sources missing: {missing}"
