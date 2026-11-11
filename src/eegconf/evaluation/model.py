"""AD-vs-HC classifier with representation selection nested inside the training data (D-024, T6.1).

The participant representation has several free choices (LaBraM block 1–12, token patch-mean or
CLS, participant pooling mean or median) plus the regularisation strength C. Choosing them on the
test participants would leak, so `select_and_fit` chooses them by an *inner* cross-validation on
the training participants only, then refits the chosen configuration on all training participants
and predicts the test participants once.

Every model is the same simple pipeline (D-006):
    median imputation (only matters for NaN classical features)
    → per-feature standardisation (removes LaBraM's constant offset; fitted on training rows)
    → L2 logistic regression with class weights balanced (cohorts are imbalanced, ADFSU 86% AD).

Candidates are passed as an ordered dict {name: X (n_participants, d)}; the order is the
tie-break preference (D-024: later block, mean pooling, smaller C win ties).
"""
from dataclasses import dataclass, field

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from eegconf.control import fit_apply

C_GRID = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0)


def make_clf(C):
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                         LogisticRegression(C=C, class_weight="balanced", max_iter=5000))


@dataclass
class Fit:
    """Result of one outer fold: chosen configuration, its inner-CV AUROC and test probabilities."""
    candidate: str
    C: float
    inner_auc: float
    proba: np.ndarray
    inner_table: list = field(default_factory=list)


def _inner_folds(y, strata, n_splits, seed):
    """Stratified K-fold on training rows (rows are participants, so it is participant-grouped)."""
    k = min(n_splits, np.unique(strata, return_counts=True)[1].min())
    return list(StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(np.zeros(len(y)), strata))


def select_and_fit(candidates, y, train_idx, test_idx, strata=None, c_grid=C_GRID, n_splits=5, seed=0,
                   control=None):
    """Pick the best (candidate, C) by inner-CV AUROC on train_idx, refit on train_idx, predict test_idx.

    `candidates`: ordered dict name -> X (n_participants, d) covering ALL participants; only the rows
    in train_idx are ever used for fitting or selection.
    `strata`: per-participant labels to stratify the inner folds on (default: y; LOCO passes cohort×dx).
    `control`: optional zero-argument factory from eegconf.control.make_control (Phase 8). A fresh
    control is fitted on the inner-training rows of every inner fold (and on all of train_idx for the
    final model), so selection evaluates exactly the pipeline that is applied to the test rows (D-031).
    With control=None the result is identical to the Phase 6 classifier.
    """
    y = np.asarray(y)
    train_idx, test_idx = np.asarray(train_idx), np.asarray(test_idx)
    ytr = y[train_idx]
    st = (np.asarray(strata) if strata is not None else y)[train_idx]
    folds = _inner_folds(ytr, st, n_splits, seed)
    best, table = None, []
    for name, X in candidates.items():
        # out-of-fold probabilities for every C; the control is fitted once per inner fold and reused
        oof = {C: np.empty(len(ytr)) for C in c_grid}
        for itr, iva in folds:
            Xa, Xb = fit_apply(control, X, train_idx[itr], [train_idx[iva]])
            for C in c_grid:
                oof[C][iva] = make_clf(C).fit(Xa, ytr[itr]).predict_proba(Xb)[:, 1]
        for C in c_grid:
            auc = roc_auc_score(ytr, oof[C])
            table.append((name, C, auc))
            # strict '>' keeps the earlier (preferred) candidate / smaller C on ties
            if best is None or auc > best[2] + 1e-12:
                best = (name, C, auc)
    name, C, auc = best
    Xa, Xt = fit_apply(control, candidates[name], train_idx, [test_idx])
    final = make_clf(C).fit(Xa, ytr)
    return Fit(name, C, auc, final.predict_proba(Xt)[:, 1], table)


def fixed_fit(X, y, train_idx, test_idx, C=1.0):
    """No selection: one pipeline fitted on train_idx, probabilities for test_idx (nuisance baselines)."""
    m = make_clf(C).fit(X[train_idx], np.asarray(y)[train_idx])
    return m.predict_proba(X[test_idx])[:, 1]
