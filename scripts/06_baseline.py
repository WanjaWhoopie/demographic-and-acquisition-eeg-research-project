"""Phase 6: baseline AD-vs-HC classification (EXP-010, EXP-011, EXP-012, EXP-013).

    python scripts/06_baseline.py            # everything
    python scripts/06_baseline.py --quick    # 1 repeat, 2 blocks: smoke test only, writes nothing

Representations compared (all with the same classifier, src/eegconf/evaluation/model.py):
  labram   frozen pretrained LaBraM; block x token x pooling x C chosen inside training folds (D-024)
  random   the same with untrained LaBraM weights (negative control, EXP-013)
  classical relative band power + aperiodic exponents (EXP-012); only C is selected

Analyses
  within   each cohort: stratified 5-fold x 10 repeats over participants (EXP-010)
  loco     train on two cohorts, test on the third (EXP-011)
  nuisance age+sex within ds004504; cohort one-hot pooled (EXP-013)

Outputs
  results/runs/EXP-01x/*.csv                participant-level predictions (local, git-ignored)
  results/tables/T06_within_cohort.csv      per cohort x representation
  results/tables/T06_loco.csv               per held-out cohort x representation + mean over folds
  results/tables/T06_loco_deltas.csv        LaBraM minus classical / random, paired per fold
  results/tables/T06_nuisance_baselines.csv
  results/tables/T06_selected_configs.csv   how often each block/token/pooling/C was chosen
"""
import os

# One BLAS thread per worker: parallelism comes from running folds side by side.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from eegconf import stats
from eegconf.evaluation import model, splits

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ("patch_mean", "cls")
POOLINGS = ("mean", "median")


# ----------------------------------------------------------------------------- inputs
def load():
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis", "age", "sex", "n_epochs")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    return z, meta


def labram_candidates(Z, blocks=range(12)):
    """Ordered candidates (D-024 tie-break: later block, patch-mean token, mean pooling first)."""
    c = OrderedDict()
    for b in sorted(blocks, reverse=True):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


# ----------------------------------------------------------------------------- one outer fold
def run_fold(cands, y, tr, te, strata, seed):
    f = model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed)
    return te, f.proba, f.candidate, f.C, f.inner_auc


def within_cohort(name, cands, meta, cohort, n_repeats, seed, n_jobs):
    """EXP-010 / EXP-012 within-cohort: repeated stratified K-fold over this cohort's participants."""
    idx = np.flatnonzero(meta["cohort"] == cohort)
    sub = meta.iloc[idx].reset_index(drop=True)
    y = sub["diagnosis"].to_numpy()
    sub_c = OrderedDict((k, v[idx]) for k, v in cands.items())
    jobs = [(rep, fold, tr, te) for rep, fold, tr, te in
            splits.participant_kfold(sub.assign(diagnosis=y), n_splits=5, n_repeats=n_repeats, seed=seed)]
    res = Parallel(n_jobs=n_jobs)(delayed(run_fold)(sub_c, y, tr, te, None, seed + 1000 * rep + fold)
                                  for rep, fold, tr, te in jobs)
    P = np.full((n_repeats, len(y)), np.nan)
    chosen = []
    for (rep, fold, _, _), (te, p, cand, C, _) in zip(jobs, res):
        P[rep, te] = p
        chosen.append((name, f"within:{cohort}", cand, C))
    per_rep = [stats.metrics(y, P[r])["auroc"] for r in range(n_repeats)]
    p_mean = P.mean(axis=0)
    auc, lo, hi = stats.bootstrap_auc(y, p_mean, seed=seed)
    m = stats.metrics(y, p_mean)
    row = {"representation": name, "cohort": cohort, "n_AD": int(y.sum()), "n_HC": int((1 - y).sum()),
           "auroc_mean_over_repeats": np.mean(per_rep), "auroc_sd_over_repeats": np.std(per_rep),
           "auroc_avg_proba": auc, "ci_low": lo, "ci_high": hi,
           **{k: v for k, v in m.items() if k != "auroc"}}
    preds = sub[["global_id", "cohort", "diagnosis"]].assign(representation=name, proba=p_mean)
    return row, preds, chosen


def loco(name, cands, meta, seed, n_jobs):
    """EXP-011 / EXP-012 LOCO: train on two cohorts, test on the held-out one."""
    y = meta["diagnosis"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()
    folds = list(splits.leave_one_cohort_out(meta))
    res = Parallel(n_jobs=min(n_jobs, len(folds)))(
        delayed(run_fold)(cands, y, tr, te, strata, seed) for _, tr, te in folds)
    rows, preds, chosen, fold_preds = [], [], [], {}
    for (cohort, tr, te), (_, p, cand, C, inner) in zip(folds, res):
        auc, lo, hi = stats.bootstrap_auc(y[te], p, seed=seed)
        m = stats.metrics(y[te], p)
        rows.append({"representation": name, "held_out": cohort, "n_AD": int(y[te].sum()), "n_HC": int((1 - y[te]).sum()),
                     "auroc": auc, "ci_low": lo, "ci_high": hi, "selected": cand, "C": C, "inner_cv_auroc": inner,
                     **{k: v for k, v in m.items() if k != "auroc"}})
        preds.append(meta.iloc[te][["global_id", "cohort", "diagnosis"]].assign(representation=name, proba=p))
        chosen.append((name, f"loco:{cohort}", cand, C))
        fold_preds[cohort] = (y[te], p)
    est, lo, hi = stats.mean_over_folds(list(fold_preds.values()), seed=seed)
    pooled = pd.concat(preds)
    rows.append({"representation": name, "held_out": "MEAN over folds", "auroc": est, "ci_low": lo, "ci_high": hi})
    pa, plo, phi = stats.bootstrap_auc(pooled["diagnosis"], pooled["proba"], seed=seed)
    rows.append({"representation": name, "held_out": "POOLED (secondary)", "auroc": pa, "ci_low": plo, "ci_high": phi})
    return rows, pooled, chosen, fold_preds


# ----------------------------------------------------------------------------- nuisance-only
def nuisance(meta, n_repeats, seed):
    rows = []
    # (1) age + sex within ds004504
    ds = meta[meta["cohort"] == "ds004504"].reset_index(drop=True)
    X, y = ds[["age", "sex"]].to_numpy(float), ds["diagnosis"].to_numpy()
    P = np.zeros((n_repeats, len(y)))
    for rep, fold, tr, te in splits.participant_kfold(ds, n_splits=5, n_repeats=n_repeats, seed=seed):
        P[rep, te] = model.fixed_fit(X, y, tr, te)
    auc, lo, hi = stats.bootstrap_auc(y, P.mean(0), seed=seed)
    rows.append({"baseline": "age + sex -> AD", "data": "ds004504 (36 AD / 29 HC)", "cv": "stratified 5-fold x 10",
                 "auroc": auc, "ci_low": lo, "ci_high": hi})
    # (2) cohort one-hot -> AD, pooled
    X = pd.get_dummies(meta["cohort"]).to_numpy(float)
    y = meta["diagnosis"].to_numpy()
    strat = meta.assign(diagnosis=meta["cohort"] + "/" + meta["diagnosis"].astype(str))
    P = np.zeros((n_repeats, len(y)))
    for rep, fold, tr, te in splits.participant_kfold(strat, n_splits=5, n_repeats=n_repeats, seed=seed):
        P[rep, te] = model.fixed_fit(X, y, tr, te)
    auc, lo, hi = stats.bootstrap_auc(y, P.mean(0), seed=seed)
    rows.append({"baseline": "cohort identity -> AD", "data": "all 176 pooled", "cv": "stratified (cohort x dx) 5-fold x 10",
                 "auroc": auc, "ci_low": lo, "ci_high": hi})
    return rows


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--n-jobs", type=int, default=20)
    args = ap.parse_args()
    seed = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))["seed"]
    n_rep = 1 if args.quick else yaml.safe_load(open(ROOT / "configs/analysis.yaml"))["cv"]["within_cohort"]["n_repeats"]
    blocks = (11, 5) if args.quick else range(12)

    z, meta = load()
    reps = OrderedDict([
        ("labram", labram_candidates(z["Z_labram-base"], blocks)),
        ("random", labram_candidates(z["Z_labram-random"], blocks)),
        ("classical", OrderedDict(classical=z["classical"])),
    ])

    within_rows, loco_rows, chosen, all_preds, fold_preds = [], [], [], [], {}
    for name, cands in reps.items():
        for cohort in ("ds004504", "ADFSU", "APAVA"):
            row, preds, ch = within_cohort(name, cands, meta, cohort, n_rep, seed, args.n_jobs)
            within_rows.append(row); chosen += ch; all_preds.append(preds.assign(analysis="within"))
            print(f"within {cohort:9s} {name:9s} AUROC {row['auroc_mean_over_repeats']:.3f} ± {row['auroc_sd_over_repeats']:.3f}")
        rows, pooled, ch, fp = loco(name, cands, meta, seed, args.n_jobs)
        loco_rows += rows; chosen += ch; all_preds.append(pooled.assign(analysis="loco")); fold_preds[name] = fp
        for r in rows:
            print(f"loco   {r['held_out']:18s} {name:9s} AUROC {r['auroc']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]")

    # LaBraM vs classical / random: paired ΔAUROC per LOCO fold and mean over folds
    delta_rows = []
    for other in ("classical", "random"):
        per = []
        for cohort, (y, p_l) in fold_preds["labram"].items():
            _, p_o = fold_preds[other][cohort]
            d, lo, hi = stats.paired_delta(y, p_l, p_o, seed=seed)
            delta_rows.append({"comparison": f"labram - {other}", "held_out": cohort, "delta_auroc": d, "ci_low": lo, "ci_high": hi})
            per.append((y, p_l, p_o))
        d, lo, hi = stats.mean_over_folds(per, seed=seed)
        delta_rows.append({"comparison": f"labram - {other}", "held_out": "MEAN over folds", "delta_auroc": d, "ci_low": lo, "ci_high": hi})

    nuis = nuisance(meta, n_rep, seed)
    for r in nuis:
        print(f"nuisance {r['baseline']:24s} AUROC {r['auroc']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]")

    if args.quick:
        print("\n--quick: nothing written")
        return
    tables = ROOT / "results/tables"
    rnd = lambda df: df.round(4)
    rnd(pd.DataFrame(within_rows)).to_csv(tables / "T06_within_cohort.csv", index=False)
    rnd(pd.DataFrame(loco_rows)).to_csv(tables / "T06_loco.csv", index=False)
    rnd(pd.DataFrame(delta_rows)).to_csv(tables / "T06_loco_deltas.csv", index=False)
    rnd(pd.DataFrame(nuis)).to_csv(tables / "T06_nuisance_baselines.csv", index=False)
    ch = pd.DataFrame(chosen, columns=["representation", "analysis", "candidate", "C"])
    ch["block"] = ch["candidate"].str.extract(r"b(\d+)_")[0]
    ch["token"] = ch["candidate"].str.extract(r"_(patch_mean|cls)_")[0]
    ch["pooling"] = ch["candidate"].str.extract(r"_(mean|median)$")[0]
    ch.groupby(["representation", "analysis", "block", "token", "pooling"], dropna=False).size().rename("times_chosen") \
      .reset_index().to_csv(tables / "T06_selected_configs.csv", index=False)
    runs = ROOT / "results/runs"
    for e in ("EXP-010", "EXP-011", "EXP-012", "EXP-013"):
        (runs / e).mkdir(parents=True, exist_ok=True)
    preds = pd.concat(all_preds)
    preds.to_csv(runs / "EXP-011" / "predictions.csv", index=False)
    print("\ntables -> results/tables/T06_*.csv; predictions -> results/runs/EXP-011/predictions.csv")


if __name__ == "__main__":
    main()
