"""Loading raw recordings from each cohort into a common in-memory format (MNE Raw/Epochs) plus a participants table.

Every cohort module exposes the same two functions:

- ``load_participants(root) -> pandas.DataFrame`` with columns
  ``participant_id, diagnosis, age, sex, mmse`` (NaN where a cohort has no demographics);
- ``iter_recordings(root, participants) -> Iterator[Recording]``.
"""
from dataclasses import dataclass, field
from pathlib import Path

import mne


@dataclass
class Recording:
    cohort: str
    participant_id: str
    path: Path
    raw: mne.io.BaseRaw
    sidecar: dict = field(default_factory=dict)  # acquisition metadata (BIDS *_eeg.json or equivalent)


def get_loader(cohort):
    if cohort == "ds004504":
        from . import ds004504
        return ds004504
    raise NotImplementedError(
        f"No loader for {cohort!r} yet: its source and file format are still being traced (WORKPLAN T2.2-T2.4)."
    )
