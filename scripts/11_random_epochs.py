"""EXP-054 (exploratory, D-037): time in recording versus amount of data per participant.

    python scripts/11_random_epochs.py [--n-jobs 20]

EXP-053 pooled the *first* k clean epochs of each recording and found higher AD discrimination with
few epochs than with all of them, across cohorts and within ds004504. "First k" mixes two things:
how much EEG is pooled and where in the recording it comes from. This script separates them.

Arm 1, position at fixed amount: 8 consecutive clean epochs (time order) from the first, middle or
  last part of each participant's clean epochs. Participants with fewer than 8 use all of them.
Arm 2, amount at random position: k in {2, 8, 32} clean epochs drawn at random without replacement
  (capped at n), 5 draws per k (draw seeds 1-5).
Reference: all clean epochs; must reproduce EXP-011 (LOCO) and EXP-010 (within ds004504).

For each representation: LOCO AUROC with the nested classifier (D-024), original representation
only; within-ds004504 AUROC, 5-fold x 10 with the EXP-010 splits, from repeat-averaged
probabilities. Contrasts first-8 minus last-8 and first-8 minus middle-8 with paired bootstrap CIs.

Outputs: results/tables/T11_random_epochs.csv, T11_random_epochs_contrasts.csv,
results/figures/EXP-054_random_epochs.png
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from eegconf import stats
from eegconf.evaluation import model, splits
from eegconf.representation import participant_tensor

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
WINDOW = 8                                   # arm 1: epochs per position window (32 s)
RANDOM_KS, N_DRAWS = (2, 8, 32), 5           # arm 2


def selections(order, rngs):
    """Every epoch subset used for one participant, keyed by representation name.

    `order` is the participant's clean-epoch indices in time order. Random draws use their own
    generator per (draw, k), used for participants in a fixed order, so the draws are reproducible.
    """
    n = len(order)
    w = min(WINDOW, n)
    mid = (n - w) // 2
    sel = OrderedDict(all=order, first_8=order[:w], middle_8=order[mid:mid + w], last_8=order[n - w:])
    for k in RANDOM_KS:
        for d in rngs:
            sel[f"random_{k}_d{d}"] = rngs[d][k].choice(order, size=min(k, n), replace=False)
    return sel


def build(meta):
    """Participant representations (12 blocks x 2 tokens x 2 poolings x 200) for every selection."""
    rngs = {d: {k: np.random.default_rng([d, k]) for k in RANDOM_KS} for d in range(1, N_DRAWS + 1)}
    reps, n_used = OrderedDict(), OrderedDict()
    for i, r in meta.iterrows():
        proc = np.load(ROOT / "data/processed" / r["cohort"] / f"{r['global_id']}.npz")
        emb = np.load(ROOT / "data/embeddings/labram-base" / r["cohort"] / f"{r['global_id']}.npz")
        order = np.argsort(proc["epoch_idx"])                # time order, as in 05_build_features
        for name, idx in selections(order, rngs).items():
            reps.setdefault(name, np.empty((len(meta), 12, 2, 2, 200), np.float32))[i] = participant_tensor(emb, idx)
            n_used.setdefault(name, np.empty(len(meta), int))[i] = len(idx)
    return reps, n_used


def candidates(Z):
    """Same candidate order as 06/08/11_data_amount (tie-breaking depends on it)."""
    c = OrderedDict()
    for b in range(11, -1, -1):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


def classify(cands, y, tr, te, strata, seed):
    return model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed).proba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-jobs", type=int, default=20)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    seed, n_rep = cfg["seed"], cfg["cv"]["within_cohort"]["n_repeats"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()

    reps, n_used = build(meta)
    assert np.allclose(reps["all"], z["Z_labram-base"]), "all-epoch representation differs from stored Z"
    print(f"built {len(reps)} representations")

    folds = list(splits.leave_one_cohort_out(meta))
    ds = np.flatnonzero(cohort == "ds004504")
    yd = y[ds]
    within_splits = list(splits.participant_kfold(
        pd.DataFrame({"participant_id": np.arange(len(ds)), "diagnosis": yd}), n_splits=5, n_repeats=n_rep, seed=seed))

    # one parallel batch: LOCO folds and within-ds004504 folds for every representation
    jobs, calls = [], []
    for name, Z in reps.items():
        c = candidates(Z)
        for held, tr, te in folds:
            jobs.append(("loco", name, held, te))
            calls.append(delayed(classify)(c, y, tr, te, strata, seed))
        cd = OrderedDict((n, v[ds]) for n, v in c.items())
        for rep, fold, tr, te in within_splits:
            jobs.append(("within", name, rep, te))
            calls.append(delayed(classify)(cd, yd, tr, te, None, seed + 1000 * rep + fold))
    res = Parallel(n_jobs=args.n_jobs, verbose=5)(calls)

    loco = {}                                                 # name -> {held: (y, p)}
    within = {name: np.full((n_rep, len(ds)), np.nan) for name in reps}
    for job, p in zip(jobs, res):
        if job[0] == "loco":
            _, name, held, te = job
            loco.setdefault(name, {})[held] = (y[te], p)
        else:
            _, name, rep, te = job
            within[name][rep, te] = p
    wmean = {name: np.nanmean(P, axis=0) for name, P in within.items()}   # repeat-averaged

    # the all-epoch reference must reproduce EXP-011 and EXP-010 (headline values, 3 decimals)
    a_all = stats.mean_over_folds(list(loco["all"].values()), seed=seed)[0]
    w_all = np.mean([stats.metrics(yd, within["all"][r])["auroc"] for r in range(n_rep)])
    assert round(a_all, 3) == 0.853 and round(w_all, 3) == 0.821, f"reference not reproduced: {a_all}, {w_all}"

    rows = []
    for name in reps:
        a = stats.mean_over_folds(list(loco[name].values()), seed=seed)
        per_rep = [stats.metrics(yd, within[name][r])["auroc"] for r in range(n_rep)]
        nu = pd.Series(n_used[name]).groupby(cohort).median()
        rows.append({"representation": name, "median_epochs_ADFSU": nu["ADFSU"], "median_epochs_APAVA": nu["APAVA"],
                     "median_epochs_ds004504": nu["ds004504"], "loco_auroc": a[0], "loco_ci_low": a[1],
                     "loco_ci_high": a[2], **{f"loco_{h}": stats.metrics(*loco[name][h])["auroc"] for h in loco[name]},
                     "within_ds004504_auroc": np.mean(per_rep), "within_ds004504_sd": np.std(per_rep),
                     "within_ds004504_auroc_avgprob": stats.metrics(yd, wmean[name])["auroc"]})
    out = pd.DataFrame(rows)

    # summary over random draws: mean, min and max of the per-draw AUROCs
    summ = []
    for k in RANDOM_KS:
        d = out[out.representation.str.startswith(f"random_{k}_")]
        for col in ("loco_auroc", "within_ds004504_auroc"):
            summ.append({"representation": f"random_{k} (5 draws)", "metric": col, "mean": d[col].mean(),
                         "min": d[col].min(), "max": d[col].max()})
    summ = pd.DataFrame(summ)

    # paired contrasts: first-8 minus last-8 and minus middle-8
    con = []
    for other in ("last_8", "middle_8", "all"):
        f0, f1 = loco["first_8"], loco[other]
        d = stats.mean_over_folds([(f0[h][0], f0[h][1], f1[h][1]) for h in f0], seed=seed)
        con.append({"contrast": f"first_8 - {other}", "setting": "LOCO (mean over folds)",
                    "delta_auroc": d[0], "ci_low": d[1], "ci_high": d[2]})
        d = stats.paired_delta(yd, wmean["first_8"], wmean[other], seed=seed)
        con.append({"contrast": f"first_8 - {other}", "setting": "within ds004504 (repeat-averaged)",
                    "delta_auroc": d[0], "ci_low": d[1], "ci_high": d[2]})
    con = pd.DataFrame(con)

    tables = ROOT / "results/tables"
    out.round(4).to_csv(tables / "T11_random_epochs.csv", index=False)
    pd.concat([con, summ]).round(4).to_csv(tables / "T11_random_epochs_contrasts.csv", index=False)
    print(out[["representation", "loco_auroc", "loco_ci_low", "loco_ci_high", "within_ds004504_auroc",
               "within_ds004504_auroc_avgprob"]].round(3).to_string(index=False))
    print(summ.round(3).to_string(index=False))
    print(con.round(3).to_string(index=False))

    # figure: AUROC by representation; random draws as points with their mean
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for a, col, title in ((ax[0], "loco_auroc", "Unseen cohort (LOCO)"), (ax[1], "within_ds004504_auroc", "Within ds004504")):
        labels = ["first 8", "middle 8", "last 8"] + [f"random {k}" for k in RANDOM_KS] + ["all"]
        for i, name in enumerate(("first_8", "middle_8", "last_8")):
            a.plot(i, out.set_index("representation").loc[name, col], "o", color="C0")
        for j, k in enumerate(RANDOM_KS):
            v = out[out.representation.str.startswith(f"random_{k}_")][col]
            a.plot(np.full(len(v), 3 + j), v, ".", color="C1", alpha=0.6)
            a.plot(3 + j, v.mean(), "_", color="C1", ms=18, mew=2)
        a.plot(6, out.set_index("representation").loc["all", col], "s", color="k")
        a.set(xticks=range(7), xticklabels=labels, title=title)
        a.tick_params(axis="x", rotation=30)
    ax[0].set(ylabel="AD vs HC AUROC")
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-054_random_epochs.png", dpi=150)
    print("tables -> results/tables/T11_random_epochs*.csv; figure -> results/figures/EXP-054_random_epochs.png")


if __name__ == "__main__":
    main()
