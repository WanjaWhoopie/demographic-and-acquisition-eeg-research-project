import numpy as np

from eegconf import overlap

RNG = np.random.default_rng(1)


def rec(name, data):
    return {"recording": name, "ch_names": [f"c{i}" for i in range(len(data))], "data": data}


def test_exact_copy_found_despite_channel_reordering():
    b = [rec("b0", RNG.normal(size=(19, 1024))), rec("b1", RNG.normal(size=(19, 1024)))]
    a = [rec("a0", b[1]["data"][::-1].copy())]  # same channels, reversed order
    assert overlap.exact_matches(a, b) == [(1, 1.0, 0)]


def test_rescaled_copy_found_by_near_match_only():
    b = [rec("b0", RNG.normal(size=(19, 1024)))]
    a = [rec("a0", b[0]["data"] * 0.5)]
    assert overlap.exact_matches(a, b)[0][1] == 0.0
    assert overlap.near_matches(a, b) == [(0, 1.0, 0)]


def test_independent_recordings_do_not_match():
    b = [rec("b0", RNG.normal(size=(19, 1024)))]
    a = [rec("a0", RNG.normal(size=(19, 1024)))]
    assert overlap.near_matches(a, b)[0][1] == 0.0


def test_channel_map_recovers_order():
    b = rec("b", RNG.normal(size=(3, 1024)))
    a = rec("a", b["data"][[2, 0, 1]])
    assert [m[1] for m in overlap.channel_map(a, b)] == ["c2", "c0", "c1"]


def test_copy_inside_longer_recording_found_at_offset():
    b = [rec("b0", RNG.normal(size=(19, 1024)))]
    longer = np.hstack([RNG.normal(size=(19, 300)), b[0]["data"], RNG.normal(size=(19, 200))])
    assert overlap.exact_matches([rec("a0", longer)], b) == [(0, 1.0, 300)]
