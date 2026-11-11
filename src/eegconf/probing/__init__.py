"""Probes: how much nuisance information can be read out of a representation (WORKPLAN Phase 7, O2).

A probe is a simple model trained to predict a nuisance variable (age, sex, cohort) from the
participant representation Z. Good probe performance means the information is *present* in Z;
whether the AD classifier *uses* it is tested separately by removing it (Phase 8).

The same nested logic as the AD classifier applies (D-024): for every outer training fold, the
LaBraM block/token/pooling and the regularisation strength are chosen by an inner CV on the
training participants only, then refitted and evaluated once on the outer test participants.

Tasks
- 'regression' (age): ridge regression; selection by inner-CV mean absolute error;
  reported as MAE and R² against a "predict the training mean" baseline.
- 'binary'     (sex): class-weighted L2 logistic regression; selection by inner-CV AUROC.
- 'multiclass' (cohort): class-weighted multinomial logistic regression; selection by inner-CV
  balanced accuracy; chance = 1 / number of classes.
- 'mlp'        nonlinear check (EXP-022): one hidden layer of 64 units with early stopping, on a
  fixed representation; used to see whether a nonlinear read-out finds more than a linear one.
"""
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import balanced_accuracy_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

GRIDS = {"regression": (0.1, 1.0, 10.0, 100.0, 1000.0),          # ridge alpha (configs/analysis.yaml)
         "binary": (0.001, 0.01, 0.1, 1.0, 10.0, 100.0),          # logistic C
         "multiclass": (0.001, 0.01, 0.1, 1.0, 10.0, 100.0)}


def make_probe(task, h):
    head = {"regression": lambda: Ridge(alpha=h),
            "binary": lambda: LogisticRegression(C=h, class_weight="balanced", max_iter=5000),
            "multiclass": lambda: LogisticRegression(C=h, class_weight="balanced", max_iter=5000)}[task]()
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), head)


def make_mlp(task, seed=0):
    """One hidden layer of 64 units, early stopping on a 20% inner validation split (T7.4)."""
    if task == "regression":
        head = MLPRegressor(hidden_layer_sizes=(64,), early_stopping=True, max_iter=2000, random_state=seed)
    else:
        head = MLPClassifier(hidden_layer_sizes=(64,), early_stopping=True, max_iter=2000, random_state=seed)
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), head)


def score(task, y, pred):
    """Higher is better for every task (MAE is negated)."""
    if task == "regression":
        return -mean_absolute_error(y, pred)
    if task == "binary":
        return roc_auc_score(y, pred)
    return balanced_accuracy_score(y, pred)


def predict(task, m, X):
    if task == "binary":
        return m.predict_proba(X)[:, 1]
    return m.predict(X)


def _inner(task, y, strata, n_splits, seed):
    if task == "regression" and strata is None:
        return list(KFold(n_splits=n_splits, shuffle=True, random_state=seed).split(y))
    s = y if strata is None else strata
    k = min(n_splits, np.unique(s, return_counts=True)[1].min())
    return list(StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(np.zeros(len(s)), s))


def select_and_fit(task, candidates, y, train_idx, test_idx, strata=None, n_splits=5, seed=0):
    """Nested selection of (candidate, hyperparameter) on train_idx; returns (name, h, inner score, test predictions)."""
    y = np.asarray(y)
    ytr = y[train_idx]
    st = None if strata is None else np.asarray(strata)[train_idx]
    folds = _inner(task, ytr, st, n_splits, seed)
    best = None
    for name, X in candidates.items():
        Xtr = X[train_idx]
        for h in GRIDS[task]:
            oof = np.empty(len(ytr), dtype=float if task != "multiclass" else ytr.dtype)
            for itr, iva in folds:
                oof[iva] = predict(task, make_probe(task, h).fit(Xtr[itr], ytr[itr]), Xtr[iva])
            s = score(task, ytr, oof)
            if best is None or s > best[2] + 1e-12:
                best = (name, h, s)
    name, h, s = best
    m = make_probe(task, h).fit(candidates[name][train_idx], ytr)
    return name, h, s, predict(task, m, candidates[name][test_idx])
