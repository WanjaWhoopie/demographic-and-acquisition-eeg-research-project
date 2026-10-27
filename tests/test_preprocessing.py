"""Harmonisation tests (WORKPLAN T4.2.3 and friends): every cohort must come out identical in form."""
import numpy as np
import pytest

from eegconf import preprocessing as pp
from eegconf.io import Segment

TARGET = ["Fp1", "Fp2", "F7", "F3", "F4", "F8", "T3", "C3", "C4", "T4", "T5", "P3", "P4", "T6", "O1", "O2"]
RNG = np.random.default_rng(0)


def cfg():
    return {"channels": TARGET, "filter": {"l_freq": 0.5, "h_freq": 30.0, "order": 4}, "resample_hz": 200,
            "epoch": {"length_s": 4.0}, "artefact_rejection": {"peak_to_peak_uv": 150, "flat_uv": 0.5}}


# --- 1. channel selection ---------------------------------------------------------------
def test_pick_channels_same_order_for_every_cohort_naming():
    ds = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2", "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz"]
    apava = ["C3", "C4", "F3", "F4", "F7", "F8", "Fp1", "Fp2", "O1", "O2", "P3", "P4", "T3", "T4", "T5", "T6"]
    modern = ["EEG Fp1-REF", "fp2", "F7", "F3", "F4", "F8", "T7", "C3", "C4", "T8", "P7", "P3", "P4", "P8", "O1", "O2"]
    for names in (ds, apava, modern):
        x = np.arange(len(names))[:, None] * np.ones((1, 10))   # row value = input channel index
        out, got = pp.pick_channels(x, names, TARGET)
        assert got == TARGET and out.shape == (16, 10)
        # each output row must come from the input channel that names the same electrode
        picked = [names[int(r[0])] for r in out]
        norm = lambda n: pp.ALIASES.get(pp.canonical(n), pp.canonical(n))
        assert [norm(n) for n in picked] == [norm(t) for t in TARGET]


def test_pick_channels_raises_when_target_missing():
    with pytest.raises(ValueError):
        pp.pick_channels(np.zeros((3, 5)), ["Fp1", "Fp2", "F7"], TARGET)


# --- 3. filter -------------------------------------------------------------------------
def test_bandpass_removes_drift_and_line_noise_keeps_alpha():
    fs, t = 500.0, np.arange(10 * 500) / 500.0
    x = (50 * np.sin(2 * np.pi * 0.1 * t) + 20 * np.sin(2 * np.pi * 10 * t) + 30 * np.sin(2 * np.pi * 50 * t))[None]
    y = pp.bandpass(x, fs)[0, 1000:-1000]           # ignore edges
    amp = lambda f: 2 * np.abs(np.fft.rfft(y * np.hanning(len(y))))[int(f * len(y) / fs)] / len(y) * 2
    assert amp(10) > 15 and amp(0.1) < 3 and amp(50) < 1


def test_bandpass_works_on_five_second_segment():
    y = pp.bandpass(RNG.normal(size=(16, 1280)), 256.0)
    assert np.isfinite(y).all() and y.shape == (16, 1280)


# --- 4. reference ----------------------------------------------------------------------
def test_common_average_has_zero_channel_mean():
    y = pp.rereference(RNG.normal(size=(16, 100)) + 5)
    assert np.allclose(y.mean(axis=0), 0)


# --- 5. resample -----------------------------------------------------------------------
@pytest.mark.parametrize("fs,n", [(500.0, 5000), (128.0, 1024), (256.0, 1280)])
def test_resample_to_200hz_gives_expected_length(fs, n):
    y = pp.resample(RNG.normal(size=(2, n)), fs)
    assert y.shape[1] == round(n * 200 / fs)


def test_resample_preserves_a_10hz_tone():
    fs, t = 128.0, np.arange(8 * 128) / 128.0
    y = pp.resample(np.sin(2 * np.pi * 10 * t)[None], fs)[0]
    t2 = np.arange(len(y)) / 200.0
    assert np.corrcoef(y[100:-100], np.sin(2 * np.pi * 10 * t2)[100:-100])[0, 1] > 0.99


# --- 6. epochs -------------------------------------------------------------------------
def test_epochs_never_cross_segment_boundary():
    # an 8-s segment gives 2 epochs, a 5-s segment 1 (tail dropped), never a mixed one
    seg8 = np.arange(16 * 1600).reshape(16, 1600).astype(float)
    assert pp.epoch(seg8, 200).shape == (2, 16, 800)
    seg5 = np.arange(16 * 1000).reshape(16, 1000).astype(float)
    e = pp.epoch(seg5, 200)
    assert e.shape == (1, 16, 800) and e[0, 0, -1] == 799


# --- 7. rejection ----------------------------------------------------------------------
def test_reject_flags_large_and_flat_epochs():
    ep = RNG.normal(0, 10, size=(4, 16, 800))
    ep[1, 3] += 400 * np.sin(np.linspace(0, 3, 800))   # one channel with a huge deflection
    ep[2, 5] = 0.0                                      # one flat channel
    keep, reason = pp.reject(ep)
    assert list(keep) == [True, False, False, True]
    assert reason[1] == "ptp_max" and reason[2] == "flat"


# --- pipeline --------------------------------------------------------------------------
def seg(fs, seconds, names, k=0):
    return Segment("X", "p", "AD", "eyes_closed", fs, names, RNG.normal(0, 10, size=(len(names), int(fs * seconds))), segment=k)


def test_pipeline_output_identical_in_form_across_cohorts():
    ds = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2", "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz"]
    apava = ["C3", "C4", "F3", "F4", "F7", "F8", "Fp1", "Fp2", "O1", "O2", "P3", "P4", "T3", "T4", "T5", "T6"]
    e1, i1 = pp.preprocess_participant([seg(500.0, 20, ds)], cfg())
    e2, i2 = pp.preprocess_participant([seg(256.0, 5, apava, k) for k in range(3)], cfg())
    e3, i3 = pp.preprocess_participant([seg(128.0, 8, ds)], cfg())
    assert e1.shape[1:] == e2.shape[1:] == e3.shape[1:] == (16, 800)
    assert (i1["epochs_before"], i2["epochs_before"], i3["epochs_before"]) == (5, 3, 2)
    assert i1["ch_names"] == i2["ch_names"] == i3["ch_names"] == TARGET
    assert list(i2["segment_idx"]) == [0, 1, 2] and list(i2["epoch_idx"]) == [0, 1, 2]
    assert e1.dtype == np.float32
