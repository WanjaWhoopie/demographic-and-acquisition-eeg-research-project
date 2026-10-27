"""APAVA (Escudero et al., 2006): 23 participants, 16 channels, 256 Hz, separate 5-s eyes-closed trials.

Read from the team's APAVA.zip release (data/raw/APAVA): Feature/feature_NN.npy holds every 5-s trial
as nine 1-s windows (256 samples) with 50% overlap, shape (9 * n_trials, 256, 16); this module
rebuilds the 5-s trials (identical to the OSF FieldTrip copy, EXP report §3.4). Label/label.npy:
column 0 = 1 AD / 0 HC, column 1 = participant number. Values treated as microvolts (D-019).
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import Segment

COHORT = "APAVA"
SFREQ = 256.0
CH_NAMES = ["C3", "C4", "F3", "F4", "F7", "F8", "Fp1", "Fp2", "O1", "O2", "P3", "P4", "T3", "T4", "T5", "T6"]
WIN, STEP, N_WIN = 256, 128, 9          # 1-s windows, 50% overlap, nine per 5-s trial
TRIAL = STEP * (N_WIN - 1) + WIN        # 1280 samples = 5 s


def load_participants(root, cfg=None):
    lab = np.load(Path(root) / "Label" / "label.npy", allow_pickle=False)
    return pd.DataFrame({
        "participant_id": [f"{int(n):02d}" for n in lab[:, 1]],
        "diagnosis": ["AD" if v == 1 else "HC" for v in lab[:, 0]],
        "age": np.nan, "sex": None, "mmse": np.nan,
    })


def rebuild_trials(windows):
    """(9 * n_trials, 256, 16) overlapping windows -> (n_trials, 16, 1280) trials."""
    n = windows.shape[0] // N_WIN
    w = windows[: n * N_WIN].reshape(n, N_WIN, WIN, windows.shape[2])
    if not np.allclose(w[:, 1:, : WIN - STEP], w[:, :-1, STEP:]):
        raise ValueError("APAVA windows do not overlap by 50% as expected")
    trials = np.empty((n, TRIAL, windows.shape[2]))
    for k in range(N_WIN):
        trials[:, STEP * k: STEP * k + WIN] = w[:, k]
    return trials.transpose(0, 2, 1)


def iter_segments(root, participants, cfg=None):
    root = Path(root)
    dx = participants.set_index("participant_id")["diagnosis"]
    for pid in participants["participant_id"]:
        windows = np.load(root / "Feature" / f"feature_{pid}.npy", allow_pickle=False)
        for t, trial in enumerate(rebuild_trials(windows)):
            yield Segment(
                cohort=COHORT, participant_id=pid, diagnosis=dx[pid], condition="eyes_closed",
                sfreq=SFREQ, ch_names=list(CH_NAMES), data=trial, segment=t,
                meta={"file": f"feature_{pid}.npy"},
            )
