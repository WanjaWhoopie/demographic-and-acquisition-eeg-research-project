"""Phase 7: nuisance probes (EXP-020 age/sex, EXP-021 cohort, EXP-022 nonlinear).

    python scripts/07_probes.py

For each representation (pretrained LaBraM, random-weights LaBraM, classical features):

EXP-020 (ds004504 only; the other cohorts have no demographics)
  age  : ridge, outer stratified 5-fold x 10 over participants; MAE, R² vs "predict training mean";
         also within HC only (age is not confounded with disease there, T7.1.4)
  sex  : logistic, AUROC and balanced accuracy; also within AD only and within HC only (T7.2)
  permutation test of the pretrained-LaBraM age and sex probes: labels shuffled, full nested
  pipeline re-run on one 5-fold split per permutation (D-029)
EXP-021 (all 176 participants)
  cohort: multinomial logistic, stratified on cohort x diagnosis, 5-fold x 5; balanced accuracy,
          macro-F1, confusion matrix; chance 1/3. Reference: classical features 0.687 (EXP-003).
  layer profile: the same probe on every block (patch-mean token, mean pooling, C = 1), descriptive
EXP-022
  MLP (64 hidden units) on the configuration most often selected by the linear probe, same splits

Outputs: results/tables/T07_*.csv, results/figures/EXP-021_layer_profile.png
"""
import argparse
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from collections import Counter, OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, mean_absolute_error, r2_score

from eegconf import probing, stats
from eegconf.evaluation import splits

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
N_JOBS = 20


def candidates(Z):
    c = OrderedDict()
    for b in range(11, -1, -1):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


def outer_splits(y, strata, n_repeats, seed):
    df = pd.DataFrame({"participant_id": np.arange(len(y)), "diagnosis": strata})
    return [(rep, tr, te) for rep, _, tr, te in splits.participant_kfold(df, n_splits=5, n_repeats=n_repeats, seed=seed)]


def run_probe(task, cands, y, strata, n_repeats, seed):
    """Nested probe over repeated outer folds. Returns per-repeat predictions and chosen configs."""
    jobs = outer_splits(y, strata if strata is not None else (y if task != "regression" else np.zeros(len(y))), n_repeats, seed)
    res = Parallel(n_jobs=N_JOBS)(delayed(probing.select_and_fit)(task, cands, y, tr, te, strata, 5, seed + 997 * rep + i)
                                  for i, (rep, tr, te) in enumerate(jobs))
    P = np.empty((n_repeats, len(y)), dtype=object if task == "multiclass" else float)
    chosen = []
    for (rep, tr, te), (name, h, s, pred) in zip(jobs, res):
        P[rep, te] = pred
        chosen.append(name)
    return P, chosen, jobs


def regression_summary(y, P, jobs):
    maes, r2s, base = [], [], []
    for r in range(P.shape[0]):
        maes.append(mean_absolute_error(y, P[r].astype(float)))
        r2s.append(r2_score(y, P[r].astype(float)))
    # baseline: each test participant predicted by their training fold's mean age
    Pb = np.empty_like(P, dtype=float)
    for rep, tr, te in jobs:
        Pb[rep, te] = y[tr].mean()
    base = [mean_absolute_error(y, Pb[r]) for r in range(P.shape[0])]
    return {"mae": np.mean(maes), "mae_sd": np.std(maes), "r2": np.mean(r2s), "r2_sd": np.std(r2s),
            "baseline_mae": np.mean(base)}


def perm_test(task, cands, y, observed, n_perm, seed):
    """Permutation p-value: shuffle the labels n_perm times and re-run the full nested probe on one
    5-fold split each time (_perm_worker). p = (1 + #null >= observed) / (1 + n_perm)."""
    rng = np.random.default_rng(seed)
    perms = [rng.permutation(y) for _ in range(n_perm)]
    null = np.array(Parallel(n_jobs=N_JOBS)(delayed(_perm_worker)(task, cands, perms[k], seed + 1 + k) for k in range(n_perm)))
    return (1 + np.sum(null >= observed)) / (1 + n_perm), null


def _perm_worker(task, cands, y, seed):
    """Nested probe on ONE stratified 5-fold split; returns -MAE (age) or AUROC (sex).
    Used both for the observed statistic and for every permutation, so they are comparable."""
    strata = None if task == "regression" else y
    jobs = outer_splits(y, strata if strata is not None else np.zeros(len(y)), 1, seed)
    P = np.empty(len(y))
    for _, tr, te in jobs:
        P[te] = probing.select_and_fit(task, cands, y, tr, te, strata, 5, seed)[3]
    return -mean_absolute_error(y, P) if task == "regression" else stats.metrics(y, P)["auroc"]


def main():
    # --only-mlp re-runs EXP-022 alone, reading the linear-probe selections from the saved
    # T07_selected_configs.csv (used after the D-030 fix; EXP-020/021 are not recomputed).
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-mlp", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    seed, n_rep = cfg["seed"], cfg["cv"]["within_cohort"]["n_repeats"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "diagnosis", "age", "sex")})
    reps = OrderedDict([("labram", candidates(z["Z_labram-base"])),
                        ("random", candidates(z["Z_labram-random"])),
                        ("classical", OrderedDict(classical=z["classical"]))])
    tables = ROOT / "results/tables"
    rows, chosen_all = [], []
    ds = np.flatnonzero(meta["cohort"] == "ds004504")
    age, sex, dx = meta["age"].to_numpy(float), meta["sex"].to_numpy(float), meta["diagnosis"].to_numpy(int)
    yc = meta["cohort"].to_numpy()
    strata = (meta["cohort"] + "/" + meta["diagnosis"].astype(str)).to_numpy()

    if args.only_mlp:
        sel = pd.read_csv(tables / "T07_selected_configs.csv")
        chosen_all = [(r.probe, r.representation, r.data, r.candidate)
                      for r in sel.itertuples() for _ in range(r.times_chosen)]
        run_mlp(reps, chosen_all, yc, strata, sex, age, ds, seed, tables)
        return

    # ---------------- EXP-020: age and sex within ds004504
    subsets = {"ds004504 all (36 AD / 29 HC)": ds, "ds004504 HC only": ds[dx[ds] == 0], "ds004504 AD only": ds[dx[ds] == 1]}
    for name, cands in reps.items():
        for label, idx in subsets.items():
            sub = OrderedDict((k, v[idx]) for k, v in cands.items())
            # age (all and HC only, T7.1.4)
            if label != "ds004504 AD only":
                P, ch, jobs = run_probe("regression", sub, age[idx], None, n_rep, seed)
                s = regression_summary(age[idx], P, jobs)
                rows.append({"probe": "age", "representation": name, "data": label, "n": len(idx), **s})
                chosen_all += [("age", name, label, c) for c in ch]
                print(f"age  {name:9s} {label:28s} MAE {s['mae']:.2f} (baseline {s['baseline_mae']:.2f}) R2 {s['r2']:.3f}")
            # sex (all, within AD, within HC; T7.2)
            ys = sex[idx].astype(int)
            P, ch, _ = run_probe("binary", sub, ys, ys, n_rep, seed)
            p = P.astype(float).mean(0)
            auc, lo, hi = stats.bootstrap_auc(ys, p, seed=seed)
            m = stats.metrics(ys, p)
            rows.append({"probe": "sex", "representation": name, "data": label, "n": len(idx), "n_female": int(ys.sum()),
                         "auroc": auc, "ci_low": lo, "ci_high": hi, "balanced_accuracy": m["balanced_accuracy"],
                         "auroc_sd_over_repeats": np.std([stats.metrics(ys, P[r].astype(float))["auroc"] for r in range(n_rep)])})
            chosen_all += [("sex", name, label, c) for c in ch]
            print(f"sex  {name:9s} {label:28s} AUROC {auc:.3f} [{lo:.3f}, {hi:.3f}]")
    pd.DataFrame(rows).round(4).to_csv(tables / "T07_age_sex_probes.csv", index=False)

    # permutation tests for the pretrained-LaBraM probes on all ds004504 participants (D-029)
    n_perm = cfg["probes"]["permutations"]
    sub = OrderedDict((k, v[ds]) for k, v in reps["labram"].items())
    perm_rows = []
    n_perm_by_task = {"regression": n_perm, "binary": cfg["probes"].get("permutations_logistic", n_perm)}
    for task, y in (("regression", age[ds]), ("binary", sex[ds].astype(int))):
        observed = _perm_worker(task, sub, y, seed)       # same single-split pipeline as the null
        p, null = perm_test(task, sub, y, observed, n_perm_by_task[task], seed)
        perm_rows.append({"probe": "age" if task == "regression" else "sex", "statistic": "-MAE" if task == "regression" else "AUROC",
                          "observed_single_split": observed, "null_mean": null.mean(), "null_95pct": np.percentile(null, 95),
                          "n_permutations": n_perm_by_task[task], "p_value": p})
        print(f"perm {perm_rows[-1]['probe']}: observed {observed:.3f}, null 95th pct {np.percentile(null, 95):.3f}, p = {p:.4f}")
    pd.DataFrame(perm_rows).round(4).to_csv(tables / "T07_permutation_tests.csv", index=False)

    # ---------------- EXP-021: cohort probe on all participants
    crow, conf = [], {}
    for name, cands in reps.items():
        P, ch, _ = run_probe("multiclass", cands, yc, strata, 5, seed)
        ba = [balanced_accuracy_score(yc, P[r]) for r in range(5)]
        f1 = [f1_score(yc, P[r], average="macro") for r in range(5)]
        labels = sorted(set(yc))
        cm = sum(confusion_matrix(yc, P[r], labels=labels) for r in range(5))
        conf[name] = pd.DataFrame(cm, index=[f"true {l}" for l in labels], columns=[f"pred {l}" for l in labels])
        crow.append({"representation": name, "balanced_accuracy": np.mean(ba), "balanced_accuracy_sd": np.std(ba),
                     "macro_f1": np.mean(f1), "chance": 1 / len(labels),
                     "most_selected": Counter(ch).most_common(1)[0][0]})
        chosen_all += [("cohort", name, "all", c) for c in ch]
        print(f"cohort {name:9s} balanced accuracy {np.mean(ba):.3f} ± {np.std(ba):.3f}")
    pd.DataFrame(crow).round(4).to_csv(tables / "T07_cohort_probe.csv", index=False)
    pd.concat(conf, names=["representation"]).to_csv(tables / "T07_cohort_confusion.csv")

    # layer profile (descriptive): fixed token/pooling and C, every block, both LaBraM models
    prof = []
    for name in ("labram", "random"):
        Z = z["Z_labram-base" if name == "labram" else "Z_labram-random"]
        for b in range(12):
            X = Z[:, b, 0, 0, :]                        # block b, patch-mean token, mean pooling
            jobs = outer_splits(yc, strata, 5, seed)
            res = Parallel(n_jobs=N_JOBS)(delayed(_fixed_multiclass)(X, yc, tr, te) for _, tr, te in jobs)
            P = np.empty((5, len(yc)), dtype=object)
            for (rep, tr, te), pred in zip(jobs, res):
                P[rep, te] = pred
            prof.append({"representation": name, "block": b + 1,
                         "balanced_accuracy": np.mean([balanced_accuracy_score(yc, P[r]) for r in range(5)])})
    prof = pd.DataFrame(prof)
    prof.round(4).to_csv(tables / "T07_cohort_layer_profile.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for name, style in (("labram", "-o"), ("random", "--s")):
        d = prof[prof.representation == name]
        ax.plot(d.block, d.balanced_accuracy, style, label=f"{name} LaBraM")
    ax.axhline(crow[2]["balanced_accuracy"], color="grey", ls=":", label="classical features")
    ax.axhline(1 / 3, color="k", lw=0.8, label="chance")
    ax.set(xlabel="LaBraM block", ylabel="cohort balanced accuracy", ylim=(0, 1.02),
           title="Cohort identity readable from each block (patch-mean, mean pooling)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-021_layer_profile.png", dpi=150)

    pd.DataFrame(chosen_all, columns=["probe", "representation", "data", "candidate"]).groupby(
        ["probe", "representation", "data", "candidate"]).size().rename("times_chosen").reset_index().to_csv(
        tables / "T07_selected_configs.csv", index=False)
    run_mlp(reps, chosen_all, yc, strata, sex, age, ds, seed, tables)
    print("\ntables -> results/tables/T07_*.csv")


def run_mlp(reps, chosen_all, yc, strata, sex, age, ds, seed, tables):
    """EXP-022: MLP (64 hidden units) on the pretrained-LaBraM configuration that the linear probe
    selected most often for each nuisance variable, on the same outer splits (5 repeats)."""
    mrows = []
    for probe, task, y, idx, strat in (("cohort", "multiclass", yc, np.arange(len(yc)), strata),
                                       ("sex", "binary", sex.astype(float), ds, None),
                                       ("age", "regression", age, ds, None)):
        cfg_name = Counter(c for p_, r_, d_, c in chosen_all if p_ == probe and r_ == "labram"
                           and d_ in ("all", "ds004504 all (36 AD / 29 HC)")).most_common(1)[0][0]
        X = reps["labram"][cfg_name][idx]
        yy = y[idx] if probe != "sex" else y[idx].astype(int)
        jobs = outer_splits(yy, strat[idx] if strat is not None else (yy if task == "binary" else np.zeros(len(yy))), 5, seed)
        out = Parallel(n_jobs=N_JOBS)(delayed(_mlp_fold)(task, X, yy, tr, te, seed + i) for i, (_, tr, te) in enumerate(jobs))
        P = np.empty((5, len(yy)), dtype=object if task == "multiclass" else float)
        for (rep, tr, te), pred in zip(jobs, out):
            P[rep, te] = pred
        if task == "multiclass":
            val = np.mean([balanced_accuracy_score(yy, P[r]) for r in range(5)]); metric = "balanced_accuracy"
        elif task == "binary":
            val = np.mean([stats.metrics(yy, P[r].astype(float))["auroc"] for r in range(5)]); metric = "auroc"
        else:
            val = np.mean([mean_absolute_error(yy, P[r].astype(float)) for r in range(5)]); metric = "mae"
        mrows.append({"probe": probe, "representation": f"labram {cfg_name}", "model": "MLP(64)", "metric": metric, "value": val})
        print(f"mlp  {probe:6s} {metric} {val:.3f}")
    pd.DataFrame(mrows).round(4).to_csv(tables / "T07_mlp_probes.csv", index=False)


def _fixed_multiclass(X, y, tr, te):
    return probing.make_probe("multiclass", 1.0).fit(X[tr], y[tr]).predict(X[te])


def _mlp_fold(task, X, y, tr, te, seed):
    m = probing.make_mlp(task, seed).fit(X[tr], y[tr])
    return probing.predict(task, m, X[te])


if __name__ == "__main__":
    main()
