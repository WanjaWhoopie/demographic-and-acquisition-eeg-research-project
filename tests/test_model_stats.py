"""Tests for nested selection (no test rows used, WORKPLAN T0.4.2) and the bootstrap statistics."""
from collections import OrderedDict

import numpy as np
import pytest

from eegconf import stats
from eegconf.evaluation import model

RNG = np.random.default_rng(0)


def toy(n=80, d=10, signal=1.5):
    y = np.r_[np.ones(n // 2), np.zeros(n - n // 2)].astype(int)
    X_sig = RNG.normal(size=(n, d)); X_sig[:, 0] += signal * y
    X_noise = RNG.normal(size=(n, d))
    return y, X_sig, X_noise


def test_selection_prefers_informative_candidate():
    y, Xs, Xn = toy()
    tr, te = np.arange(0, 80, 2), np.arange(1, 80, 2)
    fit = model.select_and_fit(OrderedDict(noise=Xn, signal=Xs), y, tr, te)
    assert fit.candidate == "signal" and len(fit.proba) == len(te)


def test_selection_never_touches_test_rows():
    # Poison the test rows with NaN-free garbage that would wreck any fit that used them; the
    # selected candidate and inner AUROC must be identical to a run where test rows are clean.
    y, Xs, Xn = toy()
    tr, te = np.arange(0, 80, 2), np.arange(1, 80, 2)
    a = model.select_and_fit(OrderedDict(noise=Xn, signal=Xs), y, tr, te)
    Xs2, Xn2, y2 = Xs.copy(), Xn.copy(), y.copy()
    Xs2[te] = 1e6; Xn2[te] = -1e6; y2[te] = 1 - y2[te]
    b = model.select_and_fit(OrderedDict(noise=Xn2, signal=Xs2), y2, tr, te)
    assert (a.candidate, a.C, a.inner_auc) == (b.candidate, b.C, b.inner_auc)


def test_imputation_handles_missing_features():
    y, Xs, _ = toy()
    Xs[::7, 3] = np.nan
    p = model.fixed_fit(Xs, y, np.arange(60), np.arange(60, 80))
    assert np.isfinite(p).all()


def test_bootstrap_ci_contains_estimate_and_is_reasonable():
    y = np.r_[np.ones(40), np.zeros(40)].astype(int)
    p = y * 0.6 + RNG.uniform(0, 0.6, 80)
    auc, lo, hi = stats.bootstrap_auc(y, p, n_boot=500)
    assert lo <= auc <= hi and 0 < hi - lo < 0.3


def test_paired_delta_zero_for_identical_predictions():
    y = np.r_[np.ones(30), np.zeros(30)].astype(int)
    p = RNG.uniform(size=60)
    d, lo, hi = stats.paired_delta(y, p, p, n_boot=200)
    assert d == 0 and lo == 0 and hi == 0


def test_mean_over_folds_averages_fold_aurocs():
    y1 = np.r_[np.ones(10), np.zeros(10)].astype(int); p1 = y1.astype(float)          # AUROC 1.0
    y2 = np.r_[np.ones(10), np.zeros(10)].astype(int); p2 = 1 - y2.astype(float)      # AUROC 0.0
    est, lo, hi = stats.mean_over_folds([(y1, p1), (y2, p2)], n_boot=100)
    assert est == pytest.approx(0.5)


def test_metrics_threshold_metrics():
    m = stats.metrics([1, 1, 0, 0], [0.9, 0.4, 0.6, 0.1])
    assert m["sensitivity"] == 0.5 and m["specificity"] == 0.5 and m["auroc"] == 0.75


def test_mlp_age_probe_predicts_on_the_target_scale():
    # Regression check for D-030: with an unscaled age target the MLP probe returned predictions
    # far outside the age range. With target standardisation, pure-noise features should give
    # predictions near the training mean, i.e. an error close to "guess the mean".
    from eegconf import probing
    X = RNG.normal(size=(80, 20))
    age = RNG.normal(70, 8, size=80)
    m = probing.make_mlp("regression", seed=0).fit(X[:60], age[:60])
    pred = m.predict(X[60:])
    baseline = np.abs(age[60:] - age[:60].mean()).mean()
    assert np.abs(pred - age[60:]).mean() < 2 * baseline
    assert 40 < pred.mean() < 100
