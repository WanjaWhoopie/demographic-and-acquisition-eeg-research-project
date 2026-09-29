"""Readers for the two releases of the Florida State University (Dennis Duke) AD database.

- ADFSU (osf.io/2v5md, Vicchietti et al., 2023): EEG_data/{AD,Healthy}/{Eyes_closed,Eyes_open}/PacienteN/<channel>.txt,
  one 1024-sample (8 s at 128 Hz) column per channel file.
- ADSZ (figshare 19091771, Alves et al.): dataset/alzheimer/{AD,Healthy}/<name>.out, 1024 rows x 19 columns,
  no channel header. AD files are named e{c,o}CCSS (code CC, segment SS); healthy files eegNN{c,o}1.

Amplitudes are returned as stored; the unit is not documented (audit A5 checks plausibility).
"""
import re
from pathlib import Path

import numpy as np

SFREQ = 128.0
DIAGNOSIS = {"AD": "AD", "Healthy": "HC"}


def read_adfsu(root):
    """Yield dicts: participant_id, diagnosis, condition, ch_names, data (n_ch, n_samples)."""
    base = Path(root) / "EEG_data"
    for group in ("AD", "Healthy"):
        for cond_dir, cond in (("Eyes_closed", "eyes_closed"), ("Eyes_open", "eyes_open")):
            for folder in sorted((base / group / cond_dir).glob("Paciente*"), key=lambda p: int(p.name[8:])):
                files = sorted(folder.glob("*.txt"))
                if not files:  # e.g. Healthy/Eyes_open/Paciente5 is empty in the release
                    continue
                yield {
                    "cohort": "ADFSU",
                    "participant_id": f"{DIAGNOSIS[group]}-{int(folder.name[8:]):02d}",
                    "diagnosis": DIAGNOSIS[group],
                    "condition": cond,
                    "recording": f"{group}/{cond_dir}/{folder.name}",
                    "ch_names": [f.stem for f in files],
                    "data": np.vstack([np.loadtxt(f) for f in files]),
                }


_AD = re.compile(r"e([co])(\d{2})(\d{2})$")
_HC = re.compile(r"eeg(\d+)([co])1$")


def read_adsz(root):
    """Yield dicts as read_adfsu; channel names are unknown (col01..col19)."""
    base = Path(root) / "dataset" / "alzheimer"
    for group in ("AD", "Healthy"):
        for f in sorted((base / group).glob("*.out")):
            m = (_AD if group == "AD" else _HC).match(f.stem)
            if group == "AD":
                cond, code, seg = m.group(1), m.group(2), m.group(3)
            else:
                code, cond, seg = m.group(1), m.group(2), "01"
            data = np.loadtxt(f).T
            yield {
                "cohort": "ADSZ",
                "participant_id": f"{DIAGNOSIS[group]}-{code}",
                "segment": seg,
                "diagnosis": DIAGNOSIS[group],
                "condition": "eyes_closed" if cond == "c" else "eyes_open",
                "recording": f"{group}/{f.name}",
                "ch_names": [f"col{i + 1:02d}" for i in range(data.shape[0])],
                "data": data,
            }
