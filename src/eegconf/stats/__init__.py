"""Participant-level uncertainty (WORKPLAN Phase 10).

- `metrics`: AUROC and PR-AUC (threshold-free, primary) plus balanced accuracy, sensitivity,
  specificity and F1 at probability 0.5 (D-025).
- `bootstrap_auc`: stratified participant bootstrap: AD and HC participants are resampled with
  replacement *separately*, so every replicate keeps the original class counts (AUROC needs both
  classes). 2000 replicates, percentile 95% CI.
- `paired_delta`: the same resampled participants are used for two sets of predictions on the same
  people (e.g. original vs controlled representation), giving a CI for the AUROC difference.
- `mean_over_folds`: for LOCO, every fold is resampled independently in each replicate and the
  per-fold values are averaged (T10.3), giving a CI for the fold-averaged AUROC or ΔAUROC.
- `bootstrap_p`: two-sided p-value for "difference = 0" from the same bootstrap replicates (D-034).
- `holm`: Holm step-down adjustment for the secondary family (D-028, T10.5).
- `delong_ci`: DeLong's analytic AUROC CI, used only to cross-check the bootstrap CIs (T10.4).
"""
import numpy as np
from scipy.stats import norm
from sklearn.metrics import (average_precision_score, balanced_accuracy_score, f1_score,
                             recall_score, roc_auc_score)

N_BOOT = 2000


def metrics(y, p, threshold=0.5):
    y, p = np.asarray(y), np.asarray(p)
    yhat = (p >= threshold).astype(int)
    return {
        "auroc": roc_auc_score(y, p),
        "pr_auc": average_precision_score(y, p),
        "balanced_accuracy": balanced_accuracy_score(y, yhat),
        "sensitivity": recall_score(y, yhat, pos_label=1, zero_division=0),
        "specificity": recall_score(y, yhat, pos_label=0, zero_division=0),
        "f1": f1_score(y, yhat, zero_division=0),
    }


def _strat_indices(y, rng):
    """One stratified bootstrap replicate: resample positives and negatives separately."""
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    return np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])


def bootstrap_auc(y, p, n_boot=N_BOOT, seed=0):
    """(auroc, ci_low, ci_high) with a stratified participant bootstrap."""
    y, p = np.asarray(y), np.asarray(p)
    rng = np.random.default_rng(seed)
    reps = [roc_auc_score(y[i], p[i]) for i in (_strat_indices(y, rng) for _ in range(n_boot))]
    return roc_auc_score(y, p), *np.percentile(reps, [2.5, 97.5])


def paired_delta(y, p_a, p_b, n_boot=N_BOOT, seed=0, return_reps=False):
    """AUROC(a) − AUROC(b) on the same participants, with a paired stratified bootstrap CI.
    With return_reps=True the replicate values are returned as a fourth element (for bootstrap_p)."""
    y, p_a, p_b = map(np.asarray, (y, p_a, p_b))
    rng = np.random.default_rng(seed)
    reps = []
    for _ in range(n_boot):
        i = _strat_indices(y, rng)
        reps.append(roc_auc_score(y[i], p_a[i]) - roc_auc_score(y[i], p_b[i]))
    d = roc_auc_score(y, p_a) - roc_auc_score(y, p_b)
    out = (d, *np.percentile(reps, [2.5, 97.5]))
    return (*out, np.array(reps)) if return_reps else out


def mean_over_folds(folds, n_boot=N_BOOT, seed=0, return_reps=False):
    """Fold-averaged AUROC (one prediction set per fold) or ΔAUROC (two) with a bootstrap CI.

    `folds`: list of (y, p) or (y, p_a, p_b) tuples, one per held-out cohort.
    Returns (estimate, ci_low, ci_high)."""
    rng = np.random.default_rng(seed)

    def value(y, *ps, idx=None):
        if idx is not None:
            y, ps = y[idx], [p[idx] for p in ps]
        a = roc_auc_score(y, ps[0])
        return a - roc_auc_score(y, ps[1]) if len(ps) == 2 else a

    folds = [tuple(np.asarray(v) for v in f) for f in folds]
    est = np.mean([value(*f) for f in folds])
    reps = [np.mean([value(*f, idx=_strat_indices(f[0], rng)) for f in folds]) for _ in range(n_boot)]
    out = (est, *np.percentile(reps, [2.5, 97.5]))
    return (*out, np.array(reps)) if return_reps else out


def bootstrap_p(reps):
    """Two-sided bootstrap p-value for a difference of 0 (D-034):
    p = min(1, 2 * min(1 + #(reps <= 0), 1 + #(reps >= 0)) / (1 + B)).
    Consistent with the percentile CI: p < 0.05 exactly when 0 lies outside the 95% interval
    (up to the +1 correction, which keeps p above 0)."""
    reps = np.asarray(reps)
    b = len(reps)
    return min(1.0, 2 * min(1 + np.sum(reps <= 0), 1 + np.sum(reps >= 0)) / (1 + b))


def holm(pvals):
    """Holm step-down adjusted p-values (same order as the input); NaN entries are skipped."""
    p = np.asarray(pvals, dtype=float)
    ok = np.flatnonzero(~np.isnan(p))
    order = ok[np.argsort(p[ok])]
    m = len(order)
    adj = np.full(len(p), np.nan)
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * p[i]))
        adj[i] = running
    return adj


def delong_ci(y, p, alpha=0.05):
    """AUROC with DeLong's variance (DeLong et al., 1988) and a normal-approximation CI."""
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    pos, neg = p[y == 1], p[y == 0]
    # psi(x, y) = 1 if x > y, 0.5 if equal, 0 otherwise
    psi = (pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])
    auc = psi.mean()
    v10, v01 = psi.mean(1), psi.mean(0)                  # structural components per positive / negative
    var = v10.var(ddof=1) / len(pos) + v01.var(ddof=1) / len(neg)
    z = norm.ppf(1 - alpha / 2)
    se = np.sqrt(var)
    return auc, max(0.0, auc - z * se), min(1.0, auc + z * se)
