import numpy as np

from eegconf import audit

FS = 200.0
RNG = np.random.default_rng(0)


def eeg(n_ch=4, seconds=20, sd_uv=20.0):
    return RNG.normal(0, sd_uv, size=(n_ch, int(FS * seconds)))


def test_units_plausible_for_microvolt_data():
    assert audit.amplitude_checks(eeg(), FS)["units_plausible"]


def test_volts_mistaken_for_microvolts_is_flagged():
    assert not audit.amplitude_checks(eeg() * 1e-6, FS)["units_plausible"]


def test_flat_channel_detected():
    x = eeg()
    x[1] = 0.01
    assert audit.amplitude_checks(x, FS)["n_flat_channels"] == 1


def test_clipping_detected():
    x = eeg()
    x[2] = np.clip(x[2], -15, 15)  # many samples pinned at +/-15 uV
    assert audit.amplitude_checks(x, FS)["n_clipped_channels"] >= 1


def test_line_noise_peak_detected():
    t = np.arange(int(FS * 20)) / FS
    x = eeg() + 50 * np.sin(2 * np.pi * 50 * t)
    f, p = audit.psd(x, FS)
    assert audit.spectral_checks(f, p, line_freq=50)["line_noise_db"] > 10


def test_channel_labels_normalised():
    res = audit.channel_check(["EEG Fp1-REF", "fp2", "T3"], ["Fp1", "Fp2", "T3", "O1"])
    assert res["missing_target_channels"] == "O1"


def test_near_duplicate_recordings_found():
    a, b = eeg(), eeg()
    fps, ids = [], ["a", "a_copy", "b"]
    for x in (a, a * 1.0001, b):
        f, p = audit.psd(x, FS)
        fps.append(audit.fingerprint(f, p))
    pairs = audit.near_duplicates(fps, ids)
    assert [(i, j) for i, j, _ in pairs] == [("a", "a_copy")]


def test_flags_combine_failures():
    row = {"n_missing_target": 1, "sfreq": 128.0, "units_plausible": False, "n_nan": 0, "n_inf": 0,
           "n_flat_channels": 0, "n_clipped_channels": 0, "extreme_fraction_max": 0.0}
    assert audit.flags(row, expected_sfreq=500.0) == "A3_missing_channels;A4_sfreq;A5_units"


def test_slow_drift_does_not_fail_units_or_extreme_checks():
    t = np.arange(int(FS * 20)) / FS
    x = eeg() + 400 * np.sin(2 * np.pi * 0.1 * t)  # large 0.1 Hz drift, typical of raw recordings
    res = audit.amplitude_checks(x, FS)
    assert res["units_plausible"] and res["extreme_fraction_max"] < audit.EXTREME_FRACTION
    assert res["raw_robust_sd_uv_median"] > 100


def test_shared_spectral_shape_is_not_a_duplicate():
    f = np.linspace(1, 30, 59)
    common = -np.log10(f)  # every EEG spectrum shares a 1/f shape
    fps = [np.tile(common, 4) + RNG.normal(0, 0.05, 4 * len(f)) for _ in range(20)]
    assert audit.near_duplicates(fps, [str(i) for i in range(20)]) == []
