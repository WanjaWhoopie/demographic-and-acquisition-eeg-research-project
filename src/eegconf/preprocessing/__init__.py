"""Harmonised preprocessing (WORKPLAN Phase 4).

Every cohort goes through exactly the same steps, in this order, so that what differs between
cohorts afterwards is what the recordings contained, not what we did to them:

1. pick_channels   – the 16 channels common to all cohorts, in one fixed order (T4.2)
2. (units)         – loaders already deliver microvolts (T4.3; D-019 for the undocumented ones)
3. bandpass        – 0.5–30 Hz, 4th-order Butterworth, zero-phase, per continuous segment (D-020)
4. rereference     – common average over the 16 channels (D-012)
5. resample        – to 200 Hz, LaBraM's input rate (polyphase, exact rational ratios)
6. epoch           – non-overlapping 4-s epochs that never cross a segment boundary (D-021)
7. reject          – drop epochs with any channel peak-to-peak > 150 µV or < 0.5 µV (D-013)

All functions are pure NumPy/SciPy on (n_channels, n_samples) arrays in microvolts, so each
step is unit-tested in tests/test_preprocessing.py. `preprocess_participant` chains them for
one participant's list of segments and returns the epochs plus a bookkeeping dict.

What is deliberately *not* done here: ICA (segments too short; D-013), notch filtering (mains
lies above 30 Hz; D-014), equal-length cropping (all clean epochs are kept, D-018; the 8-s
sensitivity analysis selects the first two epochs at analysis time using `epoch_idx`).
"""
from fractions import Fraction

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt

from eegconf.audit import canonical

TARGET_SFREQ = 200.0


# ----------------------------------------------------------------------------- 1. channels
# Old and new 10-20 names for the same electrodes. Canonical names are the old ones
# (configs/preprocessing.yaml); datasets using T7/T8/P7/P8 are mapped onto them.
ALIASES = {"T7": "T3", "T8": "T4", "P7": "T5", "P8": "T6"}


def pick_channels(data, ch_names, target):
    """Return (data, names) restricted to `target` channels in `target` order.

    Matching ignores case, 'EEG '/'-REF' decorations and the T7/T3-style aliases. Raises if a
    target channel is absent, because silently filling it would create a cohort-specific
    difference. Dropped channels (Fz, Cz, Pz, duplicates) are simply left out.
    """
    lookup = {}
    for i, name in enumerate(ch_names):
        c = canonical(name)
        lookup.setdefault(ALIASES.get(c, c), i)
    missing = [t for t in target if canonical(t) not in lookup]
    if missing:
        raise ValueError(f"target channels missing: {missing}; have {ch_names}")
    idx = [lookup[canonical(t)] for t in target]
    return data[idx], list(target)


# ----------------------------------------------------------------------------- 3. filter
def bandpass(data, sfreq, l_freq=0.5, h_freq=30.0, order=4):
    """Zero-phase Butterworth band-pass applied forward and backward (no phase distortion).

    Second-order sections keep the filter numerically stable at 0.5 Hz / 500 Hz. Applied per
    continuous segment: the caller must not concatenate trials before filtering.
    """
    sos = butter(order, [l_freq, h_freq], btype="bandpass", fs=sfreq, output="sos")
    return sosfiltfilt(sos, data, axis=1)


# ----------------------------------------------------------------------------- 4. reference
def rereference(data):
    """Common average reference: subtract the mean over channels at every sample.

    Done after channel selection so every cohort's average is over the same 16 channels.
    Removes the cohort-specific original reference (linked ears / linked mandible / average).
    """
    return data - data.mean(axis=0, keepdims=True)


# ----------------------------------------------------------------------------- 5. resample
def resample(data, sfreq, target=TARGET_SFREQ):
    """Polyphase resampling by the exact rational ratio target/sfreq (500→200 = 2/5, 128→200 =
    25/16, 256→200 = 25/32). Anti-aliasing is already guaranteed by the 30-Hz low-pass, but
    resample_poly applies its own FIR as well. Returns data at `target` Hz."""
    if sfreq == target:
        return data
    r = Fraction(target / sfreq).limit_denominator(1000)
    return resample_poly(data, r.numerator, r.denominator, axis=1)


# ----------------------------------------------------------------------------- 6. epochs
def epoch(data, sfreq, length_s=4.0):
    """Cut one continuous segment into consecutive non-overlapping epochs of `length_s`.

    The incomplete tail is dropped. A 5-s APAVA trial gives one epoch, an 8-s ADFSU recording
    two, a 13-min ds004504 recording ~195. Returns (n_epochs, n_channels, n_samples)."""
    n = int(round(length_s * sfreq))
    k = data.shape[1] // n
    return data[:, : k * n].reshape(data.shape[0], k, n).transpose(1, 0, 2)


# ----------------------------------------------------------------------------- 7. rejection
def reject(epochs, ptp_max=150.0, ptp_min=0.5):
    """Boolean mask of epochs to keep, and the reason each rejected epoch failed.

    An epoch is rejected if ANY channel's peak-to-peak amplitude exceeds `ptp_max` (artefact:
    eye movement, muscle, electrode pop) or falls below `ptp_min` (flat: disconnected channel).
    The same thresholds apply to every cohort; they act on filtered, re-referenced data.
    """
    ptp = epochs.max(axis=2) - epochs.min(axis=2)          # (n_epochs, n_channels)
    too_big = (ptp > ptp_max).any(axis=1)
    too_flat = (ptp < ptp_min).any(axis=1)
    keep = ~(too_big | too_flat)
    reason = np.where(too_big, "ptp_max", np.where(too_flat, "flat", ""))
    return keep, reason


# ----------------------------------------------------------------------------- pipeline
def preprocess_participant(segments, cfg):
    """Run steps 1–7 on all continuous segments of one participant.

    `segments`: list of eegconf.io.Segment (same participant). `cfg`: configs/preprocessing.yaml.
    Returns (epochs, info):
      epochs – float32 array (n_kept, 16, 800) in microvolts, in recording order;
      info   – dict with epoch_idx (position of each kept epoch in the participant's time
               order, 0-based), segment_idx, counts before/after rejection and the rejection
               reasons, for the QC report (EXP-003).
    """
    f, rj = cfg["filter"], cfg["artefact_rejection"]
    kept, epoch_idx, seg_idx, reasons = [], [], [], []
    n_before = 0
    for s in segments:
        x, names = pick_channels(s.data, s.ch_names, cfg["channels"])
        x = bandpass(x, s.sfreq, f["l_freq"], f["h_freq"], f.get("order", 4))
        x = rereference(x)
        x = resample(x, s.sfreq, cfg["resample_hz"])
        ep = epoch(x, cfg["resample_hz"], cfg["epoch"]["length_s"])
        keep, reason = reject(ep, rj["peak_to_peak_uv"], rj["flat_uv"])
        for k in range(len(ep)):
            if keep[k]:
                kept.append(ep[k].astype(np.float32))
                epoch_idx.append(n_before + k)
                seg_idx.append(s.segment)
            else:
                reasons.append(reason[k])
        n_before += len(ep)
    epochs = np.stack(kept) if kept else np.empty((0, len(cfg["channels"]), int(cfg["resample_hz"] * cfg["epoch"]["length_s"])), np.float32)
    info = {
        "n_segments": len(segments),
        "epochs_before": n_before,
        "epochs_after": len(kept),
        "rejected_ptp_max": int(sum(r == "ptp_max" for r in reasons)),
        "rejected_flat": int(sum(r == "flat" for r in reasons)),
        "epoch_idx": np.array(epoch_idx, int),
        "segment_idx": np.array(seg_idx, int),
        "ch_names": names if segments else list(cfg["channels"]),
    }
    return epochs, info
