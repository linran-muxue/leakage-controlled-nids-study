"""Cross-language parity and numeric traceability checks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")

KEY_NUMBERS = [
    "0.889955", "0.888870", "0.887960", "0.857713", "0.797654",
    "0.001085", "0.508", "0.092", "0.344", "0.215", "0.00061",
    "99.91", "0.000231", "3469", "5038", "0.00117", "0.0075",
    "0.0646", "0.749", "0.00271", "0.00332", "0.00401",
    "0.961807", "0.963215", "0.007755", "0.0719", "0.00141",
    "0.747960", "0.514697", "0.715340", "0.493310",
    "53,237", "3,365", "23,958", "0.99998", "0.01262", "0.000299", "0.003473",
]

print("=== key numbers present in each language ===")
missing_zh = [n for n in KEY_NUMBERS if n not in ZH]
missing_en = [n for n in KEY_NUMBERS if n not in EN]
print("missing in zh:", missing_zh or "none")
print("missing in en:", missing_en or "none")

print()
print("=== heading parity ===")
zh_heads = re.findall(r"^#{2,3}\s+(.*)$", ZH, flags=re.M)
en_heads = re.findall(r"^#{2,3}\s+(.*)$", EN, flags=re.M)
print(f"zh headings: {len(zh_heads)}, en headings: {len(en_heads)}")
zh_top = [h for h in zh_heads if re.match(r"^\d+\s", h)]
en_top = [h for h in en_heads if re.match(r"^\d+\.\s", h)]
print("zh top-level sections:", len(zh_top))
print("en top-level sections:", len(en_top))

print()
print("=== measurement-count phrasing ===")
for doc, label in ((ZH, "zh"), (EN, "en")):
    n_meas = len(re.findall(r"测量[一二三四五六七八九]|Measurement \d", doc))
    print(f"  {label}: actual measurement blocks = {n_meas}")

print()
print("=== supplementary list size ===")
for doc, label in ((ZH, "zh"), (EN, "en")):
    s = re.findall(r"\|\s*S\d+\s*\|", doc)
    print(f"  {label}: {len(s)} supplementary rows")
