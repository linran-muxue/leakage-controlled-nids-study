from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def map_attack_label(label: object, include_other: bool = False) -> Optional[str]:
    """Map a raw CIC-IDS2017 label to the paper's class scheme.

    The source CSVs contain leading spaces and, in some encodings, a replacement
    character in the en-dash used by Web Attack labels. Matching is therefore
    intentionally based on normalized lowercase substrings.
    """
    if label is None or (isinstance(label, float) and np.isnan(label)):
        return None
    raw = str(label).strip()
    key = raw.lower().replace("–", "-").replace("—", "-")

    if key == "benign":
        return "Normal"
    if key == "bot":
        return "Bot"
    if key == "ddos" or key.startswith("dos ") or key.startswith("dos-"):
        return "DoS/DDoS"
    if key in {"ftp-patator", "ssh-patator"}:
        return "Brute Force"
    if "web attack" in key and "brute" in key:
        return "Brute Force"
    if "web attack" in key and ("xss" in key or "sql" in key):
        return "Web Attack"
    if include_other:
        return "Other"
    return None


def clean_numeric_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Replace infinities with missing values and drop invalid rows."""
    cleaned = frame.copy()
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
    return cleaned.dropna(axis=0, how="any").reset_index(drop=True)
