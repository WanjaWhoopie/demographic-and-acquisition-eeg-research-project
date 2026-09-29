"""OpenNeuro ds004504 (AHEPA): BIDS, one eyes-closed EEGLAB recording per participant."""
import json
from pathlib import Path

import mne
import pandas as pd

from . import Recording

COHORT = "ds004504"
GROUP_TO_DIAGNOSIS = {"A": "AD", "C": "HC", "F": "FTD"}


def load_participants(root, groups=("A", "C")):
    df = pd.read_csv(Path(root) / "participants.tsv", sep="\t")
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Group"].isin(groups)].copy()
    return pd.DataFrame({
        "participant_id": df["participant_id"].str.strip(),
        "diagnosis": df["Group"].map(GROUP_TO_DIAGNOSIS),
        "age": df["Age"].astype(float),
        "sex": df["Gender"].str.strip(),
        "mmse": pd.to_numeric(df["MMSE"], errors="coerce"),
    }).reset_index(drop=True)


def iter_recordings(root, participants):
    root = Path(root)
    for pid in participants["participant_id"]:
        files = sorted((root / pid / "eeg").glob(f"{pid}_task-*_eeg.set"))
        if not files:
            yield Recording(COHORT, pid, root / pid, raw=None, sidecar={"missing": True})
            continue
        for f in files:
            sidecar_path = f.with_name(f.name.replace("_eeg.set", "_eeg.json"))
            sidecar = json.loads(sidecar_path.read_text()) if sidecar_path.exists() else {}
            raw = mne.io.read_raw_eeglab(f, preload=True, verbose="error")
            yield Recording(COHORT, pid, f, raw, sidecar)
