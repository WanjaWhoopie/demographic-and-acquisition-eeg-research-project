"""Loading every cohort into one common format.

Each cohort module exposes:

- ``load_participants(root, cfg) -> pandas.DataFrame`` with columns
  ``participant_id, diagnosis, age, sex, mmse`` (NaN where a cohort has no demographics);
- ``iter_segments(root, participants, cfg) -> Iterator[Segment]``.

A segment is one stretch of continuous EEG. Recordings that come as separate trials (APAVA) give
several segments per participant; filtering and epoching never cross a segment boundary (D-021).
"""
from dataclasses import dataclass, field

import numpy as np

COHORTS = ("ds004504", "ADFSU", "APAVA")


@dataclass
class Segment:
    cohort: str
    participant_id: str
    diagnosis: str
    condition: str
    sfreq: float
    ch_names: list
    data: np.ndarray            # (n_channels, n_samples), microvolts
    segment: int = 0
    meta: dict = field(default_factory=dict)


def get_loader(cohort):
    if cohort == "ds004504":
        from . import ds004504 as m
    elif cohort == "ADFSU":
        from . import adfsu as m
    elif cohort == "APAVA":
        from . import apava as m
    else:
        raise NotImplementedError(f"No loader for {cohort!r} (ADSZ is excluded, D-017).")
    return m
