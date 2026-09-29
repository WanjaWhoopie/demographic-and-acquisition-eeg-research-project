"""Raw-data audit checks A1-A12 (WORKPLAN Phase 2).

All functions take plain arrays so they can be unit-tested without real recordings.
Amplitudes are in microvolts, `data` is (n_channels, n_samples).
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

# Thresholds (documented in WORKPLAN Phase 2, standard audit checklist).
# Amplitude checks run on a 1-30 Hz band-passed copy: raw recordings carry slow drift
# (e.g. ds004504 is only high-passed at 0.4 Hz online), which inflates raw SD several-fold.
AUDIT_BAND_HZ = (1.0, 30.0)
UNITS_OK_UV = (5.0, 100.0)   # plausible robust per-channel SD of band-passed scalp EEG
FLAT_UV = 0.5                # robust SD below this = flat channel
EXTREME_UV = 150.0           # |band-passed x| above this = extreme sample (same as epoch-rejection threshold)
EXTREME_FRACTION = 0.01      # flag if > 1% of samples in any channel are extreme
CLIP_FRACTION = 1e-3         # > 0.1% of samples sitting exactly at the channel max/min = possible clipping
DUPLICATE_R = 0.9            # correlation of cohort-centred fingerprints above this = possible duplicate


def canonical(name):
    """Normalise a channel label: strip prefixes/suffixes like 'EEG ' and '-REF', case-fold."""
    n = name.strip().upper().replace("EEG ", "").replace("-REF", "").replace("-LE", "")
    return n.replace(" ", "")


def channel_check(ch_names, target):
    have = {canonical(c) for c in ch_names}
    missing = [t for t in target if canonical(t) not in have]
    return {"n_channels": len(ch_names), "ch_names": " ".join(ch_names),
            "missing_target_channels": " ".join(missing), "n_missing_target": len(missing)}


def robust_sd(data):
    """Per-channel SD estimated from the median absolute deviation (insensitive to artefacts)."""
    med = np.median(data, axis=1, keepdims=True)
    return 1.4826 * np.median(np.abs(data - med), axis=1)


def bandpass(data, sfreq, band=AUDIT_BAND_HZ):
    sos = butter(4, band, btype="bandpass", fs=sfreq, output="sos")
    return sosfiltfilt(sos, np.nan_to_num(data), axis=1)


def amplitude_checks(data, sfreq):
    """Raw-signal integrity (NaN, flat, clipping, drift) plus band-passed amplitude (units, extremes)."""
    raw_sd = robust_sd(data)
    at_max = (data == np.nanmax(data, axis=1, keepdims=True)).mean(axis=1)
    at_min = (data == np.nanmin(data, axis=1, keepdims=True)).mean(axis=1)
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
        "n_clipped_channels": int(((at_max > CLIP_FRACTION) | (at_min > CLIP_FRACTION)).sum()),
        "extreme_fraction_max": float((np.abs(bp) > EXTREME_UV).mean(axis=1).max()),
    }


def psd(data, sfreq):
    """Welch PSD per channel: 2-s Hann windows, 50% overlap. Returns freqs, psd (uV^2/Hz)."""
    nper = int(round(2 * sfreq))
    return welch(np.nan_to_num(data), fs=sfreq, window="hann", nperseg=nper, noverlap=nper // 2, axis=1)


def band_power(freqs, p, lo, hi):
    sel = (freqs >= lo) & (freqs < hi)
    return p[:, sel].mean(axis=1)


def spectral_checks(freqs, p, line_freq=50.0):
    """Line-noise peak (dB above neighbouring bins) and high-frequency roll-off (dB, 40-48 Hz vs 20-30 Hz)."""
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
    """Flattened log-power spectrum over fmin-fmax for all channels (duplicate detection, A12)."""
    sel = (freqs >= fmin) & (freqs <= fmax)
    return np.log10(p[:, sel] + 1e-12).ravel()


def near_duplicates(fingerprints, ids, r_thresh=DUPLICATE_R):
    """Pairs of recordings whose fingerprints correlate above r_thresh.

    Every EEG spectrum shares the same 1/f shape, so raw fingerprints all correlate > 0.99.
    Each feature is first standardised across recordings (removing the cohort-average spectrum);
    only what is individual to a recording is then compared.
    """
    X = np.asarray(fingerprints, dtype=float)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
    X = (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, keepdims=True)
    r = X @ X.T / X.shape[1]
    i, j = np.triu_indices(len(ids), k=1)
    hit = r[i, j] > r_thresh
    return [(ids[a], ids[b], float(r[a, b])) for a, b in zip(i[hit], j[hit])]


def flags(row, expected_sfreq, expected_condition=None):
    """List of failed checks for one recording."""
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
