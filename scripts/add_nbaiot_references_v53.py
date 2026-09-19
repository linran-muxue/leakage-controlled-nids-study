"""Insert the N-BaIoT references as [17] and [18] and shift the rest.
The list stays in citation order, so every existing entry from 17 upwards moves
by two. The two citations added by the Section 5.7 pass are parked behind
placeholders first, otherwise they would be shifted along with the old ones.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
FILES = {"English_SCI_Manuscript_v4.md": "## References",
         "中文SCI论文_v4_重构版.md": "## 参考文献"}
NEW_ENTRIES = [
    "17. Meidan Y, Bohadana M, Mathov Y, et al. N-BaIoT - Network-based detection of IoT botnet "
    "attacks using deep autoencoders. IEEE Pervasive Computing, 2018, 17(3): 12-22. "
    "DOI:10.1109/MPRV.2018.03367731.",
    "18. UCI Machine Learning Repository. Detection of IoT botnet attacks N-BaIoT [dataset]. "
    "2018. DOI:10.24432/C5RC8J.",
]
CITATION = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
SHIFT_FROM = 17


def shift_group(group: str) -> str:
    parts = re.split(r"([,\-])", group)
    out = []
    for part in parts:
        if part.strip().isdigit():
            value = int(part)
            out.append(str(value + 2) if value >= SHIFT_FROM else str(value))
        else:
            out.append(part)
    return "".join(out)


def process(name: str, marker: str) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    body, sep, refs = text.partition(marker)
    body = body.replace("[14-18]", "[[DS4]]").replace("[17,18]", "[[NB]]")
    body = CITATION.sub(lambda m: "[" + shift_group(m.group(1)) + "]", body)
    body = body.replace("[[DS4]]", "[14-18]").replace("[[NB]]", "[17,18]")

    lines = refs.splitlines()
    shifted = []
    for line in lines:
        match = re.match(r"^(\d+)\.\s", line)
        if match and int(match.group(1)) >= SHIFT_FROM:
            line = re.sub(r"^\d+\.", f"{int(match.group(1)) + 2}.", line, count=1)
        shifted.append(line)
    refs = "\n".join(shifted)
    anchor = re.search(r"^16\. .*$", refs, flags=re.M)
    if not anchor:
        raise SystemExit(f"entry 16 not found in {name}")
    refs = refs[:anchor.end()] + "\n" + "\n".join(NEW_ENTRIES) + refs[anchor.end():]
    path.write_text(body + sep + refs, encoding="utf-8")
    numbers = re.findall(r"^(\d+)\.\s", refs, flags=re.M)
    print(f"{name}: references now 1-{max(int(n) for n in numbers)}, count={len(numbers)}")


def main() -> None:
    for name, marker in FILES.items():
        process(name, marker)


if __name__ == "__main__":
    main()
