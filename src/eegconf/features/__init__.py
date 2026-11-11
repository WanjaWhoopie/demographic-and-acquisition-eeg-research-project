"""Classical EEG features (WORKPLAN T6.4 comparator, T11.1 interpretation).

Per participant, from their preprocessed 4-s epochs (n_epochs, 16, 800) at 200 Hz:

- `participant_psd`: Welch PSD averaged over epochs (2-s Hann windows, 50% overlap, 0.5-Hz bins);
- `relative_band_power`: per channel, power in delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz
  divided by 1–30 Hz power (64 features). Relative power removes overall amplitude, so these
  features describe spectral *shape*;
- `aperiodic_exponents`: per channel, the 1/f exponent from specparam in 'fixed' mode fitted over
  2–30 Hz (starting at 2 Hz keeps clear of the 0.5-Hz high-pass edge). Fits with R² < 0.9 are
  returned as NaN and counted, so the caller can impute with the training-set median.

The comparator feature vector is the 64 relative powers + 16 exponents = 80 features.
"""
import warnings

import numpy as np
from scipy.signal import welch

SFREQ = 200.0
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
APERIODIC_RANGE = (2.0, 30.0)
MIN_R2 = 0.9


def participant_psd(X, sfreq=SFREQ):
    """Mean Welch PSD over a participant's epochs. Returns (freqs, psd (n_channels, n_freqs))."""
    f, p = welch(X, fs=sfreq, window="hann", nperseg=int(2 * sfreq), noverlap=int(sfreq), axis=2)
    return f, p.mean(axis=0)


def relative_band_power(f, p):
    """(n_channels * 4,) band powers relative to 1–30 Hz, ordered band-major (delta ch1..16, theta ...)."""
    tot = p[:, (f >= 1) & (f < 30)].sum(axis=1)
    return np.concatenate([p[:, (f >= lo) & (f < hi)].sum(axis=1) / tot for lo, hi in BANDS.values()])


def aperiodic_exponents(f, p, freq_range=APERIODIC_RANGE):
    """(n_channels,) aperiodic exponents; NaN where the fit's R² < MIN_R2. Also returns the count of
    rejected fits."""
    from specparam import SpectralModel

    out = np.full(p.shape[0], np.nan)
    for ch in range(p.shape[0]):
        fm = SpectralModel(peak_width_limits=[1, 8], max_n_peaks=6, aperiodic_mode="fixed", verbose=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                fm.fit(f, p[ch], list(freq_range))
                if fm.get_metrics("gof_rsquared") >= MIN_R2:
                    out[ch] = fm.get_params("aperiodic", "exponent")
            except Exception:  # a failed fit is treated like a poor one
                pass
    return out, int(np.isnan(out).sum())


def classical_vector(X, sfreq=SFREQ):
    """80-feature comparator vector for one participant + number of rejected aperiodic fits."""
    f, p = participant_psd(X, sfreq)
    exps, n_bad = aperiodic_exponents(f, p)
    return np.concatenate([relative_band_power(f, p), exps]), n_bad
