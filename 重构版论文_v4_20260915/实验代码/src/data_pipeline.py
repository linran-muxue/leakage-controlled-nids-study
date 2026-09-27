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


def cic_physical_valid_mask(frame: pd.DataFrame):
    """Return a conservative physical-range mask for CICFlowMeter fields.

    The CIC files contain a small number of malformed negative values.  The
    two TCP initial-window fields legitimately use ``-1`` as an unavailable
    value, so that sentinel is retained; other duration, rate, length and
    header fields must be non-negative.  Missing columns are ignored to keep
    the helper usable with reduced test fixtures.
    """
    rules = {
        "Flow Duration": 0.0,
        "Total Fwd Packets": 0.0,
        "Total Backward Packets": 0.0,
        "Total Length of Fwd Packets": 0.0,
        "Total Length of Bwd Packets": 0.0,
        "Flow Bytes/s": 0.0,
        "Flow Packets/s": 0.0,
        "Flow IAT Mean": 0.0,
        "Flow IAT Std": 0.0,
        "Flow IAT Max": 0.0,
        # CICFlowMeter uses -1 when an inter-arrival minimum is undefined for
        # a one-packet flow; values below that sentinel are malformed.
        "Flow IAT Min": -1.0,
        "Fwd IAT Total": 0.0,
        "Fwd IAT Mean": 0.0,
        "Fwd IAT Std": 0.0,
        "Fwd IAT Max": 0.0,
        "Fwd IAT Min": 0.0,
        "Bwd IAT Total": 0.0,
        "Bwd IAT Mean": 0.0,
        "Bwd IAT Std": 0.0,
        "Bwd IAT Max": 0.0,
        "Bwd IAT Min": 0.0,
        "Fwd Header Length": 0.0,
        "Bwd Header Length": 0.0,
        "Fwd Header Length.1": 0.0,
        "Fwd Packets/s": 0.0,
        "Bwd Packets/s": 0.0,
        "Min Packet Length": 0.0,
        "Max Packet Length": 0.0,
        "Packet Length Mean": 0.0,
        "Packet Length Std": 0.0,
        "Packet Length Variance": 0.0,
        "Down/Up Ratio": 0.0,
        "min_seg_size_forward": 0.0,
    }
    mask = pd.Series(True, index=frame.index)
    by_feature = {}
    for column, minimum in rules.items():
        if column not in frame.columns:
            continue
        invalid = pd.to_numeric(frame[column], errors="coerce") < minimum
        by_feature[column] = int(invalid.sum())
        mask &= ~invalid
    return mask, by_feature
