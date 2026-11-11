"""EXP-053 (exploratory, D-035): is the amount of EEG per participant a hidden cohort effect?

    python scripts/11_data_amount.py [--n-jobs 20] [--rebuild]

Motivation: with 8 s per participant (EXP-043) LaBraM transferred across cohorts at 0.928, against
0.853 with all clean data (EXP-011). Clean epochs per participant differ strongly by cohort
(ADFSU always 2; APAVA median ~30; ds004504 median ~180), so the participant representation is an
average over very different numbers of epochs depending on the cohort.

Design: for k in {1, 2, 4, 8, 16, 32, 64, all}, each participant's representation is pooled from
their first min(k, n_i) clean epochs in time order ("capped" design: all 176 participants at every
k; ADFSU stays at 2 epochs throughout, so the cross-cohort imbalance in data amount grows with k).

Per k:
  (a) LOCO AD classification (nested selection, D-024), original and centring (i):
      mean AUROC with CI, and the centring ΔAUROC;
  (b) within-cohort AD classification in ds004504 (every participant has >= 68 epochs, so k is
      exact there): 5-fold x 10, the EXP-010 splits. Separates "more data helps AD detection"
      from "unequal data across cohorts hurts transfer";
  (c) cohort probe (descriptive; fixed configuration, multinomial logistic C = 1, stratified
      5-fold x 5) on block 1 and block 11, patch-mean token, mean pooling;
  (d) dispersion: mean distance of participants to their cohort centroid (block 11, standardised
      over all participants), per cohort; averaging more epochs should shrink it.
Paired contrast: LOCO AUROC at each k minus at all epochs, mean over folds with CI.

Checks: k = all must equal the stored Z (EXP-011 inputs); k = 2 must equal Z8 wherever has_8s.

Outputs: results/tables/T11_data_amount.csv, T11_data_amount_paired.csv, T11_dispersion.csv,
results/figures/EXP-053_data_amount.png; pooled features cached in data/features/data_amount.npz.
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
from sklearn.metrics import balanced_accuracy_score

from eegconf import probing, stats
from eegconf.control import make_control
from eegconf.evaluation import model, splits
from eegconf.representation import participant_tensor

ROOT = Path(__file__).resolve().parents[1]
KS = (1, 2, 4, 8, 16, 32, 64, None)                      # None = all clean epochs
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")


def k_label(k):
    return "all" if k is None else str(k)


def build(meta, z, rebuild):
    """Pool every participant's first min(k, n) epochs for each k; cached in data/features."""
    cache = ROOT / "data/features/data_amount.npz"
    if cache.exists() and not rebuild:
        c = np.load(cache)
        return c["Z"], c["n_used"]
    Z = np.empty((len(KS), len(meta), 12, 2, 2, 200), np.float32)
    n_used = np.empty((len(KS), len(meta)), int)
    for i, r in meta.iterrows():
        proc = np.load(ROOT / "data/processed" / r["cohort"] / f"{r['global_id']}.npz")
        emb = np.load(ROOT / "data/embeddings/labram-base" / r["cohort"] / f"{r['global_id']}.npz")
        order = np.argsort(proc["epoch_idx"])                # time order, as in 05_build_features
        for j, k in enumerate(KS):
            idx = order if k is None else order[:k]
            Z[j, i] = participant_tensor(emb, idx)
            n_used[j, i] = len(idx)
    # the all-epoch and 2-epoch tensors must reproduce the stored representations
    assert np.allclose(Z[KS.index(None)], z["Z_labram-base"]), "k = all differs from stored Z"
    h8 = z["has_8s"].astype(bool)
    assert np.allclose(Z[KS.index(2)][h8], z["Z8_labram-base"][h8]), "k = 2 differs from stored Z8"
    np.savez_compressed(cache, Z=Z, n_used=n_used)
    return Z, n_used


def candidates(Z):
    c = OrderedDict()
    for b in range(11, -1, -1):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


def classify(cands, y, tr, te, strata, seed, ctrl):
    return model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed, control=ctrl).proba


def cohort_fold(X, g, tr, te):
    return probing.make_probe("multiclass", 1.0).fit(X[tr], g[tr]).predict(X[te])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-jobs", type=int, default=20)
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    seed, n_rep = cfg["seed"], cfg["cv"]["within_cohort"]["n_repeats"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()
    Zk, n_used = build(meta, z, args.rebuild)
    print("built participant representations for k =", [k_label(k) for k in KS])

    folds = list(splits.leave_one_cohort_out(meta))
    ds = np.flatnonzero(cohort == "ds004504")
    yd = y[ds]
    within_splits = [(rep, fold, tr, te) for rep, fold, tr, te in splits.participant_kfold(
        pd.DataFrame({"participant_id": np.arange(len(ds)), "diagnosis": yd}), n_splits=5, n_repeats=n_rep, seed=seed)]

    # one parallel batch for (a) and (b) over every k
    jobs, calls = [], []
    for j, k in enumerate(KS):
        c = candidates(Zk[j])
        for ctrl in ("none", "centring_i"):
            for held, tr, te in folds:
                jobs.append(("loco", j, ctrl, held, te))
                calls.append(delayed(classify)(c, y, tr, te, strata, seed, make_control(ctrl, cohort, y)))
        cd = OrderedDict((n, v[ds]) for n, v in c.items())
        for rep, fold, tr, te in within_splits:
            jobs.append(("within", j, rep, fold, te))
            calls.append(delayed(classify)(cd, yd, tr, te, None, seed + 1000 * rep + fold, None))
    res = Parallel(n_jobs=args.n_jobs)(calls)

    loco = {}                                             # (j, ctrl) -> {held: (y, p)}
    within = {j: np.full((n_rep, len(ds)), np.nan) for j in range(len(KS))}
    for job, p in zip(jobs, res):
        if job[0] == "loco":
            _, j, ctrl, held, te = job
            loco.setdefault((j, ctrl), {})[held] = (y[te], p)
        else:
            _, j, rep, fold, te = job
            within[j][rep, te] = p

    rows, paired = [], []
    ref = KS.index(None)
    for j, k in enumerate(KS):
        f0, f1 = loco[(j, "none")], loco[(j, "centring_i")]
        a0 = stats.mean_over_folds(list(f0.values()), seed=seed)
        a1 = stats.mean_over_folds(list(f1.values()), seed=seed)
        d = stats.mean_over_folds([(f0[h][0], f0[h][1], f1[h][1]) for h in f0], seed=seed)
        per_rep = [stats.metrics(yd, within[j][r])["auroc"] for r in range(n_rep)]
        # (c) cohort probe on two fixed configurations
        probe = {}
        for b in (0, 10):
            X = Zk[j][:, b, 0, 0, :]
            sp = [(rep, tr, te) for rep, _, tr, te in splits.participant_kfold(
                pd.DataFrame({"participant_id": np.arange(len(y)), "diagnosis": strata}), n_splits=5, n_repeats=5, seed=seed)]
            out = Parallel(n_jobs=args.n_jobs)(delayed(cohort_fold)(X, cohort, tr, te) for _, tr, te in sp)
            P = np.empty((5, len(y)), dtype=object)
            for (rep, tr, te), pr in zip(sp, out):
                P[rep, te] = pr
            probe[b + 1] = np.mean([balanced_accuracy_score(cohort, P[r]) for r in range(5)])
        nu = pd.Series(n_used[j]).groupby(cohort).median()
        rows.append({"k_epochs": k_label(k), "median_epochs_ADFSU": nu["ADFSU"], "median_epochs_APAVA": nu["APAVA"],
                     "median_epochs_ds004504": nu["ds004504"],
                     "loco_auroc": a0[0], "loco_ci_low": a0[1], "loco_ci_high": a0[2],
                     **{f"loco_{h}": stats.metrics(*f0[h])["auroc"] for h in f0},
                     "loco_auroc_centred": a1[0], "centring_delta": d[0], "centring_delta_ci_low": d[1],
                     "centring_delta_ci_high": d[2],
                     "within_ds004504_auroc": np.mean(per_rep), "within_ds004504_sd": np.std(per_rep),
                     "cohort_probe_block1": probe[1], "cohort_probe_block11": probe[11]})
        if j != ref:
            g = loco[(ref, "none")]
            pd_ = stats.mean_over_folds([(f0[h][0], f0[h][1], g[h][1]) for h in f0], seed=seed)
            paired.append({"k_epochs": k_label(k), "delta_vs_all": pd_[0], "ci_low": pd_[1], "ci_high": pd_[2]})
        r = rows[-1]
        print(f"k={k_label(k):>3s}  LOCO {r['loco_auroc']:.3f} [{r['loco_ci_low']:.3f}, {r['loco_ci_high']:.3f}]  "
              f"centring Δ {r['centring_delta']:+.3f}  within ds004504 {r['within_ds004504_auroc']:.3f}  "
              f"cohort probe b1 {r['cohort_probe_block1']:.3f} b11 {r['cohort_probe_block11']:.3f}")
    for p in paired:
        print(f"LOCO AUROC(k={p['k_epochs']}) - AUROC(all) = {p['delta_vs_all']:+.3f} [{p['ci_low']:+.3f}, {p['ci_high']:+.3f}]")

    # (d) dispersion around the cohort centroid, block 11 patch-mean mean pooling
    disp = []
    for j, k in enumerate(KS):
        X = Zk[j][:, 10, 0, 0, :]
        X = (X - X.mean(0)) / (X.std(0) + 1e-12)
        for c in np.unique(cohort):
            Xc = X[cohort == c]
            disp.append({"k_epochs": k_label(k), "cohort": c,
                         "mean_distance_to_centroid": np.linalg.norm(Xc - Xc.mean(0), axis=1).mean()})

    tables = ROOT / "results/tables"
    pd.DataFrame(rows).round(4).to_csv(tables / "T11_data_amount.csv", index=False)
    pd.DataFrame(paired).round(4).to_csv(tables / "T11_data_amount_paired.csv", index=False)
    pd.DataFrame(disp).round(4).to_csv(tables / "T11_dispersion.csv", index=False)

    df = pd.DataFrame(rows)
    x = np.arange(len(KS))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].fill_between(x, df.loco_ci_low, df.loco_ci_high, alpha=0.2)
    ax[0].plot(x, df.loco_auroc, "-o", label="LOCO (unseen cohort)")
    ax[0].plot(x, df.loco_auroc_centred, "--s", label="LOCO, centred")
    ax[0].plot(x, df.within_ds004504_auroc, "-^", label="within ds004504")
    ax[0].set(xticks=x, xticklabels=df.k_epochs, xlabel="epochs per participant (4 s each; capped at what exists)",
              ylabel="AD vs HC AUROC", ylim=(0.6, 1.0), title="AD classification")
    ax[0].legend(fontsize=8)
    ax[1].plot(x, df.cohort_probe_block1, "-o", label="block 1")
    ax[1].plot(x, df.cohort_probe_block11, "-s", label="block 11")
    ax[1].axhline(1 / 3, color="k", lw=0.8, label="chance")
    ax[1].set(xticks=x, xticklabels=df.k_epochs, xlabel="epochs per participant", ylabel="balanced accuracy",
              ylim=(0, 1.02), title="Cohort identity readable")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-053_data_amount.png", dpi=150)
    print("\ntables -> results/tables/T11_*.csv; figure -> results/figures/EXP-053_data_amount.png")


if __name__ == "__main__":
    main()
