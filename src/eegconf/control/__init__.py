"""Nuisance control (WORKPLAN Phase 8, O3): remove age/sex or cohort information from Z.

Every method follows the same contract so that it can sit inside cross-validation:

    c = SomeControl(<side information for ALL participants>, ...)
    c.fit(X_train, train_idx)          # learns ONLY from the training rows (and their labels)
    Z_star = c.transform(X, idx)       # applies the learned transform to any rows

`idx` are participant indices into the side-information arrays (cohort, diagnosis, covariates),
so a control knows which cohort / age / sex each row belongs to. `transform` never reads the
diagnosis labels of the rows it transforms (tested in tests/test_fit_on_train.py); only `fit` may
use labels, and only of the training rows.

Methods
- Residualiser        age/sex: OLS per embedding dimension, Z_d ~ age + sex, fitted on training
                      participants (all, or HC only for the normative sensitivity run, T8.1.4);
                      the covariate-explained part is subtracted using each row's own age/sex.
- CohortCentring      prevalence-balanced centring (T8.2): for each training cohort c,
                      mu_c = 1/2 (mean of AD + mean of HC) from training labels; rows of a training
                      cohort have mu_c subtracted. A cohort not seen in training (the held-out LOCO
                      cohort) is centred with
                        variant 'i'  the pooled training mean (mean of the mu_c), uses no test data;
                        variant 'ii' the unweighted mean of its own rows (no labels; transductive).
- Leace               LEACE (Belrose et al., 2023; package concept-erasure) with the training
                      cohort as a one-hot concept: afterwards no linear classifier can separate the
                      training cohorts better than a constant (on the training data).
- Inlp                INLP (Ravfogel et al., 2020): repeatedly fit a linear cohort classifier and
                      project its direction out; fixed 20 iterations (configs/analysis.yaml).

`make_control(name, ...)` returns a zero-argument factory so that a fresh, unfitted control can be
built inside every inner and outer fold (evaluation.model.select_and_fit(control=...)).
"""
from functools import partial

import numpy as np
from sklearn.linear_model import LogisticRegression

CONTROLS = ("centring_i", "centring_ii", "leace", "inlp", "resid_all", "resid_hc")


class Residualiser:
    """Remove the part of each embedding dimension that is linear in the covariates (age, sex)."""

    def __init__(self, covariates, y=None, fit_on="all"):
        self.cov = np.asarray(covariates, dtype=float)          # (n_participants, k), e.g. [age, sex]
        self.y = None if y is None else np.asarray(y)
        self.fit_on = fit_on                                     # 'all' or 'hc' (normative, T8.1.4)

    def fit(self, X, idx):
        idx = np.asarray(idx)
        keep = np.ones(len(idx), bool) if self.fit_on == "all" else (self.y[idx] == 0)
        C = self.cov[idx][keep]
        self.c_mean = C.mean(0)
        D = np.c_[np.ones(len(C)), C - self.c_mean]              # intercept + centred covariates
        B, *_ = np.linalg.lstsq(D, X[keep], rcond=None)
        self.B = B[1:]                                           # (k, d) covariate slopes
        return self

    def transform(self, X, idx):
        return X - (self.cov[np.asarray(idx)] - self.c_mean) @ self.B


class CohortCentring:
    """Prevalence-balanced cohort centring; see module docstring for variants 'i' and 'ii'."""

    def __init__(self, cohort, y, variant="i"):
        self.cohort = np.asarray(cohort)
        self.y = np.asarray(y)
        self.variant = variant

    def fit(self, X, idx):
        idx = np.asarray(idx)
        g, yy = self.cohort[idx], self.y[idx]
        self.mu = {}
        for c in np.unique(g):
            rows = g == c
            if len(np.unique(yy[rows])) == 2:
                self.mu[c] = 0.5 * (X[rows & (yy == 1)].mean(0) + X[rows & (yy == 0)].mean(0))
            else:                                                # one class only: plain mean (not expected here)
                self.mu[c] = X[rows].mean(0)
        self.pooled = np.mean(list(self.mu.values()), axis=0)
        return self

    def transform(self, X, idx):
        g = self.cohort[np.asarray(idx)]
        out = np.array(X, dtype=float, copy=True)
        for c in np.unique(g):
            rows = g == c
            if c in self.mu:
                out[rows] -= self.mu[c]
            elif self.variant == "i":
                out[rows] -= self.pooled
            else:                                                # 'ii': unseen cohort's own mean, no labels
                out[rows] -= X[rows].mean(0)
        return out


class Leace:
    """LEACE eraser with the training cohorts as a one-hot concept (fitted in float64)."""

    def __init__(self, cohort):
        self.cohort = np.asarray(cohort)

    def fit(self, X, idx):
        import torch
        from concept_erasure import LeaceFitter
        torch.set_num_threads(1)
        g = self.cohort[np.asarray(idx)]
        levels = np.unique(g)
        Z = (g[:, None] == levels[None, :]).astype(np.float64)    # one-hot cohort
        fitter = LeaceFitter(X.shape[1], len(levels), dtype=torch.float64)
        fitter.update(torch.from_numpy(np.asarray(X, dtype=np.float64)), torch.from_numpy(Z))
        self.eraser = fitter.eraser
        return self

    def transform(self, X, idx):
        import torch
        with torch.no_grad():
            return self.eraser(torch.from_numpy(np.asarray(X, dtype=np.float64))).numpy()


class Inlp:
    """Iterative nullspace projection against cohort, in standardised coordinates.

    Each iteration fits a class-weighted L2 logistic regression (C = 1) predicting the training
    cohort from the currently projected data; its weight direction(s), expressed in the original
    standardised space, are added to a removed subspace Q and the projection P = I - Q Q^T is
    recomputed. The final P is applied to new rows after standardising with the training mean/SD.
    """

    def __init__(self, cohort, n_iter=20, C=1.0):
        self.cohort = np.asarray(cohort)
        self.n_iter, self.C = n_iter, C

    def fit(self, X, idx):
        g = self.cohort[np.asarray(idx)]
        self.m, self.s = X.mean(0), X.std(0) + 1e-12
        Xs = (X - self.m) / self.s
        d = X.shape[1]
        Q = np.zeros((d, 0))
        P = np.eye(d)
        for _ in range(self.n_iter):
            clf = LogisticRegression(C=self.C, class_weight="balanced", max_iter=5000).fit(Xs @ P, g)
            U = P @ clf.coef_.T                                  # directions in the standardised space
            U = U[:, np.linalg.norm(U, axis=0) > 1e-10]
            if U.shape[1] == 0:
                break
            Q, _ = np.linalg.qr(np.c_[Q, U])                     # orthonormal basis of all removed directions
            P = np.eye(d) - Q @ Q.T
        self.P, self.n_removed = P, Q.shape[1]
        return self

    def transform(self, X, idx):
        return ((X - self.m) / self.s) @ self.P


def make_control(name, cohort=None, y=None, covariates=None, inlp_iterations=20):
    """Zero-argument factory for control `name` (None or 'none' → no control)."""
    if name in (None, "none"):
        return None
    return {"centring_i": partial(CohortCentring, cohort, y, "i"),
            "centring_ii": partial(CohortCentring, cohort, y, "ii"),
            "leace": partial(Leace, cohort),
            "inlp": partial(Inlp, cohort, inlp_iterations),
            "resid_all": partial(Residualiser, covariates, y, "all"),
            "resid_hc": partial(Residualiser, covariates, y, "hc")}[name]


def fit_apply(factory, X, fit_idx, apply_sets):
    """Fit a fresh control on rows fit_idx of X and transform fit_idx and each index set in apply_sets.
    With factory None, returns the untransformed rows (the original representation)."""
    sets = [np.asarray(fit_idx)] + [np.asarray(s) for s in apply_sets]
    if factory is None:
        return [X[s] for s in sets]
    c = factory().fit(X[sets[0]], sets[0])
    return [c.transform(X[s], s) for s in sets]
