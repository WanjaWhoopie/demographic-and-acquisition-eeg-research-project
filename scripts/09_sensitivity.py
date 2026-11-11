"""Phase 9: primary outcome (EXP-040) and sensitivity analyses (EXP-041 to EXP-044).

    python scripts/09_sensitivity.py [--part all|primary|no_adfsu|subsample|8s|scaled] [--n-jobs 20]

Every analysis compares the original representation with the primary controlled representation,
prevalence-balanced cohort centring variant (i) (D-026), in leave-one-cohort-out (LOCO) with the
same nested classifier as Phases 6 and 8. ΔAUROC = AUROC(original) − AUROC(centred).

EXP-040 primary   reads the EXP-031 predictions (no refitting); per-fold and mean ΔAUROC with CIs,
                  controlled mean AUROC with CI, and the pattern rule of D-027.
EXP-041 no ADFSU  ds004504 and APAVA only, 2 folds. With one training cohort, centring is a constant
                  shift that the classifier's standardisation cancels exactly, so ΔAUROC = 0 by
                  construction (D-033); the run confirms this and reports the original transfer.
EXP-042 subsample 100 draws (seeds 1-100); in each, ADFSU AD participants are subsampled to the
                  number of ADFSU HC (12) and the others dropped from training and testing; per-draw
                  point estimates; distribution reported as median and 2.5-97.5 percentiles.
EXP-043 8 s       Z8 (each participant's first two clean epochs, D-018); APAVA HC without 8 s excluded.
EXP-044 amplitude amplitude-scaled embeddings (every recording at the same overall SD, D-019, D-033).

Outputs: results/tables/T09_primary_and_sensitivity.csv (T9.4), T09_adfsu_subsample_draws.csv;
participant predictions results/runs/EXP-04x/predictions.csv (local; Phase 10 reads them).
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed

from eegconf import stats
from eegconf.control import make_control
from eegconf.evaluation import model, splits

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
CONTROLS = ("none", "centring_i")
TABLES = ROOT / "results/tables"


def labram_candidates(Z):
    """Ordered candidates, same order and names as Phases 6 and 8 (D-024 tie-break)."""
    c = OrderedDict()
    for b in range(11, -1, -1):
        for t, tok in enumerate(TOKENS):
            for q, pool in enumerate(POOLINGS):
                c[f"b{b + 1:02d}_{tok}_{pool}"] = Z[:, b, t, q, :]
    return c


def classify(cands, y, tr, te, strata, seed, ctrl):
    return model.select_and_fit(cands, y, tr, te, strata=strata, seed=seed, control=ctrl).proba


def loco_jobs(meta, rows):
    """LOCO folds over the participants in `rows` (positions into meta); indices are positions in rows."""
    sub = meta.iloc[rows].reset_index(drop=True)
    return sub, list(splits.leave_one_cohort_out(sub))


def run_loco(Z, meta, rows, seed, n_jobs, tag):
    """Original vs centring (i) LOCO on participants `rows`; returns {control: {held_out: (y, p)}} and predictions."""
    sub, folds = loco_jobs(meta, rows)
    cands = OrderedDict((k, v[rows]) for k, v in labram_candidates(Z).items())
    y, cohort = sub["diagnosis"].to_numpy(), sub["cohort"].to_numpy()
    strata = (sub["cohort"] + "/" + sub["diagnosis"].astype(str)).to_numpy()
    jobs = [(c, held, tr, te) for c in CONTROLS for held, tr, te in folds]
    res = Parallel(n_jobs=n_jobs)(delayed(classify)(cands, y, tr, te, strata, seed, make_control(c, cohort, y))
                                  for c, held, tr, te in jobs)
    fp, preds = {}, []
    for (c, held, tr, te), p in zip(jobs, res):
        fp.setdefault(c, {})[held] = (y[te], p)
        preds.append(sub.iloc[te][["global_id", "cohort", "diagnosis"]].assign(analysis=tag, control=c, proba=p))
    return fp, pd.concat(preds)


def summarise(fp, analysis, seed):
    """Per-fold and mean rows: AUROC(original), AUROC(centred), ΔAUROC with CIs, and the D-027 pattern."""
    rows, per = [], []
    for held, (y, p0) in fp["none"].items():
        _, p1 = fp["centring_i"][held]
        a0, a1 = stats.bootstrap_auc(y, p0, seed=seed), stats.bootstrap_auc(y, p1, seed=seed)
        d = stats.paired_delta(y, p0, p1, seed=seed)
        rows.append({"analysis": analysis, "held_out": held, "n_AD": int(y.sum()), "n_HC": int((1 - y).sum()),
                     "auroc_original": a0[0], "auroc_original_ci": f"[{a0[1]:.3f}, {a0[2]:.3f}]",
                     "auroc_centred": a1[0], "auroc_centred_ci": f"[{a1[1]:.3f}, {a1[2]:.3f}]",
                     "delta_auroc": d[0], "delta_ci_low": d[1], "delta_ci_high": d[2]})
        per.append((y, p0, p1))
    m0 = stats.mean_over_folds([(y, p0) for y, p0, _ in per], seed=seed)
    m1 = stats.mean_over_folds([(y, p1) for y, _, p1 in per], seed=seed)
    md = stats.mean_over_folds(per, seed=seed)
    rows.append({"analysis": analysis, "held_out": "MEAN over folds",
                 "auroc_original": m0[0], "auroc_original_ci": f"[{m0[1]:.3f}, {m0[2]:.3f}]",
                 "auroc_centred": m1[0], "auroc_centred_ci": f"[{m1[1]:.3f}, {m1[2]:.3f}]",
                 "delta_auroc": md[0], "delta_ci_low": md[1], "delta_ci_high": md[2],
                 "pattern": pattern(md, m1)})
    for r in rows:
        print(f"{analysis:22s} {r['held_out']:16s} orig {r['auroc_original']:.3f}  centred {r['auroc_centred']:.3f}  "
              f"Δ {r['delta_auroc']:+.3f} [{r['delta_ci_low']:+.3f}, {r['delta_ci_high']:+.3f}]  {r.get('pattern', '')}")
    return rows


def pattern(delta, controlled):
    """D-027: A = CI of mean ΔAUROC includes 0; negative CI = its own outcome; C = positive Δ and the
    controlled mean AUROC CI includes 0.5; B = positive Δ, controlled AUROC stays above 0.5."""
    _, lo, hi = delta
    if lo <= 0 <= hi:
        return "A (no detectable change)"
    if hi < 0:
        return "significantly negative: control improved transfer"
    return "C (no better than chance after control)" if controlled[1] <= 0.5 else "B (drop, still above chance)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all", choices=["all", "primary", "no_adfsu", "subsample", "8s", "scaled"])
    ap.add_argument("--n-jobs", type=int, default=20)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))
    seed = cfg["seed"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "diagnosis")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    Z = z["Z_labram-base"]
    every = np.arange(len(meta))
    out_rows = []
    out_file = TABLES / "T09_primary_and_sensitivity.csv"
    if out_file.exists() and args.part != "all":
        out_rows = [r for r in pd.read_csv(out_file).to_dict("records")]

    def save_preds(preds, exp):
        d = ROOT / "results/runs" / exp
        d.mkdir(parents=True, exist_ok=True)
        preds.to_csv(d / "predictions.csv", index=False)

    def keep(rows_new, analysis):
        nonlocal out_rows
        out_rows = [r for r in out_rows if r["analysis"] != analysis] + rows_new

    # ---------------- EXP-040: primary outcome from the EXP-031 predictions
    if args.part in ("all", "primary"):
        pr = pd.read_csv(ROOT / "results/runs/EXP-031/predictions.csv")
        fp = {c: {h: (g["diagnosis"].to_numpy(), g["proba"].to_numpy()) for h, g in pr[pr.control == c].groupby("cohort", sort=False)}
              for c in CONTROLS}
        keep(summarise(fp, "primary (EXP-040)", seed), "primary (EXP-040)")

    # ---------------- EXP-041: without ADFSU (2 folds)
    if args.part in ("all", "no_adfsu"):
        rows = np.flatnonzero(meta["cohort"] != "ADFSU")
        fp, preds = run_loco(Z, meta, rows, seed, args.n_jobs, "no ADFSU")
        max_diff = max(np.abs(fp["none"][h][1] - fp["centring_i"][h][1]).max() for h in fp["none"])
        print(f"no ADFSU: largest |p_original - p_centred| = {max_diff:.2e} (0 expected, D-033)")
        r = summarise(fp, "without ADFSU (EXP-041)", seed)
        r[-1]["note"] = f"centring is a no-op with one training cohort; max |Δp| = {max_diff:.1e}"
        keep(r, "without ADFSU (EXP-041)")
        save_preds(preds, "EXP-041")

    # ---------------- EXP-042: ADFSU AD subsampled to the number of ADFSU HC, 100 draws
    if args.part in ("all", "subsample"):
        n_draws = cfg["sensitivity"]["adfsu_ad_subsample"]["n_draws"]
        ad = np.flatnonzero((meta["cohort"] == "ADFSU") & (meta["diagnosis"] == 1))
        n_hc = int(((meta["cohort"] == "ADFSU") & (meta["diagnosis"] == 0)).sum())
        draws = []
        for d in range(1, n_draws + 1):
            pick = np.random.default_rng(d).choice(ad, n_hc, replace=False)
            draws.append(np.sort(np.r_[np.setdiff1d(every, ad), pick]))
        jobs = []
        for d, rows in enumerate(draws, start=1):
            sub, folds = loco_jobs(meta, rows)
            y, cohort = sub["diagnosis"].to_numpy(), sub["cohort"].to_numpy()
            strata = (sub["cohort"] + "/" + sub["diagnosis"].astype(str)).to_numpy()
            for c in CONTROLS:
                for held, tr, te in folds:
                    jobs.append((d, c, held, rows, y, tr, te, strata, cohort))
        cands_all = labram_candidates(Z)
        res = Parallel(n_jobs=args.n_jobs)(
            delayed(classify)(OrderedDict((k, v[rows]) for k, v in cands_all.items()), y, tr, te, strata, seed,
                              make_control(c, cohort, y))
            for d, c, held, rows, y, tr, te, strata, cohort in jobs)
        auc = {}
        for (d, c, held, rows, y, tr, te, strata, cohort), p in zip(jobs, res):
            auc[(d, c, held)] = stats.metrics(y[te], p)["auroc"]
        drows = []
        for d in range(1, n_draws + 1):
            r = {"draw": d}
            for c in CONTROLS:
                for held in ("ADFSU", "APAVA", "ds004504"):
                    r[f"{c}_{held}"] = auc[(d, c, held)]
                r[f"{c}_mean"] = np.mean([auc[(d, c, h)] for h in ("ADFSU", "APAVA", "ds004504")])
            r["delta_mean"] = r["none_mean"] - r["centring_i_mean"]
            drows.append(r)
        dd = pd.DataFrame(drows)
        dd.round(4).to_csv(TABLES / "T09_adfsu_subsample_draws.csv", index=False)
        q = np.percentile(dd["delta_mean"], [2.5, 50, 97.5])
        keep([{"analysis": "ADFSU subsampled (EXP-042)", "held_out": f"MEAN over folds, {n_draws} draws",
               "auroc_original": dd["none_mean"].median(), "auroc_centred": dd["centring_i_mean"].median(),
               "delta_auroc": q[1], "delta_ci_low": q[0], "delta_ci_high": q[2],
               "note": f"median and 2.5-97.5 percentiles over draws (not a CI); share of draws with Δ < 0: "
                       f"{(dd['delta_mean'] < 0).mean():.2f}"}], "ADFSU subsampled (EXP-042)")
        print(f"subsample: median Δ {q[1]:+.3f}, 2.5-97.5 pct [{q[0]:+.3f}, {q[2]:+.3f}], "
              f"share Δ<0 {(dd['delta_mean'] < 0).mean():.2f}")

    # ---------------- EXP-043: 8-s equal-length representation
    if args.part in ("all", "8s"):
        rows = np.flatnonzero(z["has_8s"])
        fp, preds = run_loco(z["Z8_labram-base"], meta, rows, seed, args.n_jobs, "8 s")
        keep(summarise(fp, "8-s equal length (EXP-043)", seed), "8-s equal length (EXP-043)")
        save_preds(preds, "EXP-043")

    # ---------------- EXP-044: amplitude-scaled embeddings
    if args.part in ("all", "scaled"):
        s = np.load(ROOT / "data/features/participant_features_scaled.npz", allow_pickle=True)
        assert (s["global_id"] == meta["global_id"].to_numpy()).all(), "participant order differs"
        fp, preds = run_loco(s["Z_labram-base-scaled"], meta, every, seed, args.n_jobs, "amplitude-scaled")
        keep(summarise(fp, "amplitude-scaled (EXP-044)", seed), "amplitude-scaled (EXP-044)")
        save_preds(preds, "EXP-044")

    pd.DataFrame(out_rows).round(4).to_csv(out_file, index=False)
    print(f"\n-> {out_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
