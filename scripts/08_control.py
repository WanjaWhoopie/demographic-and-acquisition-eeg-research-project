"""Phase 8: nuisance control (EXP-030 demographic, EXP-031 cohort centring, EXP-032 LEACE / INLP).

    python scripts/08_control.py [--n-jobs 20] [--quick]

All analyses use pretrained LaBraM with the same nested selection as Phase 6 (D-024); the control
is refitted inside every inner and outer training fold (D-031) via
evaluation.model.select_and_fit(control=...). ΔAUROC = AUROC(original Z) − AUROC(controlled Z*)
(D-026), paired: the same participants and splits for both.

EXP-031 / EXP-032 (LOCO, 3 folds)
  controls: none (re-runs EXP-011 as the paired reference), centring_i (primary, D-026),
  centring_ii, leace, inlp. Per-fold AUROC with stratified bootstrap CI, per-fold paired ΔAUROC,
  mean over folds with CI (stats.mean_over_folds).
EXP-030 (within ds004504, 5-fold × 10 repeats, the EXP-010 splits)
  controls: none, resid_all (OLS on age + sex, all training participants), resid_hc (fitted on
  training HC only, T8.1.4). ΔAUROC on repeat-averaged probabilities, paired bootstrap CI;
  also mean ± SD over repeats of the per-repeat ΔAUROC.
T8.4 verification of removal (descriptive)
  (a) inside each LOCO training set (2 cohorts, chance 0.5): cohort probes, linear (logistic C = 1)
      and MLP (64), on the configuration the AD classifier chose for that fold and control; the
      control is fitted on the probe's training rows only; stratified 5-fold × 5.
  (b) all 176 participants (3 cohorts, chance 1/3): the same probes on block 11, patch-mean, mean
      pooling (the configuration most selected in EXP-021), with and without each control.
  (c) T8.1.5: age (ridge alpha 10) and sex (logistic C = 1) probes in ds004504, plus MLP, with and
      without residualisation, on the configuration the AD classifier chose most often.

Outputs: results/tables/T08_*.csv; participant predictions results/runs/EXP-031/predictions.csv
(local, not in git; Phase 9 reads them).
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed
from sklearn.metrics import balanced_accuracy_score, mean_absolute_error

from eegconf import probing, stats
from eegconf.control import fit_apply, make_control
from eegconf.evaluation import model, splits

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
LOCO_CONTROLS = ("none", "centring_i", "centring_ii", "leace", "inlp")
DEMO_CONTROLS = ("none", "resid_all", "resid_hc")


# ----------------------------------------------------------------------------- inputs
def load():
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis", "age", "sex")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    return z, meta


def labram_candidates(Z, blocks):
    """Ordered candidates, same order and names as Phase 6 (D-024 tie-break)."""
    c = OrderedDict()
    for b in sorted(blocks, reverse=True):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


def kfold(labels, n_repeats, seed):
    """Participant-level stratified 5-fold × n_repeats on positions 0..n-1 (labels = strata)."""
    df = pd.DataFrame({"participant_id": np.arange(len(labels)), "diagnosis": labels})
    return [(rep, fold, tr, te) for rep, fold, tr, te in
            splits.participant_kfold(df, n_splits=5, n_repeats=n_repeats, seed=seed)]


# ----------------------------------------------------------------------------- one outer fold
def classify(cands, y, tr, te, strata, seed, ctrl):
    f = model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed, control=ctrl)
    return f.proba, f.candidate, f.C, f.inner_auc


def probe_fold(X, target, task, fit_rows, test_rows, ctrl, mlp, seed):
    """Fit `ctrl` and a probe on fit_rows, predict test_rows (global indices into X/target)."""
    Xa, Xb = fit_apply(ctrl, X, fit_rows, [test_rows])
    h = {"regression": 10.0, "binary": 1.0, "multiclass": 1.0}[task]
    m = probing.make_mlp(task, seed) if mlp else probing.make_probe(task, h)
    m.fit(Xa, target[fit_rows])
    return probing.predict(task, m, Xb)


def probe_cv(X, target, task, rows, strata, ctrl, mlp, n_repeats, seed, n_jobs):
    """Repeated stratified 5-fold probe over `rows`; returns the per-repeat metric list."""
    jobs = kfold(strata[rows], n_repeats, seed)
    out = Parallel(n_jobs=n_jobs)(delayed(probe_fold)(X, target, task, rows[tr], rows[te], ctrl, mlp, seed + i)
                                  for i, (_, _, tr, te) in enumerate(jobs))
    P = np.empty((n_repeats, len(rows)), dtype=object if task == "multiclass" else float)
    for (rep, _, _, te), pred in zip(jobs, out):
        P[rep, te] = pred
    yt = target[rows]
    if task == "multiclass":
        return [balanced_accuracy_score(yt, P[r]) for r in range(n_repeats)]
    if task == "binary":
        return [stats.metrics(yt.astype(int), P[r].astype(float))["auroc"] for r in range(n_repeats)]
    return [mean_absolute_error(yt, P[r].astype(float)) for r in range(n_repeats)]


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-jobs", type=int, default=20)
    ap.add_argument("--quick", action="store_true", help="smoke test: 3 blocks, 2 repeats, nothing written")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    seed = cfg["seed"]
    n_rep = 2 if args.quick else cfg["cv"]["within_cohort"]["n_repeats"]
    n_inlp = cfg["control"]["inlp_iterations"]
    z, meta = load()
    Z = z["Z_labram-base"]
    cands = labram_candidates(Z, [0, 5, 11] if args.quick else range(12))
    y = meta["diagnosis"].to_numpy()
    cohort = meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()
    tables = ROOT / "results/tables"

    # ======================================================== EXP-031 / EXP-032: LOCO with controls
    folds = list(splits.leave_one_cohort_out(meta))
    jobs = [(ctrl, held, tr, te) for ctrl in LOCO_CONTROLS for held, tr, te in folds]
    res = Parallel(n_jobs=args.n_jobs)(
        delayed(classify)(cands, y, tr, te, strata, seed, make_control(ctrl, cohort, y, inlp_iterations=n_inlp))
        for ctrl, held, tr, te in jobs)
    rows, preds, fold_preds, chosen = [], [], {}, {}
    for (ctrl, held, tr, te), (p, cand, C, inner) in zip(jobs, res):
        auc, lo, hi = stats.bootstrap_auc(y[te], p, seed=seed)
        m = stats.metrics(y[te], p)
        rows.append({"control": ctrl, "held_out": held, "auroc": auc, "ci_low": lo, "ci_high": hi, "selected": cand,
                     "C": C, "inner_cv_auroc": inner, **{k: v for k, v in m.items() if k != "auroc"}})
        preds.append(meta.iloc[te][["global_id", "cohort", "diagnosis"]].assign(control=ctrl, proba=p))
        fold_preds.setdefault(ctrl, {})[held] = (y[te], p)
        chosen[(ctrl, held)] = cand
        print(f"loco {ctrl:12s} {held:9s} AUROC {auc:.3f} [{lo:.3f}, {hi:.3f}]  {cand} C={C}")
    for ctrl in LOCO_CONTROLS:
        est, lo, hi = stats.mean_over_folds(list(fold_preds[ctrl].values()), seed=seed)
        rows.append({"control": ctrl, "held_out": "MEAN over folds", "auroc": est, "ci_low": lo, "ci_high": hi})
        print(f"loco {ctrl:12s} MEAN      AUROC {est:.3f} [{lo:.3f}, {hi:.3f}]")
    deltas = []
    for ctrl in LOCO_CONTROLS[1:]:
        per = []
        for held, (yt, p0) in fold_preds["none"].items():
            _, p1 = fold_preds[ctrl][held]
            d, lo, hi = stats.paired_delta(yt, p0, p1, seed=seed)
            deltas.append({"control": ctrl, "held_out": held, "delta_auroc": d, "ci_low": lo, "ci_high": hi})
            per.append((yt, p0, p1))
        d, lo, hi = stats.mean_over_folds(per, seed=seed)
        deltas.append({"control": ctrl, "held_out": "MEAN over folds", "delta_auroc": d, "ci_low": lo, "ci_high": hi})
        print(f"delta {ctrl:12s} mean ΔAUROC (orig − controlled) {d:+.3f} [{lo:+.3f}, {hi:+.3f}]")

    # ======================================================== EXP-030: age/sex residualisation, ds004504
    ds = np.flatnonzero(cohort == "ds004504")
    yd = y[ds]
    cov = meta.iloc[ds][["age", "sex"]].to_numpy(float)
    cands_ds = OrderedDict((k, v[ds]) for k, v in cands.items())
    split_jobs = kfold(yd, n_rep, seed)                       # identical to the EXP-010 splits
    djobs = [(ctrl, rep, fold, tr, te) for ctrl in DEMO_CONTROLS for rep, fold, tr, te in split_jobs]
    dres = Parallel(n_jobs=args.n_jobs)(
        delayed(classify)(cands_ds, yd, tr, te, None, seed + 1000 * rep + fold, make_control(ctrl, y=yd, covariates=cov))
        for ctrl, rep, fold, tr, te in djobs)
    P = {c: np.full((n_rep, len(ds)), np.nan) for c in DEMO_CONTROLS}
    demo_chosen = {c: [] for c in DEMO_CONTROLS}
    for (ctrl, rep, fold, tr, te), (p, cand, C, _) in zip(djobs, dres):
        P[ctrl][rep, te] = p
        demo_chosen[ctrl].append(cand)
    drows = []
    for ctrl in DEMO_CONTROLS:
        per_rep = [stats.metrics(yd, P[ctrl][r])["auroc"] for r in range(n_rep)]
        auc, lo, hi = stats.bootstrap_auc(yd, P[ctrl].mean(0), seed=seed)
        row = {"control": ctrl, "auroc_mean_over_repeats": np.mean(per_rep), "auroc_sd_over_repeats": np.std(per_rep),
               "auroc_avg_proba": auc, "ci_low": lo, "ci_high": hi,
               "most_selected": Counter(demo_chosen[ctrl]).most_common(1)[0][0]}
        if ctrl != "none":
            d, dlo, dhi = stats.paired_delta(yd, P["none"].mean(0), P[ctrl].mean(0), seed=seed)
            per_d = [stats.metrics(yd, P["none"][r])["auroc"] - stats.metrics(yd, P[ctrl][r])["auroc"] for r in range(n_rep)]
            row.update({"delta_auroc": d, "delta_ci_low": dlo, "delta_ci_high": dhi,
                        "delta_mean_over_repeats": np.mean(per_d), "delta_sd_over_repeats": np.std(per_d)})
        drows.append(row)
        print(f"demo {ctrl:10s} AUROC {np.mean(per_rep):.3f} ± {np.std(per_rep):.3f}"
              + (f"  ΔAUROC {row['delta_auroc']:+.3f} [{row['delta_ci_low']:+.3f}, {row['delta_ci_high']:+.3f}]" if ctrl != "none" else ""))

    # ======================================================== T8.4 verification probes
    vrows = []
    vrep = 2 if args.quick else 5
    # (a) inside each LOCO training set: 2 cohorts, chance 0.5
    for ctrl in ("none", "centring_i", "leace", "inlp"):
        for held, tr, te in folds:
            X = cands[chosen[(ctrl, held)]]
            f = make_control(ctrl, cohort, y, inlp_iterations=n_inlp)
            for mlp in (False, True):
                ba = probe_cv(X, cohort, "multiclass", tr, strata, f, mlp, vrep, seed, args.n_jobs)
                vrows.append({"check": "cohort, within LOCO training set", "control": ctrl, "fold": f"held out {held}",
                              "config": chosen[(ctrl, held)], "probe": "MLP(64)" if mlp else "linear",
                              "metric": "balanced_accuracy", "value": np.mean(ba), "sd": np.std(ba), "chance": 0.5})
    # (b) all 176, 3 cohorts, chance 1/3, EXP-021 configuration
    cfg_b = "b11_patch_mean_mean" if "b11_patch_mean_mean" in cands else next(iter(cands))
    all_rows = np.arange(len(y))
    for ctrl in ("none", "centring_i", "leace", "inlp"):
        f = make_control(ctrl, cohort, y, inlp_iterations=n_inlp)
        for mlp in (False, True):
            ba = probe_cv(cands[cfg_b], cohort, "multiclass", all_rows, strata, f, mlp, vrep, seed, args.n_jobs)
            vrows.append({"check": "cohort, all 176", "control": ctrl, "fold": "5-fold", "config": cfg_b,
                          "probe": "MLP(64)" if mlp else "linear", "metric": "balanced_accuracy",
                          "value": np.mean(ba), "sd": np.std(ba), "chance": 1 / 3})
    # (c) T8.1.5: age and sex in ds004504 with and without residualisation
    age_g, sex_g = np.full(len(y), np.nan), np.full(len(y), np.nan)
    age_g[ds], sex_g[ds] = cov[:, 0], cov[:, 1]
    cov_g = np.c_[age_g, sex_g]
    for ctrl in DEMO_CONTROLS:
        cfg_c = Counter(demo_chosen[ctrl]).most_common(1)[0][0]
        f = make_control(ctrl, y=y, covariates=cov_g)
        for mlp in (False, True):
            mae = probe_cv(cands[cfg_c], age_g, "regression", ds, y, f, mlp, vrep, seed, args.n_jobs)
            auc = probe_cv(cands[cfg_c], sex_g, "binary", ds, sex_g.astype(str), f, mlp, vrep, seed, args.n_jobs)
            for name, metric, v in (("age, ds004504", "mae", mae), ("sex, ds004504", "auroc", auc)):
                vrows.append({"check": name, "control": ctrl, "fold": "5-fold", "config": cfg_c,
                              "probe": "MLP(64)" if mlp else "linear", "metric": metric, "value": np.mean(v), "sd": np.std(v),
                              "chance": 0.5 if metric == "auroc" else np.nan})
    for r in vrows:
        print(f"verify {r['check']:34s} {r['fold']:18s} {r['control']:11s} {r['probe']:8s} {r['metric']} {r['value']:.3f}")

    if args.quick:
        print("\n--quick: nothing written")
        return
    rnd = lambda d: d.round(4)
    rnd(pd.DataFrame(rows)).to_csv(tables / "T08_loco.csv", index=False)
    rnd(pd.DataFrame(deltas)).to_csv(tables / "T08_loco_deltas.csv", index=False)
    rnd(pd.DataFrame(drows)).to_csv(tables / "T08_demographic.csv", index=False)
    rnd(pd.DataFrame(vrows)).to_csv(tables / "T08_verification_probes.csv", index=False)
    run_dir = ROOT / "results/runs/EXP-031"
    run_dir.mkdir(parents=True, exist_ok=True)
    pd.concat(preds).to_csv(run_dir / "predictions.csv", index=False)
    print("\ntables -> results/tables/T08_*.csv; predictions -> results/runs/EXP-031/predictions.csv")


if __name__ == "__main__":
    main()
