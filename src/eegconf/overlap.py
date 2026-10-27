"""Cross-cohort duplicate detection (WORKPLAN Phase 3, EXP-002).

Problem: two public releases (ADSZ, ADFSU) may contain the same recordings, but with different
file formats, channel orders, channel names, rounding, or segment lengths. Comparing whole
recordings would miss copies whose channels are reordered, so the comparison is done one channel
time series at a time:

1. exact: the channel's sample vector (rounded to `decimals`) appears in a recording of the other
   release; implemented by hashing every channel of release B once and looking hashes up;
2. near: the channel correlates at |r| > NEAR_R with some channel of a B recording (catches
   rescaled, sign-flipped or re-rounded copies that an exact hash would miss).

A recording of A "matches" a recording of B when at least MIN_CHANNEL_SHARE of its channels have
a copy in that *one* B recording. Recordings of A longer than B's are scanned window by window,
because a release may keep a longer stretch of the same recording.

Inputs are plain dicts with keys `recording` (name), `ch_names` and `data` (n_ch, n_samples), as
produced by eegconf.io.fsu. Nothing here depends on the channel names.
"""
import hashlib
from collections import Counter, defaultdict

import numpy as np

NEAR_R = 0.999           # a rescaled copy of a channel still correlates ~1; unrelated EEG channels ~0-0.9
MIN_CHANNEL_SHARE = 0.8  # fraction of a recording's channels that must match one other recording


def channel_hash(x, decimals=3):
    """SHA-1 of a channel's samples rounded to `decimals`, so tiny formatting differences
    (e.g. 1.9231 vs 1.92310) still hash equal while different signals never do."""
    return hashlib.sha1(np.round(np.asarray(x, dtype=float), decimals).tobytes()).hexdigest()


def _windows(data, length, step):
    """Sub-recordings of `length` samples; recordings longer than B's may contain a B recording anywhere."""
    n = data.shape[1]
    if n <= length:
        yield 0, data
        return
    for off in range(0, n - length + 1, step):
        yield off, data[:, off:off + length]


def _b_length(recs_b):
    lengths = {rb["data"].shape[1] for rb in recs_b}
    assert len(lengths) == 1, f"B recordings must share one length, got {lengths}"
    return lengths.pop()


def exact_matches(recs_a, recs_b, decimals=3):
    """For each recording in A: (index of the B recording sharing the most identical channels, share, offset).

    A recordings longer than B are scanned at every sample offset."""
    length = _b_length(recs_b)
    index = defaultdict(set)
    for j, rb in enumerate(recs_b):
        for ch in rb["data"]:
            index[channel_hash(ch, decimals)].add(j)
    out = []
    for ra in recs_a:
        best = (None, 0.0, 0)
        for off, win in _windows(ra["data"], length, 1):
            counts = Counter()
            for ch in win:
                for j in index.get(channel_hash(ch, decimals), ()):
                    counts[j] += 1
            if counts:
                j, n = counts.most_common(1)[0]
                if n / len(win) > best[1]:
                    best = (j, n / len(win), off)
        out.append(best)
    return out


def _z(M):
    """Centre and unit-normalise each row so that A @ B.T gives Pearson correlations."""
    M = M - M.mean(axis=1, keepdims=True)
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)


def near_matches(recs_a, recs_b, step=16):
    """For each recording in A: (index of the B recording with the most channels correlating above NEAR_R, share, offset).

    Longer A recordings are scanned every `step` samples (a misaligned copy correlates less, so
    exact_matches, which scans every sample, is the primary test)."""
    length = _b_length(recs_b)
    B = np.vstack([rb["data"] for rb in recs_b])
    owner = np.concatenate([[j] * len(rb["data"]) for j, rb in enumerate(recs_b)])
    Bz = _z(B)
    out = []
    for ra in recs_a:
        best = (None, 0.0, 0)
        for off, win in _windows(ra["data"], length, step):
            r = np.abs(_z(win) @ Bz.T)          # (channels_a, channels_b)
            top = r.argmax(axis=1)
            hit = r[np.arange(len(top)), top] > NEAR_R
            counts = Counter(owner[top[hit]])
            if counts:
                j, n = counts.most_common(1)[0]
                if n / len(win) > best[1]:
                    best = (j, n / len(win), off)
        out.append(best)
    return out


def channel_map(rec_a, rec_b, offset=0):
    """Which channel of rec_b each channel of rec_a copies (by max |r|), with the correlation."""
    a = rec_a["data"][:, offset:offset + rec_b["data"].shape[1]]
    r = np.abs(_z(a) @ _z(rec_b["data"]).T)
    best = r.argmax(axis=1)
    return [(rec_a["ch_names"][i], rec_b["ch_names"][b], float(r[i, b])) for i, b in enumerate(best)]
