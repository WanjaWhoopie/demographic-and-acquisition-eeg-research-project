"""OpenNeuro ds004504 (AHEPA): BIDS, one eyes-closed EEGLAB recording per participant."""
import json
from pathlib import Path

import mne
import pandas as pd

from . import Segment

COHORT = "ds004504"
GROUP_TO_DIAGNOSIS = {"A": "AD", "C": "HC", "F": "FTD"}


def load_participants(root, cfg=None, groups=("A", "C")):
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


def iter_segments(root, participants, cfg=None):
    root = Path(root)
    dx = participants.set_index("participant_id")["diagnosis"]
    for pid in participants["participant_id"]:
        for f in sorted((root / pid / "eeg").glob(f"{pid}_task-*_eeg.set")):
            sidecar_path = f.with_name(f.name.replace("_eeg.set", "_eeg.json"))
            sidecar = json.loads(sidecar_path.read_text()) if sidecar_path.exists() else {}
            raw = mne.io.read_raw_eeglab(f, preload=True, verbose="error")
            picks = mne.pick_types(raw.info, eeg=True)
            yield Segment(
                cohort=COHORT, participant_id=pid, diagnosis=dx[pid],
                condition="eyes_closed" if sidecar.get("TaskName") == "eyesclosed" else sidecar.get("TaskName", ""),
                sfreq=float(raw.info["sfreq"]),
                ch_names=[raw.ch_names[i] for i in picks],
                data=raw.get_data(picks=picks) * 1e6,
                meta={"file": f.name, "reference": sidecar.get("EEGReference", ""),
                      "online_filter": str(sidecar.get("SoftwareFilters", "")),
                      "line_freq": sidecar.get("PowerLineFrequency")},
            )
