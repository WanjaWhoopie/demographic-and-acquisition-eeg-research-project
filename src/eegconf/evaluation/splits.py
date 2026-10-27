"""Split generators that keep every participant on one side of the train/test line.

Why this module exists
----------------------
Each participant contributes many epochs. If epochs from one person land in both the training
and the test set, a classifier can recognise the person instead of the disease and report
inflated performance (Brookshire et al., 2024; Miltiadous et al., 2026). Every split in this
project therefore operates on *participants*, and tests/test_splits.py asserts that no
participant ID ever appears on both sides.

Two kinds of split are used:

- within-cohort: stratified, participant-grouped K-fold (repeated with different seeds);
- cross-cohort: leave-one-cohort-out (LOCO), where whole cohorts are held out.

All functions yield (train_idx, test_idx) index arrays over the rows of a *participant table*
(one row per participant), never over epochs. Epoch-level arrays are expanded from these
indices by the caller, so the participant rule holds automatically.
"""
import numpy as np
from sklearn.model_selection import StratifiedKFold


def check_disjoint(groups, train_idx, test_idx):
    """Raise if any participant ID is in both train and test. Called by every generator."""
    shared = set(np.asarray(groups)[train_idx]) & set(np.asarray(groups)[test_idx])
    if shared:
        raise ValueError(f"participants in both train and test: {sorted(shared)[:5]}")


def participant_kfold(participants, n_splits=5, n_repeats=1, seed=0, stratify_on="diagnosis"):
    """Stratified K-fold over participants, repeated `n_repeats` times with different shuffles.

    `participants` is a DataFrame with one row per participant and a `stratify_on` column.
    Stratifying on diagnosis keeps the AD/HC ratio similar in every fold, which matters for
    small cohorts (APAVA has 11 HC). Yields (repeat, fold, train_idx, test_idx).
    """
    y = participants[stratify_on].to_numpy()
    groups = participants["participant_id"].to_numpy()
    # Smallest class must have at least n_splits members or stratification is impossible.
    n_min = np.unique(y, return_counts=True)[1].min()
    k = min(n_splits, n_min)
    for rep in range(n_repeats):
        skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed + rep)
        for fold, (tr, te) in enumerate(skf.split(np.zeros(len(y)), y)):
            check_disjoint(groups, tr, te)
            yield rep, fold, tr, te


def leave_one_cohort_out(participants, cohorts=None):
    """Hold out each cohort in turn. Yields (held_out_cohort, train_idx, test_idx)."""
    c = participants["cohort"].to_numpy()
    groups = participants["participant_id"].to_numpy()
    for cohort in (cohorts or sorted(set(c))):
        te = np.flatnonzero(c == cohort)
        tr = np.flatnonzero(c != cohort)
        check_disjoint(groups, tr, te)
        yield cohort, tr, te


def expand_to_epochs(participant_ids_of_rows, epoch_participant_ids):
    """Map a participant-level index selection to epoch-level row indices.

    `participant_ids_of_rows`: the participant IDs selected (e.g. groups[train_idx]).
    `epoch_participant_ids`: participant ID of every epoch row.
    Returns the epoch rows belonging to the selected participants, in their original order.
    """
    wanted = set(participant_ids_of_rows)
    return np.flatnonzero([p in wanted for p in epoch_participant_ids])
