"""Prevalence-balanced cohort centring does exactly what D-026 / T8.2 specify (WORKPLAN T0.4.3)."""
import numpy as np

from eegconf import control


def setup():
    # cohort A: 3 AD at +4, 1 HC at 0   -> plain mean 3, balanced mean 2
    # cohort B: 1 AD at 10, 1 HC at 6   -> balanced mean 8
    # cohort C (held out): values 20, 22
    X = np.array([[4.], [4.], [4.], [0.], [10.], [6.], [20.], [22.]])
    y = np.array([1, 1, 1, 0, 1, 0, 1, 0])
    cohort = np.array(list("AAAABBCC"))
    return X, y, cohort, np.arange(6), np.array([6, 7])


def test_training_cohorts_use_prevalence_balanced_means():
    X, y, cohort, tr, te = setup()
    c = control.make_control("centring_i", cohort, y)().fit(X[tr], tr)
    assert c.mu["A"][0] == 2.0 and c.mu["B"][0] == 8.0                         # ½(mean AD + mean HC), not the plain mean
    np.testing.assert_allclose(c.transform(X[tr], tr).ravel(), [2, 2, 2, -2, 2, -2])


def test_variant_i_uses_pooled_training_mean_for_unseen_cohort():
    X, y, cohort, tr, te = setup()
    _, Xte = control.fit_apply(control.make_control("centring_i", cohort, y), X, tr, [te])
    np.testing.assert_allclose(Xte.ravel(), [20 - 5, 22 - 5])                   # pooled = mean(2, 8) = 5


def test_variant_ii_uses_unseen_cohorts_own_unweighted_mean():
    X, y, cohort, tr, te = setup()
    _, Xte = control.fit_apply(control.make_control("centring_ii", cohort, y), X, tr, [te])
    np.testing.assert_allclose(Xte.ravel(), [-1, 1])                            # own mean 21, labels unused


def test_seen_cohort_in_test_rows_uses_its_training_mean():
    # inner CV: validation rows come from cohorts seen in training and get that cohort's mu_c
    X, y, cohort, tr, te = setup()
    c = control.make_control("centring_ii", cohort, y)().fit(X[[0, 1, 3, 4, 5]], np.array([0, 1, 3, 4, 5]))
    np.testing.assert_allclose(c.transform(X[[2]], np.array([2])).ravel(), [4 - 2])
