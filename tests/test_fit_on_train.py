"""Every nuisance control learns only from training rows (WORKPLAN T0.4.2, T8.5).

Two leakage checks per control:
1. Poisoning the *test* rows' labels (diagnosis) and covariates' effect on fitting must not change
   anything: the fitted transform is the same, and test rows are transformed without their labels.
2. Poisoning the *test* rows' features must not change how the *training* rows are transformed
   (the fit never looks at test rows). Centring variant (ii) is the documented exception for the
   held-out cohort itself: it uses the unlabelled test rows' own mean, never their labels.
"""
import numpy as np
import pytest

from eegconf import control
from eegconf.evaluation import model

RNG = np.random.default_rng(1)


def toy(n_per=30, d=12):
    """Three cohorts with different offsets, mixed diagnosis, ages and sexes."""
    cohort = np.repeat(np.array(["A", "B", "C"]), n_per)
    y = np.tile(np.r_[np.ones(n_per // 2), np.zeros(n_per - n_per // 2)], 3).astype(int)
    X = RNG.normal(size=(3 * n_per, d))
    for c, off in zip("ABC", (0.0, 2.0, -1.5)):
        X[cohort == c] += off
    X[:, 0] += 1.0 * y
    cov = np.c_[RNG.normal(70, 7, 3 * n_per), RNG.integers(0, 2, 3 * n_per)]
    return X, y, cohort, cov


def _needs_leace(name):
    if name == "leace":
        pytest.importorskip("concept_erasure")


@pytest.mark.parametrize("name", control.CONTROLS)
def test_test_labels_never_used(name):
    _needs_leace(name)
    X, y, cohort, cov = toy()
    tr, te = np.flatnonzero(cohort != "C"), np.flatnonzero(cohort == "C")       # LOCO-style split
    y2 = y.copy(); y2[te] = 1 - y2[te]                                          # flip test labels
    a = control.fit_apply(control.make_control(name, cohort, y, cov), X, tr, [te])
    b = control.fit_apply(control.make_control(name, cohort, y2, cov), X, tr, [te])
    for u, v in zip(a, b):
        np.testing.assert_allclose(u, v)


@pytest.mark.parametrize("name", control.CONTROLS)
def test_training_transform_ignores_test_features(name):
    _needs_leace(name)
    X, y, cohort, cov = toy()
    tr, te = np.flatnonzero(cohort != "C"), np.flatnonzero(cohort == "C")
    X2 = X.copy(); X2[te] = 1e3                                                 # garbage in test rows
    a_tr, _ = control.fit_apply(control.make_control(name, cohort, y, cov), X, tr, [te])
    b_tr, _ = control.fit_apply(control.make_control(name, cohort, y, cov), X2, tr, [te])
    np.testing.assert_allclose(a_tr, b_tr)


@pytest.mark.parametrize("name", ["centring_i", "leace", "inlp"])
def test_controlled_selection_never_touches_test_rows(name):
    _needs_leace(name)
    # Same poisoning check as for the uncontrolled classifier (test_model_stats), with a control.
    X, y, cohort, cov = toy()
    tr, te = np.flatnonzero(cohort != "C"), np.flatnonzero(cohort == "C")
    strata = np.char.add(cohort, y.astype(str))
    cands = {"x": X}
    a = model.select_and_fit(cands, y, tr, te, strata=strata, control=control.make_control(name, cohort, y, cov))
    X2, y2 = X.copy(), y.copy(); X2[te] = 1e3; y2[te] = 1 - y2[te]
    b = model.select_and_fit({"x": X2}, y2, tr, te, strata=strata, control=control.make_control(name, cohort, y2, cov))
    assert (a.candidate, a.C, a.inner_auc) == (b.candidate, b.C, b.inner_auc)


def test_no_control_matches_plain_classifier():
    X, y, cohort, cov = toy()
    tr, te = np.flatnonzero(cohort != "C"), np.flatnonzero(cohort == "C")
    a = model.select_and_fit({"x": X}, y, tr, te)
    b = model.select_and_fit({"x": X}, y, tr, te, control=control.make_control("none"))
    np.testing.assert_allclose(a.proba, b.proba)


def test_residualiser_removes_linear_covariate_signal_on_training_rows():
    X, y, cohort, cov = toy()
    X[:, 1] += 0.3 * cov[:, 0]                                                  # age-driven dimension
    tr = np.arange(0, 90, 2)
    Xt, = control.fit_apply(control.make_control("resid_all", cohort, y, cov), X, tr, [])
    for k in range(cov.shape[1]):
        r = [np.corrcoef(Xt[:, j], cov[tr, k])[0, 1] for j in range(X.shape[1])]
        assert np.max(np.abs(r)) < 1e-8


def test_residualiser_hc_fit_uses_only_controls():
    X, y, cohort, cov = toy()
    tr = np.arange(90)
    c = control.make_control("resid_hc", cohort, y, cov)().fit(X[tr], tr)
    hc = tr[y[tr] == 0]
    ref = control.make_control("resid_all", cohort, np.zeros_like(y), cov)().fit(X[hc], hc)
    np.testing.assert_allclose(c.B, ref.B)


def test_leace_removes_linear_cohort_information_on_training_rows():
    _needs_leace("leace")
    X, y, cohort, cov = toy()
    tr = np.flatnonzero(cohort != "C")
    Xt, = control.fit_apply(control.make_control("leace", cohort, y, cov), X, tr, [])
    g = cohort[tr]
    # LEACE guarantee: class-conditional means are equal after erasure
    np.testing.assert_allclose(Xt[g == "A"].mean(0), Xt[g == "B"].mean(0), atol=1e-8)


def test_inlp_projection_is_idempotent_and_removes_iterations_directions():
    X, y, cohort, cov = toy()
    tr = np.flatnonzero(cohort != "C")
    c = control.make_control("inlp", cohort, y, cov, inlp_iterations=5)().fit(X[tr], tr)
    np.testing.assert_allclose(c.P @ c.P, c.P, atol=1e-10)
    assert c.n_removed == 5                                                     # binary: one direction per iteration
