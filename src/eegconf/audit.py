"""Raw-data audit checks A1-A12 (WORKPLAN Phase 2).

Every function here takes plain NumPy arrays, so each check can be unit-tested with synthetic
signals (tests/test_audit.py) without touching real recordings. The script
scripts/01_audit.py wires these checks to the cohort loaders in eegconf.io.

Conventions
- `data` is (n_channels, n_samples) in microvolts.
- Checks return flat dicts so the script can write one CSV row per participant.
- Nothing here modifies the data; the audit only describes it.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

# ----------------------------------------------------------------------------- thresholds
# All thresholds are heuristics chosen before looking at results; change them only with a note
# in docs/decision_log.md. They are deliberately lenient: the audit should surface problems
# for a human to look at, not silently exclude data (exclusion happens in preprocessing).

# Amplitude checks run on a 1-30 Hz band-passed copy of the signal. Raw recordings carry slow
# drift (ds004504 is only high-passed at 0.4 Hz online), which inflates the raw SD several-fold
# and would make a perfectly good recording look like it has the wrong units.
AUDIT_BAND_HZ = (1.0, 30.0)

# Plausible robust per-channel SD of band-passed resting scalp EEG in an elderly population.
# Typical values are 5-30 uV; the floor is set at 3 uV because common-average-referenced data
# (APAVA) sit lower than ear-referenced data, and the ceiling at 100 uV catches data stored
# in nanovolts or otherwise mis-scaled. Data stored in volts (SD ~ 1e-5) fail the floor.
UNITS_OK_UV = (3.0, 100.0)

FLAT_UV = 0.5                # raw robust SD below this = flat (disconnected or zeroed) channel
EXTREME_UV = 150.0           # |band-passed x| above this = extreme sample; same value as the
                             # epoch-rejection threshold in configs/preprocessing.yaml
EXTREME_FRACTION = 0.01      # flag a participant if > 1% of samples in any channel are extreme

# Clipping (amplifier/ADC saturation) shows as the signal sitting flat at its extreme for several
# consecutive samples. A single sample at the maximum is normal; repeated identical maxima can also
# come from coarse amplitude quantisation (ADFSU has ~600 distinct values per recording), so we
# require a *run* of at least CLIP_RUN consecutive samples at the extreme AND at least
# CLIP_FRACTION of all samples at that extreme before calling a channel clipped.
CLIP_RUN = 4                 # consecutive samples (>= 30 ms at 128 Hz, 8 ms at 500 Hz)
CLIP_FRACTION = 1e-3

# Near-duplicate recordings: correlation between cohort-centred log-PSD fingerprints above this.
# Fingerprints are centred across the cohort first because every EEG spectrum shares the same
# 1/f shape and raw fingerprints all correlate > 0.99.
DUPLICATE_R = 0.9


def canonical(name):
    """Normalise a channel label so that 'EEG Fp1-REF', 'fp1' and 'Fp1' compare equal (A3)."""
    n = name.strip().upper().replace("EEG ", "").replace("-REF", "").replace("-LE", "")
    return n.replace(" ", "")


def channel_check(ch_names, target):
    """A3: which of the 16 target channels (configs/preprocessing.yaml) are missing."""
    have = {canonical(c) for c in ch_names}
    missing = [t for t in target if canonical(t) not in have]
    return {"n_channels": len(ch_names), "ch_names": " ".join(ch_names),
            "missing_target_channels": " ".join(missing), "n_missing_target": len(missing)}


def robust_sd(data):
    """Per-channel SD estimated from the median absolute deviation.

    1.4826 * MAD equals the SD for Gaussian data but is barely affected by a few huge
    artefacts, which an ordinary SD would be dominated by."""
    med = np.median(data, axis=1, keepdims=True)
    return 1.4826 * np.median(np.abs(data - med), axis=1)


def bandpass(data, sfreq, band=AUDIT_BAND_HZ):
    """Zero-phase 4th-order Butterworth band-pass (second-order sections for numerical stability)."""
    sos = butter(4, band, btype="bandpass", fs=sfreq, output="sos")
    return sosfiltfilt(sos, np.nan_to_num(data), axis=1)


def longest_run(mask):
    """Length of the longest run of consecutive True values along the last axis, per row."""
    # Pad with False on both sides so every run has a clear start and end, then diff.
    padded = np.concatenate([np.zeros((mask.shape[0], 1), bool), mask, np.zeros((mask.shape[0], 1), bool)], axis=1)
    d = np.diff(padded.astype(np.int8), axis=1)
    out = np.zeros(mask.shape[0], int)
    for i in range(mask.shape[0]):
        starts, ends = np.flatnonzero(d[i] == 1), np.flatnonzero(d[i] == -1)
        if len(starts):
            out[i] = (ends - starts).max()
    return out


def clipped_channels(data):
    """A10: channels whose signal sits at its own maximum or minimum for CLIP_RUN+ consecutive
    samples and for at least CLIP_FRACTION of all samples. See the threshold notes above."""
    n = 0
    for extreme in (np.nanmax(data, axis=1, keepdims=True), np.nanmin(data, axis=1, keepdims=True)):
        at = data == extreme
        n += int(((at.mean(axis=1) >= CLIP_FRACTION) & (longest_run(at) >= CLIP_RUN)).sum())
    return n


def amplitude_checks(data, sfreq):
    """A5 + A10 for one continuous segment.

    Integrity checks (NaN/Inf, flat channels, clipping) use the raw signal because drift does
    not affect them. Unit and extreme-amplitude checks use the 1-30 Hz band-passed signal so
    that slow drift cannot inflate them."""
    raw_sd = robust_sd(data)
    bp = bandpass(data, sfreq)
    sd = robust_sd(bp)
    return {
        "n_nan": int(np.isnan(data).sum()),
        "n_inf": int(np.isinf(data).sum()),
        "raw_robust_sd_uv_median": float(np.median(raw_sd)),
        "raw_range_uv": float(np.nanmax(data) - np.nanmin(data)),
        "robust_sd_uv_median": float(np.median(sd)),
        "robust_sd_uv_min": float(sd.min()),
        "robust_sd_uv_max": float(sd.max()),
        "units_plausible": bool(UNITS_OK_UV[0] <= np.median(sd) <= UNITS_OK_UV[1]),
        "n_flat_channels": int((raw_sd < FLAT_UV).sum()),
        "n_clipped_channels": clipped_channels(data),
        # worst channel's share of samples beyond +/-150 uV after band-passing
        "extreme_fraction_max": float((np.abs(bp) > EXTREME_UV).mean(axis=1).max()),
    }


def psd(data, sfreq):
    """A11: Welch power spectral density per channel, 2-s Hann windows with 50% overlap.

    Returns (freqs, psd) with psd in uV^2/Hz and 0.5-Hz resolution. Segments shorter than 2 s
    would give coarser resolution; none of our cohorts has segments under 5 s."""
    nper = int(round(2 * sfreq))
    return welch(np.nan_to_num(data), fs=sfreq, window="hann", nperseg=nper, noverlap=nper // 2, axis=1)


def band_power(freqs, p, lo, hi):
    """Mean PSD per channel over [lo, hi) Hz."""
    sel = (freqs >= lo) & (freqs < hi)
    return p[:, sel].mean(axis=1)


def spectral_checks(freqs, p, line_freq=50.0):
    """A9 + A11 summary numbers from a PSD.

    - line_noise_db: power at the mains frequency (+/-0.5 Hz) relative to the flanks 2-5 Hz
      either side, median over channels. > ~10 dB means a visible mains peak. NaN when the
      mains frequency is above the Nyquist limit (e.g. 60 Hz data sampled at 128 Hz).
    - hf_rolloff_db: 40-48 Hz power relative to 20-30 Hz. Strongly negative values mean the
      source applied a low-pass filter (A9: prior processing we cannot undo)."""
    out = {}
    nyq = freqs[-1]
    if line_freq + 5 <= nyq:
        peak = band_power(freqs, p, line_freq - 0.5, line_freq + 0.5)
        flank = (band_power(freqs, p, line_freq - 5, line_freq - 2) + band_power(freqs, p, line_freq + 2, line_freq + 5)) / 2
        out["line_noise_db"] = float(np.median(10 * np.log10(peak / flank)))
    else:
        out["line_noise_db"] = np.nan
    if 48 <= nyq:
        out["hf_rolloff_db"] = float(np.median(10 * np.log10(band_power(freqs, p, 40, 48) / band_power(freqs, p, 20, 30))))
    else:
        out["hf_rolloff_db"] = np.nan
    return out


def fingerprint(freqs, p, fmin=1.0, fmax=30.0):
    """A12: flattened log-power spectrum (all channels, fmin-fmax) used to compare recordings."""
    sel = (freqs >= fmin) & (freqs <= fmax)
    return np.log10(p[:, sel] + 1e-12).ravel()


def near_duplicates(fingerprints, ids, r_thresh=DUPLICATE_R):
    """A12: pairs of recordings whose spectral fingerprints correlate above r_thresh.

    Every EEG spectrum shares the same 1/f shape, so raw fingerprints all correlate > 0.99.
    Each feature is first standardised across recordings (removing the cohort-average
    spectrum); only what is individual to a recording is then compared. A hit is a *candidate*
    duplicate: confirm or reject it with a time-domain comparison (see EXP-001 for an example).
    """
    X = np.asarray(fingerprints, dtype=float)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)      # centre each feature across recordings
    X = (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, keepdims=True)   # z-score each recording
    r = X @ X.T / X.shape[1]                                  # Pearson correlation matrix
    i, j = np.triu_indices(len(ids), k=1)
    hit = r[i, j] > r_thresh
    return [(ids[a], ids[b], float(r[a, b])) for a, b in zip(i[hit], j[hit])]


def flags(row, expected_sfreq, expected_condition=None):
    """Names of the failed checks for one participant, joined with ';' (empty string = all passed)."""
    f = []
    if row.get("n_missing_target", 0):
        f.append("A3_missing_channels")
    if expected_sfreq and row.get("sfreq") != expected_sfreq:
        f.append("A4_sfreq")
    if not row.get("units_plausible", True):
        f.append("A5_units")
    if expected_condition and expected_condition not in str(row.get("condition", "")).lower().replace("_", ""):
        f.append("A7_condition")
    if row.get("n_nan") or row.get("n_inf"):
        f.append("A10_nan_inf")
    if row.get("n_flat_channels"):
        f.append("A10_flat")
    if row.get("n_clipped_channels"):
        f.append("A10_clipping")
    if row.get("extreme_fraction_max", 0) > EXTREME_FRACTION:
        f.append("A10_extreme_amplitude")
    return ";".join(f)
