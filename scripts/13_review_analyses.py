"""Review-prompted analyses (D-039): EXP-055 fixed-block comparison, EXP-056 pooled positive control.

    python scripts/13_review_analyses.py --part fixed_block   # EXP-055, about 1 h with 20 workers
    python scripts/13_review_analyses.py --part pooled        # EXP-056, about 3 h with 20 workers

Both reuse the EXP-031 pipeline unchanged (scripts/08_control.py: class-weighted logistic regression,
D-024 nested selection, control refitted inside every inner and outer training fold, D-031).

EXP-055 fixed block
  For each LaBraM block b, the candidate set is restricted to that block's four token × pooling
  configurations; C, token and pooling are still chosen by inner CV, so the only difference from
  EXP-031 is that the block cannot switch. LOCO, controls none / centring_i / leace / inlp.
  Per block: per-fold AUROC, mean over folds, and ΔAUROC = AUROC(none) − AUROC(control) with a paired
  bootstrap CI (stats.mean_over_folds). Check: block 1 with no control reproduces EXP-031 in every
  fold (its selection was always a block-1 configuration).
EXP-056 pooled positive control
  All 176 participants, stratified (cohort × diagnosis) participant 5-fold × 10 repeats, the full
  48-candidate selection, same four controls. From repeat-averaged out-of-fold probabilities:
  pooled AUROC, within-cohort AUROC (mean over the three cohorts), shortcut gap = pooled − within,
  and the paired bootstrap CI of each control's change in pooled AUROC and in the gap.

Outputs: results/tables/T13_fixed_block.csv, T13_fixed_block_deltas.csv, T13_pooled_control.csv;
results/figures/EXP-055_fixed_block.png, EXP-056_pooled_control.png.
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import importlib.util
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed
from sklearn.metrics import roc_auc_score

from eegconf import stats
from eegconf.control import make_control
from eegconf.evaluation import model, splits

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
CONTROLS = ("none", "centring_i", "leace", "inlp")
LABEL = {"none": "original", "centring_i": "centring (i)", "leace": "LEACE", "inlp": "INLP"}
COLOUR = {"none": "#8a94a6", "centring_i": "#2a78d6", "leace": "#1baf7a", "inlp": "#eb6834"}

# reuse load() and labram_candidates() from 08_control.py so the candidates are built identically
_spec = importlib.util.spec_from_file_location("control08", ROOT / "scripts/08_control.py")
control08 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(control08)


def classify(cands, y, tr, te, strata, seed, ctrl):
    f = model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed, control=ctrl)
    return f.proba, f.candidate, f.C


# ============================================================================ EXP-055
def fixed_block(z, meta, seed, n_inlp, n_jobs):
    Z = z["Z_labram-base"]
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()
    folds = list(splits.leave_one_cohort_out(meta))
    jobs = [(b, ctrl, held, tr, te) for b in range(12) for ctrl in CONTROLS for held, tr, te in folds]
    res = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(classify)(control08.labram_candidates(Z, [b]), y, tr, te, strata, seed,
                          make_control(ctrl, cohort, y, inlp_iterations=n_inlp))
        for b, ctrl, held, tr, te in jobs)

    pred = {}                                   # (block, control, held) -> (y_test, proba)
    rows = []
    for (b, ctrl, held, tr, te), (p, cand, C) in zip(jobs, res):
        pred[(b + 1, ctrl, held)] = (y[te], p)
        auc, lo, hi = stats.bootstrap_auc(y[te], p, seed=seed)
        rows.append({"block": b + 1, "control": ctrl, "held_out": held, "auroc": auc, "ci_low": lo, "ci_high": hi,
                     "selected": cand, "C": C})
    for b in range(1, 13):
        for ctrl in CONTROLS:
            est, lo, hi = stats.mean_over_folds([pred[(b, ctrl, h)] for h, _, _ in folds], seed=seed)
            rows.append({"block": b, "control": ctrl, "held_out": "MEAN over folds", "auroc": est, "ci_low": lo, "ci_high": hi})
    out = pd.DataFrame(rows)

    # Check: block 1 without control is the EXP-031 "none" classifier (always a block-1 configuration)
    t08 = pd.read_csv(ROOT / "results/tables/T08_loco.csv")
    for held, _, _ in folds:
        ref = t08[(t08.control == "none") & (t08.held_out == held)].auroc.iloc[0]
        got = out[(out.block == 1) & (out.control == "none") & (out.held_out == held)].auroc.iloc[0]
        assert abs(got - ref) < 5e-4, f"block 1 / none / {held}: {got:.4f} vs EXP-031 {ref:.4f}"
    print("check passed: block 1 without control reproduces EXP-031 in every fold")

    deltas = []
    for b in range(1, 13):
        for ctrl in CONTROLS[1:]:
            per = []
            for held, _, _ in folds:
                yt, p0 = pred[(b, "none", held)]
                _, p1 = pred[(b, ctrl, held)]
                d, lo, hi = stats.paired_delta(yt, p0, p1, seed=seed)
                deltas.append({"block": b, "control": ctrl, "held_out": held, "delta_auroc": d, "ci_low": lo, "ci_high": hi})
                per.append((yt, p0, p1))
            d, lo, hi = stats.mean_over_folds(per, seed=seed)
            deltas.append({"block": b, "control": ctrl, "held_out": "MEAN over folds", "delta_auroc": d, "ci_low": lo, "ci_high": hi})
            print(f"block {b:2d} {ctrl:10s} ΔAUROC (orig − controlled) {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    deltas = pd.DataFrame(deltas)
    out.round(4).to_csv(ROOT / "results/tables/T13_fixed_block.csv", index=False)
    deltas.round(4).to_csv(ROOT / "results/tables/T13_fixed_block_deltas.csv", index=False)

    # Reading rule (EXP-055 README), applied to centring (i)
    m = deltas[(deltas.held_out == "MEAN over folds") & (deltas.control == "centring_i")].set_index("block")
    if (m.ci_low > 0).any():
        verdict = "harm hidden by selection"
    elif (m.loc[9:12].ci_high < 0).any():
        verdict = "obstacle, not shortcut"
    else:
        verdict = "no measurable effect at fixed block"
    print(f"\nEXP-055 reading rule (centring): {verdict}")

    # Figure: per-block mean AUROC per control (left), per-block ΔAUROC with CIs (right)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    mm = out[out.held_out == "MEAN over folds"]
    for ctrl in CONTROLS:
        d = mm[mm.control == ctrl].set_index("block").loc[range(1, 13)]
        ax[0].plot(d.index, d.auroc, "-o", ms=4, color=COLOUR[ctrl], label=LABEL[ctrl])
    ax[0].set(xlabel="LaBraM block", ylabel="mean LOCO AUROC", title="AUROC at a fixed block", xticks=range(1, 13))
    ax[0].legend(fontsize=8)
    for k, ctrl in enumerate(CONTROLS[1:]):
        d = m if ctrl == "centring_i" else deltas[(deltas.held_out == "MEAN over folds") & (deltas.control == ctrl)].set_index("block")
        d = d.loc[range(1, 13)]
        x = np.arange(1, 13) + 0.22 * (k - 1)
        ax[1].errorbar(x, d.delta_auroc, yerr=[d.delta_auroc - d.ci_low, d.ci_high - d.delta_auroc],
                       fmt="o", ms=4, capsize=2, color=COLOUR[ctrl], label=LABEL[ctrl])
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set(xlabel="LaBraM block", ylabel="ΔAUROC (original − controlled)", title="Effect of removal at a fixed block",
              xticks=range(1, 13))
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-055_fixed_block.png", dpi=150)


# ============================================================================ EXP-056
def within_cohort_auroc(y, p, cohort):
    return np.mean([roc_auc_score(y[cohort == c], p[cohort == c]) for c in np.unique(cohort)])


def boot_pooled(y, cohort, p0, p1, seed, n_boot=2000):
    """Paired stratified (cohort × diagnosis) bootstrap of ΔAUROC(pooled) and Δ(shortcut gap)."""
    rng = np.random.default_rng(seed)
    strata = np.array([f"{c}/{v}" for c, v in zip(cohort, y)])
    groups = [np.flatnonzero(strata == s) for s in np.unique(strata)]
    d_auc, d_gap = [], []
    for _ in range(n_boot):
        i = np.concatenate([rng.choice(g, len(g)) for g in groups])
        a0, a1 = roc_auc_score(y[i], p0[i]), roc_auc_score(y[i], p1[i])
        w0, w1 = within_cohort_auroc(y[i], p0[i], cohort[i]), within_cohort_auroc(y[i], p1[i], cohort[i])
        d_auc.append(a0 - a1)
        d_gap.append((a0 - w0) - (a1 - w1))
    return (np.percentile(d_auc, [2.5, 97.5]), np.percentile(d_gap, [2.5, 97.5]))


def pooled(z, meta, seed, n_rep, n_inlp, n_jobs):
    Z = z["Z_labram-base"]
    cands = control08.labram_candidates(Z, range(12))
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()
    split_jobs = control08.kfold(strata, n_rep, seed)           # the EXP-013 cohort-only baseline splits
    jobs = [(ctrl, rep, fold, tr, te) for ctrl in CONTROLS for rep, fold, tr, te in split_jobs]
    res = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(classify)(cands, y, tr, te, strata, seed + 1000 * rep + fold,
                          make_control(ctrl, cohort, y, inlp_iterations=n_inlp))
        for ctrl, rep, fold, tr, te in jobs)
    P = {c: np.full((n_rep, len(y)), np.nan) for c in CONTROLS}
    chosen = {c: [] for c in CONTROLS}
    for (ctrl, rep, fold, tr, te), (p, cand, C) in zip(jobs, res):
        P[ctrl][rep, te] = p
        chosen[ctrl].append(cand)
    assert not any(np.isnan(P[c]).any() for c in CONTROLS)

    rows = []
    for ctrl in CONTROLS:
        pa = P[ctrl].mean(0)
        pooled_auc, lo, hi = stats.bootstrap_auc(y, pa, seed=seed)
        within = within_cohort_auroc(y, pa, cohort)
        per_pooled = [roc_auc_score(y, P[ctrl][r]) for r in range(n_rep)]
        per_within = [within_cohort_auroc(y, P[ctrl][r], cohort) for r in range(n_rep)]
        row = {"control": ctrl, "pooled_auroc": pooled_auc, "pooled_ci_low": lo, "pooled_ci_high": hi,
               "within_cohort_auroc": within, "shortcut_gap": pooled_auc - within,
               "pooled_mean_over_repeats": np.mean(per_pooled), "pooled_sd_over_repeats": np.std(per_pooled),
               "within_mean_over_repeats": np.mean(per_within), "within_sd_over_repeats": np.std(per_within),
               "most_selected": pd.Series(chosen[ctrl]).mode().iloc[0]}
        for c in np.unique(cohort):
            row[f"within_{c}"] = roc_auc_score(y[cohort == c], pa[cohort == c])
        if ctrl != "none":
            p0 = P["none"].mean(0)
            (alo, ahi), (glo, ghi) = boot_pooled(y, cohort, p0, pa, seed)
            row.update({"delta_pooled": roc_auc_score(y, p0) - pooled_auc, "delta_pooled_ci_low": alo, "delta_pooled_ci_high": ahi,
                        "delta_gap": (roc_auc_score(y, p0) - within_cohort_auroc(y, p0, cohort)) - (pooled_auc - within),
                        "delta_gap_ci_low": glo, "delta_gap_ci_high": ghi,
                        "delta_within": within_cohort_auroc(y, p0, cohort) - within})
        rows.append(row)
        print(f"pooled {ctrl:10s} AUROC {pooled_auc:.3f} [{lo:.3f}, {hi:.3f}]  within-cohort {within:.3f}  gap {pooled_auc - within:+.3f}"
              + (f"  Δpooled {row['delta_pooled']:+.3f} [{row['delta_pooled_ci_low']:+.3f}, {row['delta_pooled_ci_high']:+.3f}]"
                 f"  Δgap {row['delta_gap']:+.3f} [{row['delta_gap_ci_low']:+.3f}, {row['delta_gap_ci_high']:+.3f}]" if ctrl != "none" else ""))
    out = pd.DataFrame(rows)
    out.round(4).to_csv(ROOT / "results/tables/T13_pooled_control.csv", index=False)

    # Reading rule (EXP-056 README), centring (i)
    o, c = out.set_index("control").loc["none"], out.set_index("control").loc["centring_i"]
    if o.shortcut_gap < 0.03:
        verdict = "shortcut not exploited"
    elif (c.delta_pooled_ci_low > 0 or c.delta_gap_ci_low > 0) and c.delta_within <= 0.03:
        verdict = "controls remove the shortcut"
    else:
        verdict = "controls ineffective"
    print(f"\nEXP-056 reading rule (centring): {verdict}")

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    x = np.arange(len(CONTROLS))
    ax.bar(x - 0.2, out.pooled_auroc, 0.4, color=[COLOUR[c] for c in CONTROLS], label="pooled AUROC")
    ax.bar(x + 0.2, out.within_cohort_auroc, 0.4, color=[COLOUR[c] for c in CONTROLS], alpha=0.45, label="within-cohort AUROC")
    for i, r in out.iterrows():
        ax.text(x[i], max(r.pooled_auroc, r.within_cohort_auroc) + 0.01, f"gap {r.shortcut_gap:+.3f}", ha="center", fontsize=8)
    ax.set(xticks=x, xticklabels=[LABEL[c] for c in CONTROLS], ylabel="AUROC", ylim=(0.5, 1.0),
           title="Pooled CV: cohort shortcut available")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-056_pooled_control.png", dpi=150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["fixed_block", "pooled"])
    ap.add_argument("--n-jobs", type=int, default=20)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    z, meta = control08.load()
    if args.part == "fixed_block":
        fixed_block(z, meta, cfg["seed"], cfg["control"]["inlp_iterations"], args.n_jobs)
    else:
        pooled(z, meta, cfg["seed"], cfg["cv"]["within_cohort"]["n_repeats"], cfg["control"]["inlp_iterations"], args.n_jobs)


if __name__ == "__main__":
    main()
