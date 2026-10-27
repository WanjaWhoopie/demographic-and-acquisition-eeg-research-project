"""Leakage tests (WORKPLAN T0.4.1): no participant may appear in both train and test."""
import numpy as np
import pandas as pd
import pytest

from eegconf.evaluation import splits


def table(n_per_cohort=(20, 12, 8), hc_share=0.4, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for c, n in zip(["ds004504", "ADFSU", "APAVA"], n_per_cohort):
        for i in range(n):
            rows.append({"cohort": c, "participant_id": f"{c}-{i:02d}",
                         "diagnosis": "HC" if rng.random() < hc_share else "AD"})
    return pd.DataFrame(rows)


def test_participant_kfold_is_disjoint_and_covers_everyone():
    t = table()
    seen = []
    for rep, fold, tr, te in splits.participant_kfold(t, n_splits=5, n_repeats=3):
        assert not set(t.participant_id[tr]) & set(t.participant_id[te])
        seen.append(te)
    assert sorted(np.concatenate(seen[:5])) == list(range(len(t)))  # one repeat covers all rows once


def test_participant_kfold_stratifies_diagnosis():
    t = table(n_per_cohort=(60, 0, 0))
    for _, _, tr, te in splits.participant_kfold(t, n_splits=5):
        assert set(t.diagnosis[te]) == {"AD", "HC"}


def test_loco_holds_out_whole_cohort():
    t = table()
    folds = list(splits.leave_one_cohort_out(t))
    assert [c for c, _, _ in folds] == ["ADFSU", "APAVA", "ds004504"]
    for cohort, tr, te in folds:
        assert set(t.cohort[te]) == {cohort}
        assert cohort not in set(t.cohort[tr])
        assert not set(t.participant_id[tr]) & set(t.participant_id[te])


def test_expand_to_epochs_keeps_participants_together():
    t = table()
    epochs_pid = np.repeat(t.participant_id.to_numpy(), 3)  # 3 epochs per participant
    for _, tr, te in splits.leave_one_cohort_out(t):
        etr = splits.expand_to_epochs(t.participant_id[tr], epochs_pid)
        ete = splits.expand_to_epochs(t.participant_id[te], epochs_pid)
        assert not set(epochs_pid[etr]) & set(epochs_pid[ete])
        assert len(etr) + len(ete) == len(epochs_pid)


def test_check_disjoint_raises_on_leak():
    g = np.array(["a", "b", "c"])
    with pytest.raises(ValueError):
        splits.check_disjoint(g, np.array([0, 1]), np.array([1, 2]))
