"""Tests for the LaBraM wrapper that do not need the model weights."""
from pathlib import Path

import numpy as np
import pytest
import yaml

from eegconf import representation as rep

ROOT = Path(__file__).resolve().parents[1]
LABRAM = ROOT / "external" / "LaBraM"


def test_every_configured_channel_has_a_labram_name():
    channels = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))["channels"]
    assert all(c in rep.LABRAM_NAMES for c in channels)


def test_pool_participant_mean_and_median():
    Z = np.array([[1.0, 2.0], [3.0, 4.0], [100.0, 0.0]])
    assert np.allclose(rep.pool_participant(Z, "mean"), [34.666667, 2.0])
    assert np.allclose(rep.pool_participant(Z, "median"), [3.0, 2.0])
    with pytest.raises(ValueError):
        rep.pool_participant(Z, "max")


@pytest.mark.skipif(not (LABRAM / "utils.py").exists(), reason="LaBraM repository not cloned")
def test_input_chans_follow_labram_vocabulary():
    channels = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))["channels"]
    chans = rep.input_chans(channels, LABRAM)
    assert chans[0] == 0 and len(chans) == 17            # CLS slot + 16 channels
    assert len(set(chans)) == 17                          # no two channels share a slot
    assert all(1 <= c <= 128 for c in chans[1:])          # pos_embed has 128 + 1 slots
