"""ADFSU (osf.io/2v5md): FSU / Dennis Duke database, one 8-s recording per participant and condition.

Cleaning from EXP-002 is applied here: duplicate IDs (AD-41..44 = AD-40) are excluded and the
F1/F2 files (copies of Fp1/Fp2) are dropped, both read from configs/datasets.yaml.
Stored values are treated as microvolts (undocumented; D-019).
"""
import numpy as np
import pandas as pd

from . import Segment
from .fsu import SFREQ, read_adfsu

COHORT = "ADFSU"


def _cfg(cfg):
    cfg = cfg or {}
    return set(cfg.get("exclude_participants", [])), set(cfg.get("drop_channels", ["F1", "F2"]))


def load_participants(root, cfg=None):
    exclude, _ = _cfg(cfg)
    seen = {}
    for r in read_adfsu(root):
        if r["participant_id"] not in exclude:
            seen[r["participant_id"]] = r["diagnosis"]
    return pd.DataFrame({
        "participant_id": list(seen), "diagnosis": list(seen.values()),
        "age": np.nan, "sex": None, "mmse": np.nan,
    })


def iter_segments(root, participants, cfg=None, condition="eyes_closed"):
    exclude, drop = _cfg(cfg)
    wanted = set(participants["participant_id"])
    for r in read_adfsu(root):
        pid = r["participant_id"]
        if pid in exclude or pid not in wanted or r["condition"] != condition:
            continue
        keep = [i for i, c in enumerate(r["ch_names"]) if c not in drop]
        yield Segment(
            cohort=COHORT, participant_id=pid, diagnosis=r["diagnosis"], condition=r["condition"],
            sfreq=SFREQ, ch_names=[r["ch_names"][i] for i in keep], data=r["data"][keep],
            meta={"file": r["recording"]},
        )
